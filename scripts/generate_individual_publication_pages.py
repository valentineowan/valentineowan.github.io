#!/usr/bin/env python3
"""
Generate individual publication HTML pages from data/publications.xlsx.

Designed for the Valentine Joseph Owan academic website.

The Excel workbook is the source of truth. Every run reads the full workbook
and creates or refreshes the corresponding HTML page in publications/.
Existing page filenames stored in the `html_path` column are preserved.

Important:
- This script does NOT modify the Excel workbook.
- It does NOT delete old/orphaned HTML files.
- It preserves the site's existing CSS, header, footer and page styling.
- PDF links are generated only when `pdf_path` is supplied.
- Open-access records with a missing PDF are reported as warnings rather
  than being silently treated as request/closed access.

Usage from the project root or scripts directory:
    python scripts/generate_individual_publication_pages.py

Optional strict validation:
    python scripts/generate_individual_publication_pages.py --strict

Optional dry run:
    python scripts/generate_individual_publication_pages.py --dry-run
"""

from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path
from typing import Any

import pandas as pd


# -----------------------------------------------------------------------------
# Project paths
# -----------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
DATA_FILE = ROOT / "data" / "publications.xlsx"
OUTPUT_DIR = ROOT / "publications"
ASSETS_DIR = ROOT / "assets"

SITE_URL = "https://www.valentineowan.com"


# -----------------------------------------------------------------------------
# Small helpers
# -----------------------------------------------------------------------------
def clean(value: Any) -> str:
    """Return a clean string; pandas NaN/None become an empty string."""
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass
    return str(value).strip()


def esc(value: Any) -> str:
    """HTML-escape a value."""
    return html.escape(clean(value), quote=True)


def normalise_path(value: Any) -> str:
    """Normalise a repository-relative path to forward slashes."""
    return clean(value).replace("\\", "/").lstrip("/")


def relative_href_from_publication(pdf_path: str) -> str:
    """Build the relative href from /publications/*.html to the PDF."""
    return "../" + normalise_path(pdf_path)


def html_filename(row: pd.Series) -> str:
    """Return the authoritative HTML filename from html_path.

    Standard convention: html_path contains the repository-relative page path
    and must end in .html. The slug is used only as a fallback when html_path
    is empty. This function never appends a second .html extension.
    """
    existing = normalise_path(row.get("html_path", ""))
    if existing:
        filename = Path(existing).name
        if not filename.lower().endswith(".html"):
            filename += ".html"
        return filename

    slug = clean(row.get("slug", ""))
    if not slug:
        slug = make_slug(clean(row.get("title", "")), clean(row.get("year", "")))
    return slug if slug.lower().endswith(".html") else slug + ".html"


def make_slug(title: str, year: str = "") -> str:
    """Generate a conservative slug matching the site's existing style."""
    text = title.lower().strip()
    text = text.replace("&", " and ")
    text = re.sub(r"[’'`]+", "", text)
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    if year and not text.startswith(str(year) + "-"):
        text = f"{year}-{text}"
    return text[:180].rstrip("-")


def split_authors(authors: str) -> list[str]:
    """Split the workbook's semicolon-separated author string."""
    if not authors:
        return []
    return [a.strip() for a in authors.split(";") if a.strip()]


def author_citation_name(author: str) -> str:
    """Convert 'Owan, V. J.' to a citation_author value."""
    return author.strip()


def js_string(value: str) -> str:
    """Escape a string for a JavaScript single-line template literal."""
    return (
        clean(value)
        .replace("\\", "\\\\")
        .replace("`", "\\`")
        .replace("${", "\\${")
    )


def citation_author_meta(authors: str) -> str:
    lines = []
    for author in split_authors(authors):
        lines.append(f'   <meta name="citation_author" content="{esc(author_citation_name(author))}" />')
    return "\n".join(lines)


def safe_intish(value: Any) -> str:
    text = clean(value)
    if not text:
        return ""
    try:
        number = float(text)
        if number.is_integer():
            return str(int(number))
    except ValueError:
        pass
    return text


def normalise_display_entry_type(row: pd.Series) -> str:
    """Return the publication type label used on the existing site pages.

    The current workbook contains two legacy project records whose stored
    entry_type is `phdthesis`, while the existing HTML pages identify them as
    `bedproject` and `nceproject`. We preserve that established site labelling
    without changing the Excel workbook.
    """
    entry_type = clean(row.get("entry_type", "")).lower()
    booktitle = clean(row.get("booktitle", ""))

    if entry_type == "phdthesis" and booktitle.lower() == "b.ed. project":
        return "bedproject"
    if entry_type == "phdthesis" and booktitle.lower() == "cross river state college of education, akamkpa":
        return "nceproject"
    return entry_type


def entry_label(entry_type: str) -> str:
    labels = {
        "article": "article",
        "chapter": "book chapter",
        "proceedings": "conference proceeding",
        "conference": "conference proceeding",
        "project": "project",
        "bedproject": "B.Ed. project",
        "nceproject": "NCE project",
        "thesis": "thesis",
        "dissertation": "dissertation",
    }
    return labels.get(entry_type.lower(), entry_type or "publication")


def thesis_citation_label(entry_type: str) -> str:
    """Human-readable bracket label for APA/Vancouver fallbacks."""
    labels = {
        "bedproject": "B.Ed. project",
        "nceproject": "NCE project",
        "project": "project",
        "thesis": "thesis",
        "dissertation": "dissertation",
    }
    return labels.get(entry_type.lower(), "publication")


def _legacy_build_detail_rows(row: pd.Series) -> list[str]:
    """Build publication-detail paragraphs using the fields available in Excel."""
    entry_type = normalise_display_entry_type(row)
    rows: list[str] = []

    journal = clean(row.get("journal", ""))
    source_title = clean(row.get("source_title", ""))
    booktitle = clean(row.get("booktitle", ""))
    publisher = clean(row.get("publisher", ""))
    school = clean(row.get("school", ""))
    year = safe_intish(row.get("year", ""))
    volume = safe_intish(row.get("volume", ""))
    issue = safe_intish(row.get("issue", ""))
    pages = clean(row.get("pages", ""))
    doi = clean(row.get("doi", ""))

    # Match the terminology used by the existing pages.
    if entry_type in {"article"}:
        if journal:
            rows.append(f"<p><strong>Journal:</strong> {esc(journal)}</p>")
        elif source_title:
            rows.append(f"<p><strong>Journal:</strong> {esc(source_title)}</p>")
        if year:
            rows.append(f"<p><strong>Year:</strong> {esc(year)}</p>")
        if volume:
            rows.append(f"<p><strong>Volume:</strong> {esc(volume)}</p>")
        if issue:
            rows.append(f"<p><strong>Issue:</strong> {esc(issue)}</p>")
        if pages:
            rows.append(f"<p><strong>Pages / article number:</strong> {esc(pages)}</p>")
    elif entry_type in {"chapter", "proceedings", "conference", "project", "bedproject", "nceproject", "thesis", "dissertation"}:
        title = booktitle or source_title or journal
        if title:
            rows.append(f"<p><strong>Book title:</strong> {esc(title)}</p>")
        if publisher:
            rows.append(f"<p><strong>Publisher:</strong> {esc(publisher)}</p>")
        if school:
            rows.append(f"<p><strong>Institution:</strong> {esc(school)}</p>")
        if year:
            rows.append(f"<p><strong>Year:</strong> {esc(year)}</p>")
        if volume:
            rows.append(f"<p><strong>Volume:</strong> {esc(volume)}</p>")
        if issue:
            rows.append(f"<p><strong>Issue:</strong> {esc(issue)}</p>")
        if pages:
            rows.append(f"<p><strong>Pages / article number:</strong> {esc(pages)}</p>")
    else:
        if journal:
            rows.append(f"<p><strong>Journal:</strong> {esc(journal)}</p>")
        elif source_title:
            rows.append(f"<p><strong>Source:</strong> {esc(source_title)}</p>")
        if booktitle:
            rows.append(f"<p><strong>Book title:</strong> {esc(booktitle)}</p>")
        if publisher:
            rows.append(f"<p><strong>Publisher:</strong> {esc(publisher)}</p>")
        if school:
            rows.append(f"<p><strong>Institution:</strong> {esc(school)}</p>")
        if year:
            rows.append(f"<p><strong>Year:</strong> {esc(year)}</p>")
        if volume:
            rows.append(f"<p><strong>Volume:</strong> {esc(volume)}</p>")
        if issue:
            rows.append(f"<p><strong>Issue:</strong> {esc(issue)}</p>")
        if pages:
            rows.append(f"<p><strong>Pages / article number:</strong> {esc(pages)}</p>")

    if entry_type:
        rows.append(f"<p><strong>Type:</strong> {esc(entry_type)}</p>")

    if doi:
        doi_url = doi if doi.startswith("http") else f"https://doi.org/{doi}"
        rows.append(
            f'<p><strong>DOI:</strong> <a href="{esc(doi_url)}" target="_blank" rel="noopener">{esc(doi)}</a></p>'
        )

    return rows


def _legacy_build_actions(row: pd.Series) -> str:
    pdf_path = normalise_path(row.get("pdf_path", ""))
    access = clean(row.get("access", "")).lower()
    doi = clean(row.get("doi", ""))

    actions: list[str] = []
    if access == "open" and pdf_path:
        pdf_href = relative_href_from_publication(pdf_path)
        actions.append(
            f'<a class="btn" href="{esc(pdf_href)}" target="_blank" rel="noopener">Read PDF</a>'
        )

    if doi:
        doi_url = doi if doi.startswith("http") else f"https://doi.org/{doi}"
        actions.append(
            f'<a class="btn btn-ghost" href="{esc(doi_url)}" target="_blank" rel="noopener">View DOI</a>'
        )

    actions.append('<a class="btn btn-ghost" href="../publications.html">Back to publications</a>')
    return "\n".join(actions)


def build_citation_block(row: pd.Series) -> tuple[str, str]:
    """Return citation JS object entries and the initial APA citation."""
    citations = {
        "apa": clean(row.get("apa_citation", "")),
        "mla": clean(row.get("mla_citation", "")),
        "harvard": clean(row.get("harvard_citation", "")),
        "vancouver": clean(row.get("vancouver_citation", "")),
        "bibtex": clean(row.get("bibtex", "")),
    }

    # Fallbacks are used only when a stored citation is absent.
    title = clean(row.get("title", ""))
    authors = split_authors(clean(row.get("authors", "")))
    year = safe_intish(row.get("year", ""))
    entry_type = normalise_display_entry_type(row)
    journal = clean(row.get("journal", "")) or clean(row.get("source_title", ""))
    booktitle = clean(row.get("booktitle", ""))
    publisher = clean(row.get("publisher", ""))
    school = clean(row.get("school", ""))
    volume = safe_intish(row.get("volume", ""))
    issue = safe_intish(row.get("issue", ""))
    pages = clean(row.get("pages", ""))
    doi = clean(row.get("doi", ""))
    doi_url = doi if doi.startswith("http") else (f"https://doi.org/{doi}" if doi else "")

    author_display = "; ".join(authors) if authors else ""
    citation_authors = author_display

    if not citations["apa"]:
        if entry_type in {"bedproject", "nceproject", "project", "thesis", "dissertation"}:
            apa = f"{citation_authors} ({year}). <em>{title}</em> [{thesis_citation_label(entry_type)}]"
            if school:
                apa += f". {school}"
            if doi_url:
                apa += f". {doi_url}"
        else:
            apa = f"{citation_authors} ({year}). {title}."
            if journal:
                apa += f" <em>{journal}</em>"
            if volume:
                apa += f", {volume}"
                if issue:
                    apa += f"({issue})"
            if pages:
                apa += f", {pages}"
            if doi_url:
                apa += f". {doi_url}"
        citations["apa"] = apa

    if not citations["mla"]:
        mla = f"{citation_authors}. \"{title}.\""
        if journal:
            mla += f" {journal},"
        elif booktitle:
            mla += f" {booktitle},"
        if volume:
            mla += f" vol. {volume},"
        if issue:
            mla += f" no. {issue},"
        if year:
            mla += f" {year},"
        if pages:
            mla += f" pp. {pages}."
        if doi_url:
            mla += f" {doi_url}."
        citations["mla"] = mla

    if not citations["harvard"]:
        harvard = f"{citation_authors}, {year}. <em>{title}</em>."
        if journal:
            harvard += f" {journal}"
            if volume:
                harvard += f", {volume}"
                if issue:
                    harvard += f"({issue})"
            if pages:
                harvard += f", pp.{pages}"
        elif school:
            harvard += f" {thesis_citation_label(entry_type)}, {school}."
        if doi_url:
            harvard += f" Available at: {doi_url}"
        citations["harvard"] = harvard

    if not citations["vancouver"]:
        # Compact fallback; stored Excel citations are preferred whenever present.
        surname_initials = []
        for a in authors:
            parts = [p.strip() for p in a.split(",", 1)]
            surname_initials.append(parts[0] if parts else a)
        van = ", ".join(surname_initials) + ". " if surname_initials else ""
        van += title + "."
        if journal:
            van += f" {journal}."
            if year:
                van += f" {year}"
            if volume:
                van += f";{volume}"
                if issue:
                    van += f"({issue})"
            if pages:
                van += f":{pages}"
        if doi:
            van += f" doi:{doi}"
        citations["vancouver"] = van

    if not citations["bibtex"]:
        key = clean(row.get("mendeley_key", "")) or f"Owan{year}"
        bib_type = "article"
        if entry_type in {"chapter"}:
            bib_type = "incollection"
        elif entry_type in {"proceedings", "conference"}:
            bib_type = "inproceedings"
        elif entry_type in {"bedproject", "nceproject", "project", "thesis", "dissertation"}:
            bib_type = "misc"
        author_bib = " and ".join(a.replace(", ", ", ") for a in authors)
        lines = [f"@{bib_type}{{{key},", f"  author = {{{author_bib}}},", f"  title = {{{title}}},"]
        if journal:
            lines.append(f"  journal = {{{journal}}},")
        if booktitle:
            lines.append(f"  booktitle = {{{booktitle}}},")
        if publisher:
            lines.append(f"  publisher = {{{publisher}}},")
        if school:
            lines.append(f"  school = {{{school}}},")
        if year:
            lines.append(f"  year = {{{year}}},")
        if volume:
            lines.append(f"  volume = {{{volume}}},")
        if issue:
            lines.append(f"  number = {{{issue}}},")
        if pages:
            lines.append(f"  pages = {{{pages}}},")
        if doi:
            lines.append(f"  doi = {{{doi}}},")
        abstract = clean(row.get("abstract", ""))
        if abstract:
            lines.append(f"  abstract = {{{abstract}}},")
        keywords = clean(row.get("keywords", ""))
        if keywords:
            lines.append(f"  keywords = {{{keywords}}}")
        else:
            if lines[-1].endswith(","):
                lines[-1] = lines[-1][:-1]
        lines.append("}")
        citations["bibtex"] = "\n".join(lines)

    def make_js(value: str) -> str:
        return "`" + js_string(value) + "`"

    js_entries = ",\n".join(
        f"      {key}: {make_js(value)}" for key, value in citations.items()
    )
    return js_entries, citations["apa"]


def build_metrics(row: pd.Series) -> str:
    citations = clean(row.get("openalex_citations", ""))
    openalex_id = clean(row.get("openalex_id", ""))
    checked = clean(row.get("openalex_last_checked", ""))
    if not citations and not openalex_id:
        return ""

    citation_text = esc(citations) if citations else "0"
    record_link = ""
    if openalex_id:
        record_link = f' <a href="https://openalex.org/{esc(openalex_id)}" target="_blank" rel="noopener">(view record)</a>'

    checked_line = ""
    if checked:
        checked_line = f'<p><small>Last checked: {esc(checked)}</small></p>'

    return f'''        <section class="card article-block">
          <h2>Citation metrics</h2>
          <p><strong>Citations:</strong> {citation_text}{record_link}</p>
          <p><small>Source: OpenAlex</small></p>
          {checked_line}
        </section>'''


def build_optional_section(heading: str, content: str) -> str:
    if not clean(content):
        return ""
    return f'''        <section class="card article-block">
          <h2>{esc(heading)}</h2>
          <p>{content}</p>
        </section>'''


def build_page(row: pd.Series) -> str:
    title = clean(row.get("title", "Untitled publication"))
    authors = clean(row.get("authors", ""))
    year = safe_intish(row.get("year", ""))
    doi = clean(row.get("doi", ""))
    doi_url = doi if doi.startswith("http") else (f"https://doi.org/{doi}" if doi else "")
    pdf_path = normalise_path(row.get("pdf_path", ""))
    abstract = clean(row.get("abstract", ""))
    keywords = clean(row.get("keywords", ""))
    entry_type = normalise_display_entry_type(row)
    filename = html_filename(row)
    canonical = f"{SITE_URL}/publications/{filename}"

    citation_pdf_meta = ""
    if pdf_path:
        citation_pdf_meta = f'   <meta name="citation_pdf_url" content="{esc(relative_href_from_publication(pdf_path))}" />\n'

    doi_meta = ""
    if doi:
        doi_meta = f'   <meta name="citation_doi" content="{esc(doi)}" />\n'

    actions = _legacy_build_actions(row)
    details = "\n".join(_legacy_build_detail_rows(row))
    metrics = build_metrics(row)
    citation_entries, _ = build_citation_block(row)

    abstract_section = ""
    if abstract:
        abstract_section = f'''        <section class="card article-block">
          <h2>Abstract</h2>
          <p>{esc(abstract)}</p>
        </section>'''

    keywords_section = ""
    if keywords:
        keywords_section = f'''        <section class="card article-block">
          <h2>Keywords</h2>
          <p>{esc(keywords)}</p>
        </section>'''

    # Keep the site's established CSS and page structure intact.
    return f'''<!doctype html>
<html lang="en-GB">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{esc(title)} | Valentine Joseph Owan</title>
  <meta name="description" content="{esc(title)}" />
  <meta name="citation_title" content="{esc(title)}" />
{citation_author_meta(authors)}
  <meta name="citation_publication_date" content="{esc(year)}" />
{('  <meta name="citation_journal_title" content="' + esc(clean(row.get("journal", "")) or clean(row.get("source_title", ""))) + '" />\n') if (clean(row.get("journal", "")) or clean(row.get("source_title", ""))) else ''}{doi_meta}{citation_pdf_meta}  <link rel="canonical" href="{esc(canonical)}" />
  <link rel="stylesheet" href="../assets/css/style.css" />
  <style>
    .article-wrap {{
      display:grid;
      gap:16px;
    }}
    .article-top h1 {{
      margin-bottom:10px;
    }}
    .article-authors {{
      color:var(--muted);
      font-size:1rem;
    }}
    .article-actions {{
      display:flex;
      flex-wrap:wrap;
      gap:10px;
      margin-top:14px;
    }}
    .article-meta p {{
      margin:0 0 8px;
      color:var(--muted);
    }}
    .article-block h2 {{
      margin-top:0;
    }}
    .citation-tabs {{
      display:flex;
      flex-wrap:wrap;
      gap:8px;
      margin:10px 0 12px;
    }}
    .citation-tabs button {{
      padding:8px 12px;
      border-radius:10px;
      border:1px solid var(--line);
      background:var(--panel);
      cursor:pointer;
      color:var(--text);
    }}
    .citation-tabs button:hover {{
      background:rgba(17,24,39,.05);
    }}
    .citation-box {{
      white-space:pre-wrap;
      overflow-wrap:anywhere;
      color:var(--text);
    }}
    .crumbs {{
      font-size:14px;
      color:var(--muted);
      margin-bottom:12px;
    }}
    .crumbs a {{
      text-decoration:none;
    }}
  </style>
</head>
<body>
  <a class="skip-link" href="#main">Skip to content</a>

  <header class="site-header">
    <div class="container header-inner">
      <div class="brand">
        <a href="../index.html" class="brand-name">Valentine Joseph Owan</a>
        <div class="brand-tag">Researcher | Psychometrician | Statistician</div>
      </div>

      <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav">
        Menu
      </button>

      <nav id="site-nav" class="site-nav" aria-label="Primary">
        <a class="nav-link" href="../index.html">Home</a>
        <a class="nav-link" href="../about.html">About</a>
        <a class="nav-link active" href="../publications.html">Publications</a>
        <a class="nav-link" href="../teaching.html">Teaching</a>
        <a class="nav-link" href="../cv.html">CV</a>
        <a class="nav-link" href="../updates.html">Updates</a>
        <a class="nav-link" href="../contact.html">Contact</a>
        <a class="nav-link" href="../quotes.html">Quotes</a>
      </nav>
    </div>
  </header>

  <main id="main" class="section">
    <div class="container narrow">
      <div class="crumbs">
        <a href="../index.html">Home</a> / <a href="../publications.html">Publications</a> / Record
      </div>

      <div class="article-wrap">
        <section class="card article-top">
          <p class="kicker">Publication record</p>
          <h1>{esc(title)}</h1>
          <p class="article-authors">{esc(authors)}</p>
          <div class="article-actions">
            {actions}
          </div>
        </section>

        <section class="card article-meta">
          <h2>Publication details</h2>
          {details}
        </section>

        {metrics}

        {abstract_section}

        {keywords_section}

        <section class="card article-block">
          <h2>Citation</h2>

          <div class="citation-tabs">
            <button onclick="showCitation('apa')">APA</button>
            <button onclick="showCitation('mla')">MLA</button>
            <button onclick="showCitation('harvard')">Harvard</button>
            <button onclick="showCitation('vancouver')">Vancouver</button>
            <button onclick="showCitation('bibtex')">BibTeX</button>
          </div>

          <div id="citationText" class="citation-box"></div>

          <div class="card-actions">
            <button class="btn btn-ghost" onclick="copyCitation()">Copy citation</button>
          </div>
        </section>
      </div>
    </div>
  </main>

  <footer class="site-footer">
    <div class="container">
      <div class="footer-top">
        <div class="footer-copy">
          © <span id="year"></span> Valentine Joseph Owan
          <span class="footer-sep">•</span>
          University of Calabar
        </div>

        <nav class="footer-links" aria-label="Footer">
          <a href="../index.html">Home</a>
          <a href="../about.html">About</a>
          <a href="../publications.html">Publications</a>
          <a href="../teaching.html">Teaching</a>
          <a href="../cv.html">CV</a>
          <a href="../updates.html">Updates</a>
          <a href="../quotes.html">Quotes</a>
          <a href="../contact.html">Contact</a>
        </nav>
      </div>

      <div class="footer-note">
        Academic website for research, teaching, and scholarly work.
      </div>
    </div>
  </footer>

  <script src="../assets/js/main.js"></script>
  <script>
    const citations = {{
{citation_entries}
    }};

    function showCitation(type) {{
      const box = document.getElementById("citationText");
      if (!box) return;
      box.innerHTML = citations[type] || "";
    }}

    function copyCitation() {{
      const box = document.getElementById("citationText");
      if (!box) return;
      const text = box.innerText;
      navigator.clipboard.writeText(text).then(() => {{
        alert("Citation copied");
      }});
    }}

    (function () {{
      var y = document.getElementById("year");
      if (y) y.textContent = new Date().getFullYear();
      showCitation("apa");
    }})();
  </script>
</body>
</html>
'''


def validate_rows(df: pd.DataFrame) -> tuple[list[str], list[str], dict[str, int]]:
    errors: list[str] = []
    warnings: list[str] = []
    stats = {
        "records": len(df),
        "open": 0,
        "open_with_pdf": 0,
        "open_missing_pdf": 0,
        "request": 0,
        "pdf_missing_on_disk": 0,
        "duplicate_slugs": 0,
        "duplicate_html": 0,
    }

    required = ["title", "year", "entry_type", "access"]
    missing_columns = [c for c in required if c not in df.columns]
    if missing_columns:
        errors.append("Missing required Excel columns: " + ", ".join(missing_columns))
        return errors, warnings, stats

    slug_values = [clean(v) for v in df.get("slug", pd.Series(dtype=object))]
    html_values = [normalise_path(v) for v in df.get("html_path", pd.Series(dtype=object))]

    slug_dupes = pd.Series([s for s in slug_values if s]).duplicated(keep=False)
    stats["duplicate_slugs"] = int(slug_dupes.sum())
    if stats["duplicate_slugs"]:
        dupes = sorted({s for s in slug_values if s and slug_values.count(s) > 1})
        errors.append("Duplicate slugs: " + ", ".join(dupes[:20]))

    html_dupes = pd.Series([h for h in html_values if h]).duplicated(keep=False)
    stats["duplicate_html"] = int(html_dupes.sum())
    if stats["duplicate_html"]:
        dupes = sorted({h for h in html_values if h and html_values.count(h) > 1})
        errors.append("Duplicate html_path values: " + ", ".join(dupes[:20]))

    for idx, row in df.iterrows():
        title = clean(row.get("title", ""))
        year = clean(row.get("year", ""))
        entry_type = clean(row.get("entry_type", ""))
        access = clean(row.get("access", "")).lower()
        pdf_path = normalise_path(row.get("pdf_path", ""))

        if not title:
            errors.append(f"Row {idx + 2}: missing title")
        if not year:
            errors.append(f"Row {idx + 2}: missing year ({title[:70]})")
        if not entry_type:
            errors.append(f"Row {idx + 2}: missing entry_type ({title[:70]})")

        if access == "open":
            stats["open"] += 1
            if pdf_path:
                stats["open_with_pdf"] += 1
                pdf_abs = ROOT / pdf_path
                if not pdf_abs.is_file():
                    stats["pdf_missing_on_disk"] += 1
                    warnings.append(
                        f"Open Access PDF not found on disk: {pdf_path} | {title}"
                    )
            else:
                stats["open_missing_pdf"] += 1
                warnings.append(f"Open Access record has no pdf_path: {title}")
        elif access == "request":
            stats["request"] += 1
            if pdf_path:
                warnings.append(f"Request record has a PDF path: {title} | {pdf_path}")
        elif access:
            warnings.append(f"Unrecognised access value '{access}': {title}")

    return errors, warnings, stats


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate individual publication pages from publications.xlsx")
    parser.add_argument("--strict", action="store_true", help="Treat missing physical PDFs for supplied paths as errors")
    parser.add_argument("--dry-run", action="store_true", help="Validate and report without writing HTML files")
    args = parser.parse_args()

    if not DATA_FILE.exists():
        print(f"ERROR: Excel file not found: {DATA_FILE}")
        return 1

    try:
        df = pd.read_excel(DATA_FILE)
    except Exception as exc:
        print(f"ERROR: Could not read Excel workbook: {exc}")
        return 1

    errors, warnings, stats = validate_rows(df)

    if args.strict:
        strict_warnings = [w for w in warnings if "PDF not found on disk" in w]
        errors.extend(strict_warnings)
        warnings = [w for w in warnings if w not in strict_warnings]

    print("=" * 64)
    print("VALENTINE OWAN — INDIVIDUAL PUBLICATION PAGE GENERATOR")
    print("=" * 64)
    print(f"Excel:       {DATA_FILE}")
    print(f"Output:      {OUTPUT_DIR}")
    print(f"Records:     {stats['records']}")
    print(f"Open Access: {stats['open']}")
    print(f"  with PDF:  {stats['open_with_pdf']}")
    print(f"  no PDF:    {stats['open_missing_pdf']}")
    print(f"Request:     {stats['request']}")
    print(f"Paid:        {stats.get('paid', 0)}")
    print(f"Book records:{stats.get('books', 0)}")
    print(f"PDF missing: {stats['pdf_missing_on_disk']}")
    print(f"Slug dupes:  {stats['duplicate_slugs']}")
    print(f"HTML dupes:  {stats['duplicate_html']}")
    print()

    if errors:
        print("ERRORS")
        for item in errors:
            print(f"  ✗ {item}")
        print()
        print("Generation stopped. Fix the errors and run again.")
        return 1

    if warnings:
        print("WARNINGS")
        for item in warnings[:100]:
            print(f"  ! {item}")
        if len(warnings) > 100:
            print(f"  ... and {len(warnings) - 100} more warning(s)")
        print()

    if args.dry_run:
        print("Dry run complete. No HTML files were changed.")
        return 0

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    created = 0
    updated = 0
    unchanged = 0
    generated_paths: set[Path] = set()

    for _, row in df.iterrows():
        filename = html_filename(row)
        out_file = OUTPUT_DIR / filename
        generated_paths.add(out_file.resolve())
        page = build_page(row)

        if out_file.exists():
            try:
                old = out_file.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                old = out_file.read_text(encoding="utf-8-sig")
            if old == page:
                unchanged += 1
            else:
                out_file.write_text(page, encoding="utf-8")
                updated += 1
        else:
            out_file.write_text(page, encoding="utf-8")
            created += 1

    # Do not delete files not represented in Excel. Report them instead.
    orphaned = []
    for existing in OUTPUT_DIR.glob("*.html"):
        if existing.resolve() not in generated_paths:
            orphaned.append(existing.name)

    print("RESULT")
    print(f"  ✓ Created:   {created}")
    print(f"  ✓ Updated:   {updated}")
    print(f"  ✓ Unchanged: {unchanged}")
    print(f"  ! Orphaned:  {len(orphaned)} (not deleted)")

    if orphaned:
        print("\nOrphaned HTML files (not in Excel; left untouched):")
        for name in sorted(orphaned)[:100]:
            print(f"  - {name}")
        if len(orphaned) > 100:
            print(f"  ... and {len(orphaned) - 100} more")

    print("\nGeneration completed successfully.")
    return 0



_legacy_build_page = build_page
_legacy_validate_rows = validate_rows


def publication_type(row: pd.Series) -> str:
    return clean(row.get("publication_type", "")).lower()


def is_book_material(row: pd.Series) -> bool:
    return publication_type(row) in {"monograph", "textbook", "book"}


def book_status(row: pd.Series) -> str:
    return clean(row.get("publication_status", "")).lower() or "published"


def pdf_role(row: pd.Series) -> str:
    return clean(row.get("pdf_role", "")).lower()


def asset_href(asset_path: str) -> str:
    return "../" + normalise_path(asset_path)


def book_label(kind: str) -> str:
    return {"monograph": "Monograph", "textbook": "Textbook", "book": "Book"}.get(kind, "Book")


def build_detail_rows(row: pd.Series) -> list[str]:
    if not is_book_material(row):
        return _legacy_build_detail_rows(row)
    kind = publication_type(row)
    rows = []
    publisher = clean(row.get("publisher", "")); year = safe_intish(row.get("year", ""))
    isbn = clean(row.get("isbn", "")); edition = clean(row.get("edition", "")); pages = clean(row.get("pages", ""))
    status = book_status(row); access = clean(row.get("access", "")).lower()
    price = clean(row.get("price", "")); currency = clean(row.get("currency", "")); doi = clean(row.get("doi", ""))
    if publisher: rows.append(f"<p><strong>Publisher:</strong> {esc(publisher)}</p>")
    if year: rows.append(f"<p><strong>Year:</strong> {esc(year)}</p>")
    if isbn: rows.append(f"<p><strong>ISBN:</strong> {esc(isbn)}</p>")
    if edition: rows.append(f"<p><strong>Edition:</strong> {esc(edition)}</p>")
    if pages: rows.append(f"<p><strong>Pages:</strong> {esc(pages)}</p>")
    rows.append(f"<p><strong>Type:</strong> {esc(book_label(kind))}</p>")
    rows.append(f"<p><strong>Status:</strong> {esc(status.title())}</p>")
    if access:
        label = {"open":"Open Access","request":"Available upon request","paid":"Paid"}.get(access, access.title())
        rows.append(f"<p><strong>Access:</strong> {esc(label)}</p>")
    if price: rows.append(f"<p><strong>Price:</strong> {esc((currency + ' ') if currency else '')}{esc(price)}</p>")
    if doi:
        doi_url = doi if doi.startswith("http") else f"https://doi.org/{doi}"
        rows.append(f'<p><strong>DOI:</strong> <a href="{esc(doi_url)}" target="_blank" rel="noopener">{esc(doi)}</a></p>')
    return rows


def build_actions(row: pd.Series) -> str:
    pdf_path = normalise_path(row.get("pdf_path", "")); access = clean(row.get("access", "")).lower(); role = pdf_role(row); doi = clean(row.get("doi", ""))
    actions = []
    if is_book_material(row):
        if pdf_path and role == "full_text" and access == "open":
            actions.append(f'<a class="btn" href="{esc(asset_href(pdf_path))}" target="_blank" rel="noopener">Read full book</a>')
        elif pdf_path and role == "preview":
            actions.append(f'<a class="btn btn-ghost" href="{esc(asset_href(pdf_path))}" target="_blank" rel="noopener">View book information</a>')
        purchase_url = clean(row.get("purchase_url", "")); request_url = clean(row.get("request_url", ""))
        if access == "paid" and purchase_url:
            actions.append(f'<a class="btn" href="{esc(purchase_url)}" target="_blank" rel="noopener">Purchase / Order</a>')
        elif access == "request":
            href = request_url or "../contact.html"; target = ' target="_blank" rel="noopener"' if request_url.startswith("http") else ""
            actions.append(f'<a class="btn btn-ghost" href="{esc(href)}"{target}>Request a copy</a>')
        elif access == "paid":
            href = request_url or "../contact.html"; target = ' target="_blank" rel="noopener"' if request_url.startswith("http") else ""
            actions.append(f'<a class="btn btn-ghost" href="{esc(href)}"{target}>Enquire / Order</a>')
    elif access == "open" and pdf_path:
        actions.append(f'<a class="btn" href="{esc(asset_href(pdf_path))}" target="_blank" rel="noopener">Read PDF</a>')
    if doi:
        doi_url = doi if doi.startswith("http") else f"https://doi.org/{doi}"
        actions.append(f'<a class="btn btn-ghost" href="{esc(doi_url)}" target="_blank" rel="noopener">View DOI</a>')
    actions.append('<a class="btn btn-ghost" href="../books.html">Back to books</a>' if is_book_material(row) else '<a class="btn btn-ghost" href="../publications.html">Back to publications</a>')
    return "\n".join(actions)


def build_book_page(row: pd.Series) -> str:
    title = clean(row.get("title", "Untitled book")); authors = clean(row.get("authors", "")); year = safe_intish(row.get("year", ""))
    filename = html_filename(row); canonical = f"{SITE_URL}/publications/{filename}"; kind = publication_type(row); status = book_status(row)
    description = clean(row.get("book_description", "")) or clean(row.get("abstract", "")); cover_path = normalise_path(row.get("cover_path", ""))
    cover = f'<img class="book-cover" src="{esc(asset_href(cover_path))}" alt="Cover of {esc(title)}" />' if cover_path else '<div class="book-cover book-cover-placeholder">Cover image</div>'
    actions = build_actions(row); details = "\n".join(build_detail_rows(row)); citation_entries, _ = build_citation_block(row)
    preview_note = '<p class="book-note"><strong>Note:</strong> This PDF is a book information/preview document. It does not contain the full textbook.</p>' if pdf_role(row) == "preview" else ""
    description_section = f'<section class="card article-block"><h2>About the book</h2><div class="book-description"><p>{esc(description)}</p></div></section>' if description else ""
    return f'''<!doctype html>
<html lang="en-GB"><head>
<meta charset="utf-8" /><meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{esc(title)} | Valentine Joseph Owan</title><meta name="description" content="{esc(description or title)}" />
<meta name="citation_title" content="{esc(title)}" />
{citation_author_meta(authors)}
<meta name="citation_publication_date" content="{esc(year)}" />
<link rel="canonical" href="{esc(canonical)}" /><link rel="stylesheet" href="../assets/css/style.css" />
<style>
.book-page-wrap{{display:grid;gap:16px}} .book-hero{{display:grid;grid-template-columns:minmax(180px,260px) 1fr;gap:24px;align-items:start}} .book-cover{{width:100%;max-width:260px;aspect-ratio:2/3;object-fit:cover;border-radius:12px;border:1px solid var(--line);box-shadow:0 8px 24px rgba(17,24,39,.10);background:var(--panel)}} .book-cover-placeholder{{display:grid;place-items:center;color:var(--muted);font-size:.95rem;padding:20px;text-align:center}} .book-type{{font-size:.82rem;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);margin:0 0 8px}} .book-actions{{display:flex;flex-wrap:wrap;gap:10px;margin-top:16px}} .book-meta p{{margin:0 0 8px;color:var(--muted)}} .book-note{{margin-top:14px;padding:12px;border-left:3px solid var(--line);background:var(--panel);border-radius:8px}} .book-description{{line-height:1.75}} .crumbs{{font-size:14px;color:var(--muted);margin-bottom:12px}} .crumbs a{{text-decoration:none}} .citation-tabs{{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0 12px}} .citation-tabs button{{padding:8px 12px;border-radius:10px;border:1px solid var(--line);background:var(--panel);cursor:pointer;color:var(--text)}} .citation-box{{white-space:pre-wrap;overflow-wrap:anywhere;color:var(--text)}} @media(max-width:700px){{.book-hero{{grid-template-columns:1fr}}.book-cover{{max-width:220px}}}}
</style></head>
<body><a class="skip-link" href="#main">Skip to content</a>
<header class="site-header"><div class="container header-inner"><div class="brand"><a href="../index.html" class="brand-name">Valentine Joseph Owan</a><div class="brand-tag">Researcher | Psychometrician | Statistician</div></div><button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav">Menu</button><nav id="site-nav" class="site-nav" aria-label="Primary"><a class="nav-link" href="../index.html">Home</a><a class="nav-link" href="../about.html">About</a><a class="nav-link" href="../publications.html">Publications</a><a class="nav-link active" href="../books.html">Books</a><a class="nav-link" href="../teaching.html">Teaching</a><a class="nav-link" href="../cv.html">CV</a><a class="nav-link" href="../updates.html">Updates</a><a class="nav-link" href="../contact.html">Contact</a><a class="nav-link" href="../quotes.html">Quotes</a></nav></div></header>
<main id="main" class="section"><div class="container narrow"><div class="crumbs"><a href="../index.html">Home</a> / <a href="../books.html">Books</a> / {esc(status.title())}</div><div class="book-page-wrap"><section class="card book-hero"><div>{cover}</div><div><p class="book-type">{esc(book_label(kind))}</p><h1>{esc(title)}</h1><p class="article-authors">{esc(authors)}</p><span class="tag">{esc(status.title())}</span><div class="book-actions">{actions}</div>{preview_note}</div></section><section class="card book-meta"><h2>Book details</h2>{details}</section>{description_section}<section class="card article-block"><h2>Citation</h2><div class="citation-tabs"><button onclick="showCitation('apa')">APA</button><button onclick="showCitation('mla')">MLA</button><button onclick="showCitation('harvard')">Harvard</button><button onclick="showCitation('vancouver')">Vancouver</button><button onclick="showCitation('bibtex')">BibTeX</button></div><div id="citationText" class="citation-box"></div><div class="card-actions"><button class="btn btn-ghost" onclick="copyCitation()">Copy citation</button></div></section></div></div></main>
<footer class="site-footer"><div class="container"><div class="footer-top"><div class="footer-copy">© <span id="year"></span> Valentine Joseph Owan <span class="footer-sep">•</span> University of Calabar</div><nav class="footer-links" aria-label="Footer"><a href="../index.html">Home</a><a href="../about.html">About</a><a href="../publications.html">Publications</a><a href="../books.html">Books</a><a href="../teaching.html">Teaching</a><a href="../cv.html">CV</a><a href="../updates.html">Updates</a><a href="../quotes.html">Quotes</a><a href="../contact.html">Contact</a></nav></div><div class="footer-note">Academic website for research, teaching, and scholarly work.</div></div></footer>
<script src="../assets/js/main.js"></script><script>const citations = {{
{citation_entries}
}};function showCitation(type){{const box=document.getElementById("citationText");if(box)box.innerHTML=citations[type]||"";}}function copyCitation(){{const box=document.getElementById("citationText");if(!box)return;navigator.clipboard.writeText(box.innerText).then(()=>alert("Citation copied"));}}(function(){{var y=document.getElementById("year");if(y)y.textContent=new Date().getFullYear();showCitation("apa");}})();</script></body></html>
'''


def build_page(row: pd.Series) -> str:
    if is_book_material(row):
        return build_book_page(row)
    return _legacy_build_page(row)


def validate_rows(df: pd.DataFrame):
    errors, warnings, stats = _legacy_validate_rows(df)
    stats.setdefault("paid", 0); stats.setdefault("books", 0)
    for _, row in df.iterrows():
        if not is_book_material(row):
            continue
        stats["books"] += 1
        access = clean(row.get("access", "")).lower()
        if access == "paid": stats["paid"] += 1
        elif access not in {"open","request","paid"}: warnings.append(f"Unrecognised book access value '{access}': {clean(row.get('title',''))}")
        role = pdf_role(row)
        if role not in {"", "full_text", "full book", "preview"}: warnings.append(f"Unrecognised pdf_role '{role}': {clean(row.get('title',''))}")
        cover_path = normalise_path(row.get("cover_path", "")); pdf_path = normalise_path(row.get("pdf_path", ""))
        if cover_path and not (ROOT / cover_path).is_file(): warnings.append(f"Book cover not found on disk: {cover_path} | {clean(row.get('title',''))}")
        if pdf_path and not (ROOT / pdf_path).is_file(): warnings.append(f"Book PDF/preview not found on disk: {pdf_path} | {clean(row.get('title',''))}")
    return errors, warnings, stats


if __name__ == "__main__":
    sys.exit(main())
