from pathlib import Path
from datetime import datetime
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "publications.xlsx"
OUTPUT_FILE = ROOT / "sitemap.xml"

SITE_URL = "https://www.valentineowan.com"


def clean_text(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def iso_date_from_value(value):
    """
    Convert a date-like value to YYYY-MM-DD.
    Falls back to today's date if conversion fails.
    """
    today = datetime.today().strftime("%Y-%m-%d")

    if pd.isna(value) or str(value).strip() == "":
        return today

    try:
        dt = pd.to_datetime(value, errors="coerce")
        if pd.isna(dt):
            return today
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return today


def add_url(urls, loc, lastmod=None, changefreq=None, priority=None):
    item = {"loc": loc}

    if lastmod:
        item["lastmod"] = lastmod
    if changefreq:
        item["changefreq"] = changefreq
    if priority is not None:
        item["priority"] = priority

    urls.append(item)


def main():
    urls = []
    today = datetime.today().strftime("%Y-%m-%d")

    # Core static pages
    static_pages = [
        ("", today, "weekly", "1.0"),
        ("index.html", today, "weekly", "1.0"),
        ("about.html", today, "monthly", "0.9"),
        ("publications.html", today, "weekly", "0.95"),
        ("south-south-rankings.html", today, "monthly", "0.9"),
        ("tro.html", today, "monthly", "0.8"),
        ("rps.html", today, "monthly", "0.8"),
        ("rii.html", today, "monthly", "0.8"),
        ("anps.html", today, "monthly", "0.8"),
        ("rmf.html", today, "monthly", "0.8"),
        ("ird.html", today, "monthly", "0.8"),
        ("anoi.html", today, "monthly", "0.8"),
        ("urpi.html", today, "monthly", "0.8"),
        ("bos.html", today, "monthly", "0.8"),
        ("moi.html", today, "monthly", "0.8"),
        ("bl-rii.html", today, "monthly", "0.8"),
        ("teaching.html", today, "monthly", "0.8"),
        ("cv.html", today, "monthly", "0.8"),
        ("updates.html", today, "weekly", "0.7"),
        ("contact.html", today, "yearly", "0.6"),
        ("quotes.html", today, "monthly", "0.5"),
    ]

    for page, lastmod, changefreq, priority in static_pages:
        if page == "":
            loc = f"{SITE_URL}/"
        else:
            loc = f"{SITE_URL}/{page}"
        add_url(urls, loc, lastmod, changefreq, priority)

    # Publication pages from Excel
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Excel file not found: {DATA_FILE}")

    df = pd.read_excel(DATA_FILE)
    df.columns = df.columns.str.strip().str.lower()
    df = df.fillna("")

    if "slug" not in df.columns:
        raise ValueError("The publications.xlsx file must contain a 'slug' column.")

    # Prefer OpenAlex last checked date, then publication date/year, then today
    for _, row in df.iterrows():
        slug = clean_text(row.get("slug", ""))
        if not slug:
            continue

        openalex_last_checked = row.get("openalex_last_checked", "")
        openalex_publication_date = row.get("openalex_publication_date", "")
        year = clean_text(row.get("year", ""))

        if clean_text(openalex_last_checked):
            lastmod = iso_date_from_value(openalex_last_checked)
        elif clean_text(openalex_publication_date):
            lastmod = iso_date_from_value(openalex_publication_date)
        elif year:
            lastmod = f"{year}-01-01"
        else:
            lastmod = today

        loc = f"{SITE_URL}/publications/{slug}.html"
        add_url(urls, loc, lastmod, "monthly", "0.8")

    # Remove duplicate URLs while preserving order
    seen = set()
    unique_urls = []
    for item in urls:
        if item["loc"] not in seen:
            unique_urls.append(item)
            seen.add(item["loc"])

    # Build XML
    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

    for item in unique_urls:
        lines.append("  <url>")
        lines.append(f"    <loc>{item['loc']}</loc>")
        if "lastmod" in item:
            lines.append(f"    <lastmod>{item['lastmod']}</lastmod>")
        if "changefreq" in item:
            lines.append(f"    <changefreq>{item['changefreq']}</changefreq>")
        if "priority" in item:
            lines.append(f"    <priority>{item['priority']}</priority>")
        lines.append("  </url>")

    lines.append("</urlset>")

    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"✅ Sitemap generated successfully: {OUTPUT_FILE}")
    print(f"Total URLs in sitemap: {len(unique_urls)}")


if __name__ == "__main__":
    main()