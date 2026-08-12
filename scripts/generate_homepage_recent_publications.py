from pathlib import Path
import html
import re
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

DATA_FILE = ROOT / "data" / "publications.xlsx"
HOME_FILE = ROOT / "index.html"

START_MARKER = "<!-- HOMEPAGE_RECENT:START -->"
END_MARKER = "<!-- HOMEPAGE_RECENT:END -->"

RECENT_LIMIT = 5


def clean(value):
    """Convert empty or missing Excel values to an empty string."""
    if pd.isna(value):
        return ""
    return str(value).strip()


def esc(value):
    """Escape text for safe HTML output."""
    return html.escape(clean(value))


def normalise_path(value):
    return clean(value).replace("\\", "/")


def publication_category(row):
    """Create a simple category label for the homepage card."""

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


def get_summary(row):
    """
    Use the beginning of the abstract as a short description.
    If there is no abstract, use the publication venue instead.
    """

    abstract = clean(row.get("abstract", ""))

    if abstract:
        # Collapse repeated spaces.
        abstract = re.sub(r"\s+", " ", abstract)

        # Keep the description short enough for a homepage card.
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


def build_card(row):
    title = esc(row.get("title", "Untitled publication"))
    year = esc(row.get("year", ""))
    category = esc(publication_category(row))
    summary = get_summary(row)
    tags = get_tags(row)

    slug = clean(row.get("slug", ""))
    html_path = normalise_path(row.get("html_path", ""))

    if html_path:
        href = html_path
    elif slug:
        href = f"publications/{slug}.html"
    else:
        href = "publications.html"

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


def build_homepage_section(df):
    """
    Build the five newest publication cards.

    Excel row order is used as the tie breaker when several publications
    have the same year. Therefore, when a new record is added to the
    bottom of the Excel database, it will be treated as newer than older
    records from the same year.
    """

    df = df.copy()

    if "year" not in df.columns:
        raise ValueError("The Excel database does not contain a 'year' column.")

    df["year_num"] = pd.to_numeric(df["year"], errors="coerce")

    df = df[df["year_num"].notna()].copy()

    # Preserve Excel row order.
    df["excel_order"] = range(len(df))

    # Remove theses and projects from the homepage publication list.
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

    # Newest year first.
    # For publications in the same year, the latest Excel entry comes first.
    recent_df = df.sort_values(
        by=["year_num", "excel_order"],
        ascending=[False, False]
    ).head(RECENT_LIMIT)

    cards = "\n\n".join(
        build_card(row)
        for _, row in recent_df.iterrows()
    )

    return f"""{START_MARKER}

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

{END_MARKER}"""


def main():
    print("=" * 64)
    print("VALENTINE OWAN — HOMEPAGE RECENT PUBLICATIONS GENERATOR")
    print("=" * 64)

    print(f"Excel:  {DATA_FILE}")
    print(f"Output: {HOME_FILE}")

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Excel database not found: {DATA_FILE}"
        )

    if not HOME_FILE.exists():
        raise FileNotFoundError(
            f"Homepage not found: {HOME_FILE}"
        )

    df = pd.read_excel(DATA_FILE)

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.lower()
    )

    section_html = build_homepage_section(df)

    with HOME_FILE.open("r", encoding="utf-8") as f:
        home_html = f.read()

    pattern = re.compile(
        rf"{re.escape(START_MARKER)}.*?{re.escape(END_MARKER)}",
        flags=re.DOTALL
    )

    if not pattern.search(home_html):
        raise ValueError(
            "Homepage markers were not found.\n"
            f"Expected:\n{START_MARKER}\n...\n{END_MARKER}"
        )

    home_html = pattern.sub(section_html, home_html)

    with HOME_FILE.open("w", encoding="utf-8") as f:
        f.write(home_html)

    print()
    print(f"✓ Recent publications updated: {min(len(df), RECENT_LIMIT)}")
    print("✓ Homepage updated successfully.")
    print()
    print("Newest entries are selected by:")
    print("  1. Publication year")
    print("  2. Latest row position in the Excel database")
    print()


if __name__ == "__main__":
    main()