from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json
import re
import sys
import time

import pandas as pd
import requests

# ✅ FIXED ROOT (no hard-coded path)
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"

EXCEL_FILE = DATA_DIR / "publications.xlsx"
BACKUP_FILE = DATA_DIR / "publications.backup.before_openalex.xlsx"
CACHE_FILE = DATA_DIR / "openalex_author_works_cache.json"

OPENALEX_AUTHOR_ID = "A5058462199"
OPENALEX_BASE_URL = "https://api.openalex.org/works"
POLITE_EMAIL: Optional[str] = None

REQUEST_TIMEOUT = 45
REQUEST_DELAY_SECONDS = 0.15
PER_PAGE = 200
TITLE_FUZZY_MATCH_THRESHOLD = 0.93
ONLY_UPDATE_ROWS_WITH_EMPTY_OPENALEX_ID = False


def log(message: str) -> None:
    print(message, flush=True)


def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def normalize_doi(value: object) -> Optional[str]:
    if value is None or pd.isna(value):
        return None
    doi = str(value).strip()
    if not doi or doi.lower() in {"nan", "none"}:
        return None
    doi = doi.replace("https://doi.org/", "").replace("http://doi.org/", "")
    doi = doi.replace("doi:", "").strip()
    return doi.lower()


def normalize_title(value: object) -> Optional[str]:
    if value is None or pd.isna(value):
        return None
    text = str(value).strip().lower()
    if not text:
        return None
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[“”\"'`’]", "", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def title_similarity(a: Optional[str], b: Optional[str]) -> float:
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    a_tokens = set(a.split())
    b_tokens = set(b.split())
    if not a_tokens or not b_tokens:
        return 0.0
    jaccard = len(a_tokens & b_tokens) / len(a_tokens | b_tokens)
    a_prefix = a[:120]
    b_prefix = b[:120]
    same_prefix = 1.0 if a_prefix == b_prefix else 0.0
    return max(jaccard, same_prefix)


def safe_get(d: dict, *keys, default=None):
    current = d
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key)
        if current is None:
            return default
    return current


@dataclass
class OpenAlexWork:
    openalex_id: Optional[str]
    openalex_url: Optional[str]
    doi: Optional[str]
    title: Optional[str]
    title_norm: Optional[str]
    publication_year: Optional[int]
    publication_date: Optional[str]
    cited_by_count: Optional[int]
    cited_by_api_url: Optional[str]
    type_: Optional[str]
    source_title: Optional[str]
    pdf_url: Optional[str]


def extract_work(raw: dict) -> OpenAlexWork:
    doi_url = safe_get(raw, "ids", "doi")
    doi = normalize_doi(doi_url or raw.get("doi"))

    title = raw.get("display_name") or raw.get("title")
    title_norm = normalize_title(title)

    primary_location = raw.get("primary_location") or {}
    source_title = safe_get(primary_location, "source", "display_name")
    pdf_url = primary_location.get("pdf_url")

    return OpenAlexWork(
        openalex_id=(raw.get("id") or "").split("/")[-1] if raw.get("id") else None,
        openalex_url=raw.get("id"),
        doi=doi,
        title=title,
        title_norm=title_norm,
        publication_year=raw.get("publication_year"),
        publication_date=raw.get("publication_date"),
        cited_by_count=raw.get("cited_by_count"),
        cited_by_api_url=raw.get("cited_by_api_url"),
        type_=raw.get("type"),
        source_title=source_title,
        pdf_url=pdf_url,
    )


def build_params(cursor: str = "*") -> dict:
    params = {
        "filter": f"authorships.author.id:https://openalex.org/{OPENALEX_AUTHOR_ID}",
        "per-page": PER_PAGE,
        "cursor": cursor,
        "select": ",".join([
            "id","doi","title","display_name","publication_year","publication_date",
            "cited_by_count","cited_by_api_url","type","primary_location","ids",
        ]),
    }
    if POLITE_EMAIL:
        params["mailto"] = POLITE_EMAIL
    return params


def fetch_all_openalex_works() -> List[OpenAlexWork]:
    works: List[OpenAlexWork] = []
    session = requests.Session()
    cursor = "*"
    page_num = 0

    while True:
        page_num += 1
        params = build_params(cursor=cursor)

        response = session.get(
            OPENALEX_BASE_URL,
            params=params,
            timeout=REQUEST_TIMEOUT,
            headers={"User-Agent": "ValentineOwanSiteSync/1.0"},
        )
        response.raise_for_status()

        payload = response.json()
        results = payload.get("results", [])
        meta = payload.get("meta", {})

        if not results:
            break

        works.extend([extract_work(item) for item in results])

        log(f"Fetched page {page_num}: {len(results)} works (total: {len(works)})")

        next_cursor = meta.get("next_cursor")
        if not next_cursor:
            break

        cursor = next_cursor
        time.sleep(REQUEST_DELAY_SECONDS)

    return works


def save_cache(works: List[OpenAlexWork]) -> None:
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(
        json.dumps([w.__dict__ for w in works], indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    log(f"Saved OpenAlex cache: {CACHE_FILE}")


def update_excel_with_openalex(works: List[OpenAlexWork]) -> None:
    if not EXCEL_FILE.exists():
        raise FileNotFoundError(f"Excel file not found: {EXCEL_FILE}")

    df = pd.read_excel(EXCEL_FILE)

    if not BACKUP_FILE.exists():
        df.to_excel(BACKUP_FILE, index=False)
        log(f"Created backup: {BACKUP_FILE}")

    doi_map = {w.doi: w for w in works if w.doi}

    for i, row in df.iterrows():
        doi = normalize_doi(row.get("doi"))
        if doi and doi in doi_map:
            work = doi_map[doi]
            df.at[i, "openalex_id"] = work.openalex_id
            df.at[i, "openalex_citations"] = work.cited_by_count
            df.at[i, "openalex_last_checked"] = now_str()

    df.to_excel(EXCEL_FILE, index=False)
    log(f"Updated Excel: {EXCEL_FILE}")


def main() -> None:
    try:
        log("Fetching OpenAlex data...")
        works = fetch_all_openalex_works()
        save_cache(works)

        log("Updating Excel...")
        update_excel_with_openalex(works)

    except Exception as e:
        log(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()