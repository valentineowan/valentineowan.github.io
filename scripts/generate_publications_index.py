from pathlib import Path
import re
import html
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "publications.xlsx"
PUBLICATIONS_FILE = ROOT / "publications.html"

START_MARKER = "<!-- ARCHIVE:START -->"
END_MARKER = "<!-- ARCHIVE:END -->"

YEARJUMP_START = "<!-- YEARJUMP:START -->"
YEARJUMP_END = "<!-- YEARJUMP:END -->"

RECENT_START = "<!-- RECENT:START -->"
RECENT_END = "<!-- RECENT:END -->"

RECENT_LIMIT = 4


def safe_text(value):
    if pd.isna(value):
        return ""
    return html.escape(str(value).strip())


def safe_attr(value):
    if pd.isna(value):
        return ""
    return html.escape(str(value).strip(), quote=True)


def safe_int(value, default=0):
    try:
        if pd.isna(value) or str(value).strip() == "":
            return default
        return int(float(value))
    except Exception:
        return default


def clean_text(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def normalise_access(value):
    value = clean_text(value).lower()
    return value if value else "request"


def map_entry_type(value):
    value = clean_text(value).lower()

    mapping = {
        "article": "article",
        "journal article": "article",
        "incollection": "chapter",
        "book chapter": "chapter",
        "inproceedings": "proceeding",
        "conference proceeding": "proceeding",
        "conference proceedings": "proceeding",
        "book": "chapter",
        "phdthesis": "thesis",
        "mastersthesis": "thesis",
        "bedproject": "thesis",
        "nceproject": "thesis",
        "project": "thesis",
    }

    return mapping.get(value, "article")


def build_main_link(row):
    doi = clean_text(row.get("doi", ""))
    pdf_path = clean_text(row.get("pdf_path", ""))

    if doi:
        return f"https://doi.org/{doi}"
    if pdf_path:
        return pdf_path.replace("\\", "/")
    return "#"


def build_venue(row):
    journal = clean_text(row.get("journal", ""))
    source_title = clean_text(row.get("source_title", ""))
    booktitle = clean_text(row.get("booktitle", ""))

    if journal:
        return journal
    if source_title:
        return source_title
    if booktitle:
        return booktitle
    return ""


def clean_number(value):
    try:
        if pd.isna(value) or str(value).strip() == "":
            return ""
        num = float(value)
        if num.is_integer():
            return str(int(num))
        return str(num)
    except Exception:
        return str(value).strip()


def build_citation_text(row):
    authors = safe_text(row.get("authors", ""))
    year = clean_text(row.get("year", ""))
    title = safe_text(row.get("title", ""))
    venue = safe_text(build_venue(row))

    volume = clean_number(row.get("volume", ""))
    issue = clean_number(row.get("issue", ""))
    pages = safe_text(row.get("pages", ""))

    year_text = year if year else "n.d."

    citation = f"{authors} ({year_text}). {title}."

    if venue:
        citation += f" <em>{venue}</em>"

        if volume and issue:
            citation += f", {volume}({issue})"
        elif volume:
            citation += f", {volume}"
        elif issue:
            citation += f", ({issue})"

        if pages:
            citation += f", {pages}"

        citation += "."

    return citation


def build_links_block(row):
    slug = clean_text(row.get("slug", ""))
    pdf_path = clean_text(row.get("pdf_path", "")).replace("\\", "/")
    access = normalise_access(row.get("access", ""))
    citations = safe_int(row.get("openalex_citations", 0), 0)

    parts = []
    parts.append(f'<span class="tag">OpenAlex citations: {citations}</span>')

    if slug:
        parts.append(
            f'<a class="btn btn-ghost" href="publications/{safe_attr(slug)}.html">View details</a>'
        )

    if access == "open" and pdf_path:
        parts.append(
            f'<a class="btn btn-ghost" href="{safe_attr(pdf_path)}" target="_blank" rel="noopener">Read PDF</a>'
        )
    else:
        parts.append('<span class="pub-access-note">Closed access · Available upon request</span>')
        parts.append('<a class="btn btn-ghost" href="contact.html">Request a copy</a>')

    return '<div class="pub-links">\n                  ' + "\n                  ".join(parts) + "\n                </div>"


def build_entry_html(row):
    year = clean_text(row.get("year", ""))
    data_year = safe_attr(year)
    data_type = safe_attr(map_entry_type(row.get("entry_type", "")))
    href = safe_attr(build_main_link(row))

    citation_html = build_citation_text(row)
    links_html = build_links_block(row)

    target_attr = ' target="_blank" rel="noopener"' if href.startswith("http") else ""

    if href == "#":
        return f"""      <li class="pub-entry" data-type="{data_type}" data-year="{data_year}">
        <span class="pub-cite">
          {citation_html}
        </span>
        {links_html}
      </li>"""
    else:
        return f"""      <li class="pub-entry" data-type="{data_type}" data-year="{data_year}">
        <a class="pub-cite" href="{href}"{target_attr}>
          {citation_html}
        </a>
        {links_html}
      </li>"""


def build_recent_entry_html(row):
    year = clean_text(row.get("year", ""))
    href = safe_attr(build_main_link(row))
    citation_html = build_citation_text(row)

    target_attr = ' target="_blank" rel="noopener"' if href.startswith("http") else ""

    if href == "#":
        return f"""  <li class="pub-entry" data-type="selected" data-year="{safe_attr(year)}">
    <span class="pub-cite">
      {citation_html}
    </span>
  </li>"""
    else:
        return f"""  <li class="pub-entry" data-type="selected" data-year="{safe_attr(year)}">
    <a class="pub-cite" href="{href}"{target_attr}>
      {citation_html}
    </a>
  </li>"""


def build_year_block(year, rows, open_years=None):
    if open_years is None:
        open_years = set()

    open_attr = " open" if year in open_years else ""
    items = "\n\n".join(build_entry_html(row) for _, row in rows.iterrows())

    return f"""  <details class="pub-year" id="year-{year}"{open_attr}>
    <summary>{year}</summary>
    <ol class="pub-list">
{items}
    </ol>
  </details>"""


def build_section(section_id, heading, label_id, section_df, open_years):
    if section_df.empty:
        return ""

    grouped = section_df.groupby("year_num", sort=False)
    year_blocks = [build_year_block(y, g, open_years) for y, g in grouped]

    section_id_attr = f' id="{section_id}"' if section_id else ""

    return f"""        <section class="pub-section"{section_id_attr}>
          <div class="pub-section-head">
            <h3>{heading}</h3>
            <span class="tag" id="{label_id}">0</span>
          </div>

{chr(10).join(year_blocks)}
        </section>"""


def replace_count_by_id(html_text, element_id, value):
    pattern = rf'(id="{element_id}">\s*)\d+(\s*<)'
    return re.sub(pattern, rf'\g<1>{value}\g<2>', html_text)


def build_yearjump_html(years):
    links = "\n".join([f'            <a href="#year-{year}">{year}</a>' for year in years])
    return f"""{YEARJUMP_START}
          <div class="year-jump" aria-label="Jump to year">
{links}
          </div>
{YEARJUMP_END}"""


def replace_year_filter_options(html_text, years):
    options = ['              <option value="">All years</option>']
    options.extend([f'              <option value="{year}">{year}</option>' for year in years])
    options_html = "\n".join(options)

    pattern = re.compile(
        r'(<select id="yearFilter"[^>]*>\s*)(.*?)(\s*</select>)',
        flags=re.DOTALL
    )

    if not pattern.search(html_text):
        return html_text

    return pattern.sub(rf'\1{options_html}\3', html_text, count=1)


def build_recent_html(df):
    recent_df = df.sort_values(
        by=["year_num", "sort_citations", "sort_title"],
        ascending=[False, False, True]
    ).head(RECENT_LIMIT)

    items = "\n".join(build_recent_entry_html(row) for _, row in recent_df.iterrows())

    return f"""{RECENT_START}
<ol class="pub-list">
{items}
</ol>
{RECENT_END}"""


def main():
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Excel file not found: {DATA_FILE}")

    if not PUBLICATIONS_FILE.exists():
        raise FileNotFoundError(f"HTML file not found: {PUBLICATIONS_FILE}")

    df = pd.read_excel(DATA_FILE)
    df.columns = df.columns.str.strip().str.lower()
    df = df.fillna("")

    # Books, monographs and textbooks have their own catalogue and are not
    # duplicated inside the journal-article archive.
    if "publication_type" in df.columns:
        book_types = {"monograph", "textbook", "book"}
        book_mask = df["publication_type"].astype(str).str.strip().str.lower().isin(book_types)
        df = df[~book_mask].copy()

    df["year_num"] = pd.to_numeric(df["year"], errors="coerce")
    df = df[df["year_num"].notna()].copy()
    df["year_num"] = df["year_num"].astype(int)

    df["site_type"] = df["entry_type"].apply(map_entry_type)
    df = df[df["site_type"] != "thesis"].copy()

    df["sort_citations"] = df["openalex_citations"].apply(lambda x: safe_int(x, 0))
    df["sort_title"] = df["title"].astype(str).str.lower()

    df = df.sort_values(
        by=["year_num", "sort_citations", "sort_title"],
        ascending=[False, False, True]
    )

    years = sorted(df["year_num"].unique(), reverse=True)
    open_years = set(years[:2])

    articles_df = df[df["site_type"] == "article"]
    chapters_df = df[df["site_type"] == "chapter"]
    proceedings_df = df[df["site_type"] == "proceeding"]

    total_count = len(df)
    articles_count = len(articles_df)
    chapters_count = len(chapters_df)
    proceedings_count = len(proceedings_df)

    archive_html = "\n\n".join([
        build_section("", "Journal articles", "labelArticles", articles_df, open_years),
        build_section("book-chapters", "Book chapters", "labelChapters", chapters_df, open_years),
        build_section("conference-proceedings", "Conference proceedings", "labelProceedings", proceedings_df, open_years)
    ])

    recent_html = build_recent_html(df)

    with PUBLICATIONS_FILE.open("r", encoding="utf-8") as f:
        html_text = f.read()

    if 'href="books.html"' not in html_text:
        html_text = html_text.replace(
            '<a class="nav-link" href="publications.html">Publications</a>',
            '<a class="nav-link" href="publications.html">Publications</a>\n        <a class="nav-link" href="books.html">Books</a>',
            1,
        )

    html_text = re.sub(
        rf"{re.escape(START_MARKER)}.*?{re.escape(END_MARKER)}",
        f"{START_MARKER}\n{archive_html}\n{END_MARKER}",
        html_text,
        flags=re.DOTALL
    )

    html_text = re.sub(
        rf"{re.escape(RECENT_START)}.*?{re.escape(RECENT_END)}",
        recent_html,
        html_text,
        flags=re.DOTALL
    )

    html_text = replace_count_by_id(html_text, "countAll", total_count)
    html_text = replace_count_by_id(html_text, "countArticles", articles_count)
    html_text = replace_count_by_id(html_text, "countChapters", chapters_count)
    html_text = replace_count_by_id(html_text, "countProceedings", proceedings_count)

    html_text = replace_count_by_id(html_text, "labelArticles", articles_count)
    html_text = replace_count_by_id(html_text, "labelChapters", chapters_count)
    html_text = replace_count_by_id(html_text, "labelProceedings", proceedings_count)

    html_text = replace_year_filter_options(html_text, years)

    yearjump_pattern = re.compile(
        rf"{re.escape(YEARJUMP_START)}.*?{re.escape(YEARJUMP_END)}",
        flags=re.DOTALL
    )
    yearjump_html = build_yearjump_html(years)

    if yearjump_pattern.search(html_text):
        html_text = yearjump_pattern.sub(yearjump_html, html_text)
    else:
        print("Warning: YEARJUMP markers not found. Year jump links were not updated.")

    with PUBLICATIONS_FILE.open("w", encoding="utf-8") as f:
        f.write(html_text)

    print("✅ Recent publications, archive, and year controls updated successfully")
    print(
        f"Total: {total_count} | Articles: {articles_count} | "
        f"Chapters: {chapters_count} | Proceedings: {proceedings_count}"
    )
    print("Years:", ", ".join(map(str, years)))


if __name__ == "__main__":
    main()