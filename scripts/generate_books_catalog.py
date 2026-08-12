#!/usr/bin/env python3
"""Generate books.html from the book/monograph/textbook records in publications.xlsx."""
from __future__ import annotations

import argparse
import html
from pathlib import Path
from typing import Any

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
DATA_FILE = ROOT / "data" / "publications.xlsx"
OUTPUT_FILE = ROOT / "books.html"
SITE_URL = "https://www.valentineowan.com"
BOOK_TYPES = {"monograph", "textbook", "book"}


def clean(value: Any) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass
    return str(value).strip()


def esc(value: Any) -> str:
    return html.escape(clean(value), quote=True)


def norm_path(value: Any) -> str:
    return clean(value).replace("\\", "/").lstrip("/")


def kind(row: pd.Series) -> str:
    return clean(row.get("publication_type", "")).lower()


def status(row: pd.Series) -> str:
    return clean(row.get("publication_status", "")).lower() or "published"


def access_label(row: pd.Series) -> str:
    value = clean(row.get("access", "")).lower()
    return {"open": "Open Access", "request": "Available upon request", "paid": "Paid"}.get(value, value.title() or "Available")


def href_from_books_page(path: str) -> str:
    return norm_path(path)


def card(row: pd.Series) -> str:
    title = clean(row.get("title", "Untitled book"))
    authors = clean(row.get("authors", ""))
    year = clean(row.get("year", ""))
    book_kind = kind(row)
    book_status = status(row)
    cover_path = norm_path(row.get("cover_path", ""))
    html_path = norm_path(row.get("html_path", ""))
    href = href_from_books_page(html_path) if html_path else "#"
    cover = f'<img class="book-card-cover" src="{esc(cover_path)}" alt="Cover of {esc(title)}" loading="lazy" />' if cover_path else '<div class="book-card-cover book-card-placeholder">Cover image</div>'
    description = clean(row.get("book_description", "")) or clean(row.get("abstract", ""))
    if len(description) > 260:
        description = description[:257].rsplit(" ", 1)[0] + "…"
    return f'''<article class="book-card card">
  <a class="book-card-cover-link" href="{esc(href)}">{cover}</a>
  <div class="book-card-body">
    <p class="book-card-type">{esc(book_kind.title())}</p>
    <p class="book-card-year">{esc(year)}</p>
    <h2><a href="{esc(href)}">{esc(title)}</a></h2>
    <p class="book-card-authors">{esc(authors)}</p>
    <div class="book-card-tags"><span class="tag">{esc(book_status.title())}</span><span class="tag">{esc(access_label(row))}</span></div>
    {f'<p class="book-card-description">{esc(description)}</p>' if description else ''}
    <a class="btn btn-ghost" href="{esc(href)}">View book</a>
  </div>
</article>'''


def build_page(df: pd.DataFrame) -> str:
    rows = []
    for _, row in df.iterrows():
        rows.append(card(row))
    content = "\n".join(rows) if rows else '<div class="card"><p>No books, monographs or textbooks have been added yet.</p></div>'
    return f'''<!doctype html>
<html lang="en-GB">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Books | Valentine Joseph Owan</title>
  <meta name="description" content="Books, monographs and textbooks by Valentine Joseph Owan." />
  <link rel="canonical" href="{SITE_URL}/books.html" />
  <link rel="stylesheet" href="assets/css/style.css" />
  <style>
    .books-intro{{max-width:780px;margin-bottom:22px}}
    .books-grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}}
    .book-card{{display:grid;grid-template-columns:minmax(130px,190px) 1fr;gap:18px;align-items:start}}
    .book-card-cover-link{{display:block}}
    .book-card-cover{{width:100%;aspect-ratio:2/3;object-fit:cover;border-radius:10px;border:1px solid var(--line);background:var(--panel);box-shadow:0 6px 18px rgba(17,24,39,.08)}}
    .book-card-placeholder{{display:grid;place-items:center;color:var(--muted);padding:16px;text-align:center}}
    .book-card-body h2{{margin:5px 0 8px;font-size:1.1rem;line-height:1.35}}
    .book-card-body h2 a{{text-decoration:none}}
    .book-card-type{{margin:0;text-transform:uppercase;letter-spacing:.08em;font-size:.76rem;color:var(--muted)}}
    .book-card-year{{margin:3px 0;color:var(--muted);font-size:.9rem}}
    .book-card-authors{{margin:0 0 10px;color:var(--muted)}}
    .book-card-tags{{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 12px}}
    .book-card-description{{line-height:1.6;color:var(--muted)}}
    @media(max-width:800px){{.books-grid{{grid-template-columns:1fr}}}}
    @media(max-width:560px){{.book-card{{grid-template-columns:1fr}}.book-card-cover{{max-width:210px}}}}
  </style>
</head>
<body>
  <a class="skip-link" href="#main">Skip to content</a>
  <header class="site-header"><div class="container header-inner">
    <div class="brand"><a href="index.html" class="brand-name">Valentine Joseph Owan</a><div class="brand-tag">Researcher | Psychometrician | Statistician</div></div>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav">Menu</button>
    <nav id="site-nav" class="site-nav" aria-label="Primary">
      <a class="nav-link" href="index.html">Home</a><a class="nav-link" href="about.html">About</a><a class="nav-link" href="publications.html">Publications</a><a class="nav-link active" href="books.html">Books</a><a class="nav-link" href="teaching.html">Teaching</a><a class="nav-link" href="cv.html">CV</a><a class="nav-link" href="updates.html">Updates</a><a class="nav-link" href="contact.html">Contact</a><a class="nav-link" href="quotes.html">Quotes</a>
    </nav>
  </div></header>
  <main id="main" class="section"><div class="container">
    <div class="crumbs" style="font-size:14px;color:var(--muted);margin-bottom:12px"><a href="index.html">Home</a> / Books</div>
    <div class="books-intro"><p class="kicker">Books</p><h1>Books, Monographs and Textbooks</h1><p>A catalogue of books by Valentine Joseph Owan, arranged from newest to oldest.</p></div>
    <section class="books-grid">
{content}
    </section>
  </div></main>
  <footer class="site-footer"><div class="container"><div class="footer-top"><div class="footer-copy">© <span id="year"></span> Valentine Joseph Owan <span class="footer-sep">•</span> University of Calabar</div><nav class="footer-links" aria-label="Footer"><a href="index.html">Home</a><a href="about.html">About</a><a href="publications.html">Publications</a><a href="books.html">Books</a><a href="teaching.html">Teaching</a><a href="cv.html">CV</a><a href="updates.html">Updates</a><a href="quotes.html">Quotes</a><a href="contact.html">Contact</a></nav></div><div class="footer-note">Academic website for research, teaching, and scholarly work.</div></div></footer>
  <script src="assets/js/main.js"></script><script>(function(){{var y=document.getElementById("year");if(y)y.textContent=new Date().getFullYear();}})();</script>
</body>
</html>
'''


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate books.html from publications.xlsx")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if not DATA_FILE.exists():
        print(f"ERROR: Excel file not found: {DATA_FILE}")
        return 1
    df = pd.read_excel(DATA_FILE).fillna("")
    if "publication_type" not in df.columns:
        print("ERROR: publications.xlsx does not yet contain 'publication_type'.")
        print("Run the database upgrade before generating the Books catalogue.")
        return 1
    books = df[df["publication_type"].astype(str).str.strip().str.lower().isin(BOOK_TYPES)].copy()
    books["year_num"] = pd.to_numeric(books.get("year", ""), errors="coerce")
    books["title_sort"] = books.get("title", "").astype(str).str.lower()
    books = books.sort_values(["year_num", "title_sort"], ascending=[False, True], na_position="last")
    print("VALENTINE OWAN — BOOKS CATALOGUE GENERATOR")
    print(f"Excel:  {DATA_FILE}")
    print(f"Output: {OUTPUT_FILE}")
    print(f"Books:  {len(books)}")
    if args.dry_run:
        print("Dry run complete. No HTML files were changed.")
        return 0
    OUTPUT_FILE.write_text(build_page(books), encoding="utf-8")
    print(f"Generated: {OUTPUT_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
