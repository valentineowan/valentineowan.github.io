from pathlib import Path
import html
import re

import pandas as pd


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

DATA_FILE = ROOT / "data" / "publications.xlsx"
HOME_FILE = ROOT / "index.html"
PUBLICATIONS_FILE = ROOT / "publications.html"


# ============================================================
# HTML MARKERS
# ============================================================

HOME_START_MARKER = "<!-- HOMEPAGE_RECENT:START -->"
HOME_END_MARKER = "<!-- HOMEPAGE_RECENT:END -->"

PUBLICATIONS_START_MARKER = "<!-- RECENT:START -->"
PUBLICATIONS_END_MARKER = "<!-- RECENT:END -->"


# ============================================================
# SETTINGS
# ============================================================

RECENT_LIMIT = 5


# ============================================================
# BASIC CLEANING
# ============================================================

def clean(value):
    """Convert empty or missing Excel values to an empty string."""
    if pd.isna(value):
        return ""
    return str(value).strip()


def esc(value):
    """Escape text for safe HTML output."""
    return html.escape(clean(value))


def normalise_path(value):
    """Convert Windows-style paths to web-style paths."""
    return clean(value).replace("\\", "/")


# ============================================================
# PUBLICATION CLASSIFICATION
# ============================================================

def publication_category(row):
    """Create a readable publication category."""

    publication_type = clean(row.get("publication_type", "")).lower()
    entry_type = clean(row.get("entry_type", "")).lower()

    if publication_type in {"monograph", "textbook", "book"}:
        return "Book"

    mapping = {
        "article": "Journal Article",
        "journal article": "Journal Article",
        "incollection": "Book Chapter",
        "book chapter": "Book Chapter",
        "inproceedings": "Conference Proceeding",
        "conference proceeding": "Conference Proceeding",
        "conference proceedings": "Conference Proceeding",
        "phdthesis": "Thesis",
        "mastersthesis": "Thesis",
        "project": "Research Project",
    }

    return mapping.get(entry_type, "Publication")


# ============================================================
# HOMEPAGE CONTENT HELPERS
# ============================================================

def get_summary(row):
    """
    Use the beginning of the abstract as a short description.
    If there is no abstract, use the publication venue instead.
    """

    abstract = clean(row.get("abstract", ""))

    if abstract:
        abstract = re.sub(r"\s+", " ", abstract)

        limit = 230

        if len(abstract) > limit:
            shortened = abstract[:limit]
            last_space = shortened.rfind(" ")

            if last_space > 0:
                shortened = shortened[:last_space]

            return esc(shortened + "…")

        return esc(abstract)

    venue = clean(row.get("journal", ""))

    if not venue:
        venue = clean(row.get("source_title", ""))

    if not venue:
        venue = clean(row.get("booktitle", ""))

    if venue:
        return esc(f"Published in {venue}.")

    return "Publication details are available on the individual publication page."


def get_tags(row):
    """Create up to three tags from the keywords column."""

    keywords = clean(row.get("keywords", ""))

    if not keywords:
        return ""

    tags = []

    for keyword in re.split(r"[;,]", keywords):
        keyword = keyword.strip()

        if keyword:
            tags.append(keyword)

        if len(tags) == 3:
            break

    if not tags:
        return ""

    tag_html = "\n".join(
        f"                    <span>{esc(tag)}</span>"
        for tag in tags
    )

    return f"""
                <div class="paper-tags">
{tag_html}
                </div>"""


def get_publication_href(row):
    """Return the preferred internal publication page link."""

    slug = clean(row.get("slug", ""))
    html_path = normalise_path(row.get("html_path", ""))

    if html_path:
        return html_path

    if slug:
        return f"publications/{slug}.html"

    return "publications.html"


def build_homepage_card(row):
    """Build one recent-publication card for the homepage."""

    title = esc(row.get("title", "Untitled publication"))
    year = esc(row.get("year", ""))
    category = esc(publication_category(row))
    summary = get_summary(row)
    tags = get_tags(row)
    href = get_publication_href(row)

    year_html = f" ({year})" if year else ""

    return f"""            <article class="card featured-paper">

                <div class="paper-category">
                    {category}{year_html}
                </div>

                <h3>
                    {title}
                </h3>

                <p>
                    {summary}
                </p>
{tags}

                <div class="card-actions">
                    <a class="text-link"
                       href="{html.escape(href, quote=True)}">
                        View Publication
                    </a>
                </div>

            </article>"""


# ============================================================
# PUBLICATIONS PAGE CONTENT HELPERS
# ============================================================

def get_publication_citation(row):
    """
    Build a compact citation for the Recent Publications section.

    If a ready-made citation exists in the Excel database, it is used.
    Otherwise, a readable fallback citation is assembled from available
    bibliographic fields.
    """

    for column in ("citation", "apa_citation", "reference", "full_citation"):
        value = clean(row.get(column, ""))

        if value:
            return esc(value)

    authors = clean(row.get("author", ""))

    if not authors:
        authors = clean(row.get("authors", ""))

    title = clean(row.get("title", "Untitled publication"))
    year = clean(row.get("year", ""))

    journal = clean(row.get("journal", ""))

    if not journal:
        journal = clean(row.get("source_title", ""))

    if not journal:
        journal = clean(row.get("booktitle", ""))

    volume = clean(row.get("volume", ""))
    issue = clean(row.get("number", ""))

    if not issue:
        issue = clean(row.get("issue", ""))

    pages = clean(row.get("pages", ""))

    parts = []

    if authors:
        parts.append(authors)

    if year:
        parts.append(f"({year}).")

    if title:
        parts.append(f"{title}.")

    citation = " ".join(parts)

    if journal:
        venue = f"<em>{esc(journal)}</em>"

        if volume:
            venue += f", {esc(volume)}"

        if issue:
            venue += f"({esc(issue)})"

        if pages:
            venue += f", {esc(pages)}"

        citation += f" {venue}."

    elif pages:
        citation += f" {esc(pages)}."

    return citation


def get_external_publication_href(row):
    """
    Prefer DOI or URL for the citation link on publications.html.
    If neither exists, use the internal publication page.
    """

    doi = clean(row.get("doi", ""))

    if doi:
        if doi.lower().startswith(("http://", "https://")):
            return doi
        return f"https://doi.org/{doi}"

    for column in ("url", "link", "publisher_url"):
        value = clean(row.get(column, ""))

        if value:
            return normalise_path(value)

    return get_publication_href(row)


def build_publications_recent_item(row):
    """Build one compact recent-publication item for publications.html."""

    year = esc(row.get("year", ""))
    citation = get_publication_citation(row)
    href = get_external_publication_href(row)

    return f"""  <li class="pub-entry" data-type="selected" data-year="{year}">
    <a class="pub-cite" href="{html.escape(href, quote=True)}" target="_blank" rel="noopener">
      {citation}
    </a>
  </li>"""


# ============================================================
# RECENT PUBLICATION SELECTION
# ============================================================

def get_recent_publications(df):
    """
    Select the newest eligible publications.

    Publication year is the primary ordering variable.
    When several records have the same year, the latest row in the Excel
    database is treated as newer than earlier rows.

    Theses and projects are excluded.
    """

    df = df.copy()

    if "year" not in df.columns:
        raise ValueError(
            "The Excel database does not contain a 'year' column."
        )

    df["year_num"] = pd.to_numeric(df["year"], errors="coerce")
    df = df[df["year_num"].notna()].copy()

    # Preserve original Excel row order.
    df["excel_order"] = range(len(df))

    if "entry_type" in df.columns:
        excluded_types = {
            "phdthesis",
            "mastersthesis",
            "bedproject",
            "nceproject",
            "project",
        }

        df = df[
            ~df["entry_type"]
            .astype(str)
            .str.strip()
            .str.lower()
            .isin(excluded_types)
        ].copy()

    return (
        df.sort_values(
            by=["year_num", "excel_order"],
            ascending=[False, False]
        )
        .head(RECENT_LIMIT)
    )


# ============================================================
# SECTION BUILDERS
# ============================================================

def build_homepage_section(recent_df):
    """Build the Recent Publications section for index.html."""

    cards = "\n\n".join(
        build_homepage_card(row)
        for _, row in recent_df.iterrows()
    )

    return f"""{HOME_START_MARKER}

<section class="section">

    <div class="container">

        <h2 class="section-title">
            Recent Publications
        </h2>

        <p class="section-kicker">
            The five most recent additions to the publication record.
        </p>

        <div class="grid-3">

{cards}

        </div>

        <div class="mt-12">

            <a class="btn"
               href="publications.html">

                Browse All Publications

            </a>

        </div>

    </div>

</section>

{HOME_END_MARKER}"""


def build_publications_recent_section(recent_df):
    """Build the compact Recent Publications list for publications.html."""

    items = "\n".join(
        build_publications_recent_item(row)
        for _, row in recent_df.iterrows()
    )

    return f"""{PUBLICATIONS_START_MARKER}
<ol class="pub-list">
{items}
</ol>
{PUBLICATIONS_END_MARKER}"""


# ============================================================
# FILE REPLACEMENT
# ============================================================

def replace_marked_section(
    file_path,
    start_marker,
    end_marker,
    replacement_html,
    label,
):
    """Replace HTML content between two marker comments."""

    if not file_path.exists():
        raise FileNotFoundError(
            f"{label} file not found: {file_path}"
        )

    with file_path.open("r", encoding="utf-8") as f:
        file_html = f.read()

    pattern = re.compile(
        rf"{re.escape(start_marker)}.*?{re.escape(end_marker)}",
        flags=re.DOTALL,
    )

    if not pattern.search(file_html):
        raise ValueError(
            f"{label} markers were not found.\n"
            f"Expected:\n{start_marker}\n...\n{end_marker}"
        )

    updated_html = pattern.sub(replacement_html, file_html)

    with file_path.open("w", encoding="utf-8") as f:
        f.write(updated_html)


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 68)
    print("VALENTINE OWAN — RECENT PUBLICATIONS GENERATOR")
    print("=" * 68)
    print()

    print(f"Excel database:     {DATA_FILE}")
    print(f"Homepage:           {HOME_FILE}")
    print(f"Publications page:  {PUBLICATIONS_FILE}")
    print()

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Excel database not found: {DATA_FILE}"
        )

    df = pd.read_excel(DATA_FILE)

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.lower()
    )

    recent_df = get_recent_publications(df)

    if recent_df.empty:
        raise ValueError(
            "No eligible publications were found in the Excel database."
        )

    # Build both sections from the exact same five records.
    homepage_section = build_homepage_section(recent_df)

    publications_recent_section = (
        build_publications_recent_section(recent_df)
    )

    # Update homepage.
    replace_marked_section(
        HOME_FILE,
        HOME_START_MARKER,
        HOME_END_MARKER,
        homepage_section,
        "Homepage",
    )

    # Update publications page.
    replace_marked_section(
        PUBLICATIONS_FILE,
        PUBLICATIONS_START_MARKER,
        PUBLICATIONS_END_MARKER,
        publications_recent_section,
        "Publications page",
    )

    print("✓ Recent publications updated successfully.")
    print(f"✓ Records selected: {len(recent_df)}")
    print("✓ Homepage recent-publication section updated.")
    print("✓ Publications page recent-publication section updated.")
    print()
    print("Selection order:")
    print("  1. Newest publication year")
    print("  2. Latest row position in the Excel database")
    print()
    print("The same publication records are now used on both pages.")


if __name__ == "__main__":
    main()
