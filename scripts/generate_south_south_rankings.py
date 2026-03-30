from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "south_south_rankings.xlsx"

UNIVERSITY_SHEET = "University_Metrics"
BLOCK_SHEET = "Block_Metrics"

MAIN_PAGE = ROOT / "south-south-rankings.html"

THESIS_TITLE = (
    "Academic Capacity Variables as Predictors of Research Publication in Mainstream "
    "Journals among University Lecturers in South-South Nigeria"
)

THESIS_SOURCE_SHORT = (
    "Derived from the doctoral research of Valentine Joseph Owan on university research "
    "performance in South-South Nigeria, University of Calabar, 2026."
)

THESIS_SOURCE_LONG = (
    f"The ranking framework and associated metrics presented on this page were developed "
    f"as part of a doctoral research study titled <em>{THESIS_TITLE}</em>. The study was "
    f"conducted by <strong>Owan, Valentine Joseph</strong> in the Department of Educational "
    f"Psychology, University of Calabar, Nigeria, and submitted to the College of "
    f"Postgraduate Studies in partial fulfilment of the requirements for the award of the "
    f"Doctor of Philosophy (Ph.D.) degree in Research, Measurement and Evaluation, March 2026."
)

DATA_NOTE_SUFFIX = (
    "Data were extracted from the Scopus database and were accurate as of 12 pm, 9 February 2026."
)


UNIVERSITY_METRICS: List[Dict[str, Any]] = [
    {
        "slug": "tro",
        "title": "Total Research Output (TRO)",
        "sheet": "university",
        "column": "Number of Documents",
        "display_name": "TRO",
        "meaning": (
            "Total Research Output refers to the total number of scholarly documents produced "
            "by a university in mainstream journals. It represents the cumulative volume of "
            "research publications attributed to an institution over time. In simple terms, "
            "this metric shows how much research a university has contributed without adjusting "
            "for staff size or institutional age. Universities with higher TRO values have "
            "produced more publications, while those with lower values have contributed fewer. "
            "For that reason, TRO serves as a direct indicator of institutional research "
            "productivity and gives a clear starting point for comparison."
        ),
        "formula": "TRO = Number of Documents",
        "usefulness": [
            "Gives a direct measure of total research output.",
            "Works well as a baseline ranking before adjusted metrics are applied.",
            "Helps identify institutions with the largest publication volume.",
        ],
        "strengths": [
            "Simple and easy to understand.",
            "Based on verifiable publication records.",
            "Useful for descriptive institutional comparison.",
        ],
        "limitations": [
            "Favours older institutions with longer publication history.",
            "Does not adjust for staff size.",
            "Does not measure efficiency.",
        ],
        "note": (
            "Ranking is based on the total number of Scopus indexed documents associated "
            "with each university."
        ),
        "sort_desc": True,
        "table_columns": [
            "Institution",
            "Block",
            "Number of Documents",
            "Year established",
            "Age",
        ],
    },
    {
        "slug": "rps",
        "title": "Research Participation Size (RPS)",
        "sheet": "university",
        "column": "Number of Authors",
        "display_name": "RPS",
        "meaning": (
            "Research Participation Size refers to the total number of authors affiliated "
            "with each university who have published in mainstream journals. It indicates "
            "the size of the research-active staff base within an institution. In simple "
            "terms, RPS shows how many lecturers or researchers are actively involved in "
            "publishing. Universities with higher values have a larger pool of staff "
            "contributing to research, while lower values point to a smaller active group. "
            "This helps explain whether strong output is linked to broad staff participation "
            "or to the work of a smaller number of researchers."
        ),
        "formula": "RPS = Number of Authors",
        "usefulness": [
            "Shows the size of the research-active workforce.",
            "Helps explain differences in institutional output.",
            "Supports interpretation of productivity and efficiency metrics.",
        ],
        "strengths": [
            "Easy to compute and interpret.",
            "Useful for understanding staff participation in research.",
            "Adds explanatory value to output-based rankings.",
        ],
        "limitations": [
            "Does not measure publication quality or efficiency.",
            "A large staff base does not always mean high productivity.",
            "Should be read alongside other metrics.",
        ],
        "note": (
            "Ranking is based on the total number of authors affiliated with each university "
            "who have published in Scopus indexed journals."
        ),
        "sort_desc": True,
        "table_columns": [
            "Institution",
            "Block",
            "Number of Authors",
            "Number of Documents",
            "Age",
        ],
    },
    {
        "slug": "rii",
        "title": "Research Intensity Index (RII)",
        "sheet": "university",
        "column": "RII(Docs/authors)",
        "display_name": "RII",
        "meaning": (
            "Research Intensity Index measures the average research output per researcher "
            "within each university. It is calculated by dividing the total number of "
            "documents produced by an institution by the number of authors affiliated with "
            "that institution. In simple terms, RII shows how productive the average "
            "research-active staff member is. A higher value means that, on average, each "
            "researcher contributes more published work, while a lower value points to lower "
            "average output per researcher. This moves attention away from total volume alone "
            "and towards researcher-level efficiency."
        ),
        "formula": "RII = Number of Documents / Number of Authors",
        "usefulness": [
            "Allows fairer comparison across universities of different sizes.",
            "Shows average output per researcher.",
            "Helps separate scale from efficiency.",
        ],
        "strengths": [
            "Controls for differences in staff size.",
            "Useful for comparing large and small institutions.",
            "Easy to interpret as output per researcher.",
        ],
        "limitations": [
            "Does not adjust for institutional age.",
            "Can be affected by very small author counts.",
            "Does not account for publication quality.",
        ],
        "note": "Ranking is based on average research output per author.",
        "sort_desc": True,
        "table_columns": [
            "Institution",
            "Block",
            "RII(Docs/authors)",
            "Number of Documents",
            "Number of Authors",
        ],
    },
    {
        "slug": "anps",
        "title": "Age-Normalised Productivity Score (ANPS)",
        "sheet": "university",
        "column": "ANPS(Docs/Age)",
        "display_name": "ANPS",
        "meaning": (
            "Age-Normalised Productivity Score measures the average annual research output "
            "of each university. It is computed by dividing the total number of documents "
            "produced by an institution by the number of years since it was established. In "
            "simple terms, ANPS shows how much research a university produces per year. "
            "Older universities often appear stronger when total output alone is used because "
            "they have existed longer. This metric reduces that historical advantage and "
            "places universities of different ages on a more comparable scale."
        ),
        "formula": "ANPS = Number of Documents / Age of Institution",
        "usefulness": [
            "Adjusts output for institutional age.",
            "Supports fairer comparison between old and new universities.",
            "Shows average yearly productivity.",
        ],
        "strengths": [
            "Reduces the effect of institutional age on output comparisons.",
            "Simple to calculate and explain.",
            "Useful for age-adjusted productivity assessment.",
        ],
        "limitations": [
            "Does not adjust for staff size.",
            "Can favour younger institutions with recent output surges.",
            "Still does not address quality differences in publications.",
        ],
        "note": "Ranking is based on age-normalised research output.",
        "sort_desc": True,
        "table_columns": [
            "Institution",
            "Block",
            "ANPS(Docs/Age)",
            "Year established",
            "Age",
            "Number of Documents",
        ],
    },
    {
        "slug": "rmf",
        "title": "Research Momentum Factor (RMF)",
        "sheet": "university",
        "column": "RMF(Docs/Age x Authors)",
        "display_name": "RMF",
        "meaning": (
            "Research Momentum Factor measures sustained research productivity per researcher "
            "per year within each university. It is calculated by dividing the total number "
            "of documents by the product of the number of authors and the institutional age. "
            "RMF combines output, staff participation, and time into one indicator. In simple "
            "terms, it shows how consistently productive a university has been when both its "
            "research workforce and its years of existence are taken into account. Higher "
            "values suggest stronger sustained productivity over time."
        ),
        "formula": "RMF = Number of Documents / (Number of Authors × Age)",
        "usefulness": [
            "Brings together output, staff participation, and time in one metric.",
            "Useful for spotting younger institutions with strong momentum.",
            "Adds an efficiency-over-time angle to institutional comparison.",
        ],
        "strengths": [
            "Balances output, age, and authorship.",
            "Useful for comparative reporting.",
            "Shows sustained productivity rather than raw totals alone.",
        ],
        "limitations": [
            "Less intuitive than simpler metrics like TRO or RII.",
            "Can favour younger institutions with small but active staff bases.",
            "Should be read with other metrics for fuller meaning.",
        ],
        "note": "Ranking is based on sustained research productivity per author per year.",
        "sort_desc": True,
        "table_columns": [
            "Institution",
            "Block",
            "RMF(Docs/Age x Authors)",
            "Age",
            "Number of Documents",
            "Number of Authors",
        ],
    },
    {
        "slug": "ird",
        "title": "Institutional Research Density (IRD)",
        "sheet": "university",
        "column": "IRD(Authors/Age)",
        "display_name": "IRD",
        "meaning": (
            "Institutional Research Density measures the rate at which research capacity has "
            "expanded within each university over time. It is calculated by dividing the "
            "number of authors affiliated with an institution by the number of years since "
            "the university was established. In simple terms, IRD shows how quickly a "
            "university has built a pool of research-active staff. Higher values point to "
            "faster growth in research capacity, while lower values point to slower growth. "
            "This is useful because it brings attention to staff development patterns that "
            "may not be visible from publication output alone."
        ),
        "formula": "IRD = Number of Authors / Age",
        "usefulness": [
            "Shows growth in research-active staffing over time.",
            "Helps identify institutions building research capacity quickly.",
            "Adds a workforce-development angle to publication analysis.",
        ],
        "strengths": [
            "Simple way to assess research capacity growth.",
            "Useful for identifying emerging institutions.",
            "Complements output-focused measures.",
        ],
        "limitations": [
            "Does not directly measure publication output.",
            "A high value does not necessarily mean high research quality.",
            "Can favour newer institutions with rapid staff build-up.",
        ],
        "note": (
            "Ranking is based on research capacity growth measured as authors per year of "
            "institutional age."
        ),
        "sort_desc": True,
        "table_columns": [
            "Institution",
            "Block",
            "IRD(Authors/Age)",
            "Age",
            "Number of Authors",
        ],
    },
    {
        "slug": "anoi",
        "title": "Age-Normalised Output Index (ANOI)",
        "sheet": "university",
        "column": "ANOI (ANPS/Mean ANPS of all institutions)",
        "display_name": "ANOI",
        "meaning": (
            "Age-Normalised Output Index measures the research productivity of each "
            "university relative to the system-wide average after adjusting for "
            "institutional age. It is computed by dividing the ANPS of an institution by "
            "the mean ANPS of all institutions in the analysis. In simple terms, ANOI shows "
            "whether a university is performing above or below the average annual research "
            "output expected for its age. Values above one indicate above-average "
            "age-adjusted productivity, while values below one indicate below-average "
            "performance."
        ),
        "formula": "ANOI = ANPS / Mean ANPS of all institutions",
        "usefulness": [
            "Places each university in relation to the wider system average.",
            "Helps identify institutions outperforming or underperforming for their age.",
            "Supports quick comparative assessment.",
        ],
        "strengths": [
            "Standardises age-adjusted productivity.",
            "Easy to interpret around a threshold of 1.0.",
            "Useful for system-level comparison.",
        ],
        "limitations": [
            "Depends on the mean ANPS of the institutions included.",
            "May shift when the comparison set changes.",
            "Still does not include staff-size adjustment directly.",
        ],
        "note": (
            "Ranking is based on productivity relative to the system-wide average after "
            "adjusting for institutional age."
        ),
        "sort_desc": True,
        "table_columns": [
            "Institution",
            "Block",
            "ANOI (ANPS/Mean ANPS of all institutions)",
            "ANPS(Docs/Age)",
            "Age",
        ],
    },
    {
        "slug": "urpi",
        "title": "University Research Performance Index (URPI)",
        "sheet": "university",
        "column": "URPI",
        "display_name": "URPI",
        "meaning": (
            "University Research Performance Index is a composite indicator that summarises "
            "institutional research performance using a balanced combination of output, "
            "efficiency, and growth measures. It combines ANPS, RII, and RMF using a "
            "weighted formula. In simple terms, URPI gives a single score that reflects how "
            "well a university performs across multiple dimensions of research activity. "
            "Institutions with higher values tend to record stronger annual productivity, "
            "higher output per researcher, and better sustained momentum. This makes URPI "
            "useful when a broader summary measure is needed."
        ),
        "formula": "URPI = 0.4(ANPS) + 0.4(RII) + 0.2(RMF)",
        "usefulness": [
            "Combines multiple dimensions of research performance in one score.",
            "Reduces reliance on any single metric.",
            "Useful for summary institutional comparison.",
        ],
        "strengths": [
            "Balances output, efficiency, and momentum.",
            "Useful for rounded performance assessment.",
            "Helps simplify multi-metric interpretation.",
        ],
        "limitations": [
            "More complex than single indicators.",
            "Results depend on the selected weighting scheme.",
            "May hide the detail visible in separate metrics.",
        ],
        "note": (
            "Ranking is based on a composite index combining output, efficiency, and "
            "research momentum."
        ),
        "sort_desc": True,
        "table_columns": [
            "Institution",
            "Block",
            "URPI",
            "RII(Docs/authors)",
            "ANPS(Docs/Age)",
            "RMF(Docs/Age x Authors)",
        ],
    },
]

BLOCK_METRICS: List[Dict[str, Any]] = [
    {
        "slug": "bos",
        "title": "Block Output Share (BOS)",
        "sheet": "block",
        "column": "BOS(Block Share)",
        "display_name": "BOS",
        "meaning": (
            "Block Output Share measures the proportion of total research output contributed "
            "by each ownership category in South-South Nigeria. In this study, the blocks "
            "are federal, state, and private universities. The metric is calculated by "
            "dividing the total number of documents produced within a block by the total "
            "number of documents produced by all universities, then multiplying by 100. In "
            "simple terms, BOS shows how much each category of university contributes to the "
            "region's total publication output."
        ),
        "formula": "BOS = (Documents in Block / Total Documents) × 100",
        "usefulness": [
            "Shows the contribution of each ownership category to regional output.",
            "Useful for policy and system-level comparison.",
            "Helps identify where output is concentrated.",
        ],
        "strengths": [
            "Simple percentage-based measure.",
            "Useful for ownership-level analysis.",
            "Easy to explain to policy audiences.",
        ],
        "limitations": [
            "Does not compare individual universities directly.",
            "Can be driven by block size.",
            "Does not reflect efficiency or annual productivity.",
        ],
        "note": (
            "Values represent the share of total Scopus indexed documents contributed by each "
            "institutional block."
        ),
        "sort_desc": True,
        "table_columns": [
            "Block",
            "Number of Institutions",
            "Number of Documents",
            "Number of Authors",
            "BOS(Block Share)",
        ],
    },
    {
        "slug": "moi",
        "title": "Mean Output per Institution (MOI)",
        "sheet": "block",
        "column": "MOI (Block Documents/Number of Institutions in the block)",
        "display_name": "MOI",
        "meaning": (
            "Mean Output per Institution measures the average research output of universities "
            "within each ownership category in South-South Nigeria. It is calculated by "
            "dividing the total number of documents produced within a given block by the "
            "number of universities in that block. In simple terms, MOI shows how productive "
            "the average university is within each ownership group. This makes it useful for "
            "comparing the average institutional output of federal, state, and private "
            "universities."
        ),
        "formula": (
            "MOI = Number of Documents in the Block / Number of Institutions in the Block"
        ),
        "usefulness": [
            "Shows average institutional output within each ownership category.",
            "Helps distinguish block size from average university productivity.",
            "Useful for comparing ownership groups.",
        ],
        "strengths": [
            "Simple average that is easy to interpret.",
            "Useful for block-level comparison.",
            "Helps reduce the effect of unequal block sizes.",
        ],
        "limitations": [
            "Can hide differences between universities within the same block.",
            "Sensitive to extreme values in small blocks.",
            "Does not account for age or staff size.",
        ],
        "note": (
            "Values represent the average number of Scopus indexed documents produced per "
            "institution within each block."
        ),
        "sort_desc": True,
        "table_columns": [
            "Block",
            "Number of Institutions",
            "Number of Documents",
            "MOI (Block Documents/Number of Institutions in the block)",
        ],
    },
    {
        "slug": "bl-rii",
        "title": "Block-Level Research Intensity Index (BL-RII)",
        "sheet": "block",
        "column": "BL-RII",
        "display_name": "BL-RII",
        "meaning": (
            "Block-Level Research Intensity Index measures the average research output per "
            "researcher within each ownership category in South-South Nigeria. It is "
            "calculated by dividing the total number of documents produced by all "
            "universities in a given block by the total number of authors in that block. In "
            "simple terms, BL-RII shows how productive the average research-active staff "
            "member is within each ownership group. It is useful for judging whether "
            "differences in total output across blocks are linked more to staff size or to "
            "average researcher productivity."
        ),
        "formula": "BL-RII = Total Documents in a Block / Total Authors in the Block",
        "usefulness": [
            "Compares researcher-level productivity across ownership groups.",
            "Helps separate staff size from output efficiency.",
            "Useful for interpreting block differences in total output.",
        ],
        "strengths": [
            "Focuses on average productivity per researcher.",
            "Useful for comparing block-level efficiency.",
            "Easy to compute from block totals.",
        ],
        "limitations": [
            "Does not show variation between universities within a block.",
            "Does not account for age differences across institutions.",
            "Should be read alongside BOS and MOI.",
        ],
        "note": (
            "Values represent the average research output per author within each "
            "institutional block."
        ),
        "sort_desc": True,
        "table_columns": [
            "Block",
            "Number of Institutions",
            "Number of Documents",
            "Number of Authors",
            "BL-RII",
        ],
    },
]

ALL_METRICS = UNIVERSITY_METRICS + BLOCK_METRICS


def html_escape(value: Any) -> str:
    text = "" if value is None else str(value)
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def format_value(value: Any, column: str) -> str:
    if pd.isna(value):
        return "—"

    if column in {"Year established", "Age", "Number of Documents", "Number of Authors", "Number of Institutions"}:
        return f"{int(round(float(value))):,}"

    if column == "BOS(Block Share)":
        return f"{float(value):.2f}%"

    if column in {
        "RII(Docs/authors)",
        "RMF(Docs/Age x Authors)",
        "IRD(Authors/Age)",
        "ANOI (ANPS/Mean ANPS of all institutions)",
        "BL-RII",
    }:
        return f"{float(value):.3f}"

    if column in {
        "ANPS(Docs/Age)",
        "URPI",
        "MOI (Block Documents/Number of Institutions in the block)",
    }:
        return f"{float(value):.2f}"

    return html_escape(value)


def read_workbook() -> tuple[pd.DataFrame, pd.DataFrame]:
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Workbook not found: {DATA_FILE}")

    university_df = pd.read_excel(DATA_FILE, sheet_name=UNIVERSITY_SHEET)
    block_df = pd.read_excel(DATA_FILE, sheet_name=BLOCK_SHEET)

    university_df = university_df.dropna(subset=["Institution"]).copy()
    block_df = block_df.dropna(subset=["Block"]).copy()

    university_df["Institution"] = university_df["Institution"].astype(str).str.strip()
    university_df["Block"] = university_df["Block"].astype(str).str.strip()
    block_df["Block"] = block_df["Block"].astype(str).str.strip()

    return university_df, block_df


def add_ranks(
    df: pd.DataFrame,
    value_col: str,
    is_university: bool,
    descending: bool = True,
) -> pd.DataFrame:
    result = df.copy()
    ascending = not descending

    tie_col = "Institution" if is_university else "Block"
    result = result.sort_values(
        by=[value_col, tie_col],
        ascending=[ascending, True],
    ).reset_index(drop=True)

    result["Overall Rank"] = range(1, len(result) + 1)

    if is_university:
        result["Block Rank"] = (
            result.groupby("Block")[value_col]
            .rank(method="min", ascending=ascending)
            .astype(int)
        )

    return result


def build_table(df: pd.DataFrame, metric: Dict[str, Any]) -> str:
    if metric["sheet"] == "university":
        columns = ["Overall Rank", "Block Rank"] + metric["table_columns"]
    else:
        columns = ["Overall Rank"] + metric["table_columns"]

    header_html = "".join(
        f'<th style="text-align:left; white-space:nowrap;">{html_escape(col)}</th>'
        for col in columns
    )

    row_html_parts: List[str] = []
    for _, row in df.iterrows():
        cells = []
        for col in columns:
            cells.append(
                f'<td style="text-align:left; vertical-align:top;">{format_value(row[col], col)}</td>'
            )
        row_html_parts.append("<tr>" + "".join(cells) + "</tr>")

    return (
        '<div style="overflow-x:auto;">'
        '<table class="rankings-table" style="width:100%; border-collapse:collapse; table-layout:auto;">'
        f"<thead><tr>{header_html}</tr></thead>"
        f"<tbody>{''.join(row_html_parts)}</tbody>"
        "</table>"
        "</div>"
    )


def nav_links(current_index: int) -> str:
    left_html = ""
    right_html = ""

    if current_index > 0:
        prev_metric = ALL_METRICS[current_index - 1]
        left_html = (
            f'<a class="btn btn-ghost" href="{prev_metric["slug"]}.html">'
            f"← {html_escape(prev_metric['display_name'])}</a>"
        )

    if current_index < len(ALL_METRICS) - 1:
        next_metric = ALL_METRICS[current_index + 1]
        right_html = (
            f'<a class="btn btn-ghost" href="{next_metric["slug"]}.html">'
            f"{html_escape(next_metric['display_name'])} →</a>"
        )

    return (
        '<div class="card-actions" style="justify-content:space-between;">'
        f"<div>{left_html}</div>"
        f"<div>{right_html}</div>"
        "</div>"
    )


def site_header(active_page: str) -> str:
    rankings_active = " active" if active_page == "rankings" else ""

    return f"""
<a class="skip-link" href="#main-content">Skip to content</a>

<header class="site-header">
  <div class="container">
    <div class="header-inner">
      <div>
        <a class="brand-name" href="index.html">Valentine Owan</a>
        <div class="brand-tag">Research, statistics and academic scholarship</div>
      </div>

      <nav class="site-nav" aria-label="Main navigation">
        <a class="nav-link" href="index.html">Home</a>
        <a class="nav-link" href="about.html">About</a>
        <a class="nav-link" href="publications.html">Publications</a>
        <a class="nav-link{rankings_active}" href="south-south-rankings.html">Rankings</a>
        <a class="nav-link" href="contact.html">Contact</a>
      </nav>
    </div>
  </div>
</header>
"""


def site_footer() -> str:
    return """
<footer class="site-footer">
  <div class="container">
    <div class="footer-top">
      <div class="footer-copy">
        <span>&copy; 2026 Valentine Owan</span>
        <span class="footer-sep">•</span>
        <span>Academic rankings and research resources</span>
      </div>

      <div class="footer-links">
        <a href="index.html">Home</a>
        <a href="about.html">About</a>
        <a href="publications.html">Publications</a>
        <a href="south-south-rankings.html">Rankings</a>
      </div>
    </div>

    <div class="footer-note">
      Built for clear academic communication and public access to research information.
    </div>
  </div>
</footer>
"""


def page_shell(title: str, body: str, active_page: str = "rankings") -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html_escape(title)} | Valentine Owan</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  {site_header(active_page)}

  <main id="main-content">
    {body}
  </main>

  {site_footer()}
</body>
</html>
"""


def generate_metric_page(
    metric: Dict[str, Any],
    current_index: int,
    university_df: pd.DataFrame,
    block_df: pd.DataFrame,
) -> None:
    is_university = metric["sheet"] == "university"
    source_df = university_df if is_university else block_df

    ranked_df = add_ranks(
        df=source_df,
        value_col=metric["column"],
        is_university=is_university,
        descending=metric["sort_desc"],
    )

    table_html = build_table(ranked_df, metric)

    usefulness_html = "".join(
        f"<li>{html_escape(item)}</li>" for item in metric["usefulness"]
    )
    strengths_html = "".join(
        f"<li>{html_escape(item)}</li>" for item in metric["strengths"]
    )
    limitations_html = "".join(
        f"<li>{html_escape(item)}</li>" for item in metric["limitations"]
    )

    full_note = f"{metric['note']} {DATA_NOTE_SUFFIX}"

    body = f"""
<section class="hero">
  <div class="container narrow">
    <div class="card" style="background:linear-gradient(135deg, rgba(47,111,237,.10), rgba(15,118,110,.08), #ffffff); border:1px solid rgba(47,111,237,.16); box-shadow:var(--shadow-2, 0 14px 32px rgba(17,24,39,.10));">
      <a class="text-link" href="south-south-rankings.html">← Back to rankings overview</a>
      <div class="mt-12"></div>
      <span class="kicker">South-South Nigeria university rankings</span>
      <h1>{html_escape(metric["title"])}</h1>
      <p class="lead">{html_escape(metric["meaning"])}</p>
      <div class="callout">
        <div class="callout-title">Data note</div>
        <div class="callout-text">Verified Scopus records, accurate as of 12 pm, 9 February 2026.</div>
      </div>
    </div>
  </div>
</section>

<section class="section">
  <div class="container narrow">
    <div class="grid-2">
      <div class="card">
        <h2>Formula</h2>
        <p><strong>{html_escape(metric["formula"])}</strong></p>
      </div>

      <div class="card">
        <h2>Usefulness</h2>
        <ul class="clean-list">
          {usefulness_html}
        </ul>
      </div>

      <div class="card">
        <h2>Strengths</h2>
        <ul class="clean-list">
          {strengths_html}
        </ul>
      </div>

      <div class="card">
        <h2>Limitations</h2>
        <ul class="clean-list">
          {limitations_html}
        </ul>
      </div>
    </div>
  </div>
</section>

<section class="section alt">
  <div class="container">
    <div class="card">
      <h2>Ranking table</h2>
      {table_html}
      <p class="note mt-10" style="padding:10px 12px; background:rgba(17,24,39,.03); border:1px solid var(--line); border-radius:12px;">
        <strong>Note:</strong> {html_escape(full_note)}
      </p>
      <p class="note mt-10">{html_escape(THESIS_SOURCE_SHORT)}</p>
      {nav_links(current_index)}
    </div>
  </div>
</section>
"""

    output_file = ROOT / f'{metric["slug"]}.html'
    output_file.write_text(
        page_shell(metric["title"], body, active_page="rankings"),
        encoding="utf-8",
    )
    print(f"Generated {output_file.name}")


def generate_index_page() -> None:
    card_html_parts: List[str] = []

    for metric in ALL_METRICS:
        short_meaning = metric["meaning"]
        if len(short_meaning) > 200:
            short_meaning = short_meaning[:200].rsplit(" ", 1)[0] + "..."

        card_html_parts.append(
            f"""
<div class="card">
  <h2>{html_escape(metric["title"])}</h2>
  <p>{html_escape(short_meaning)}</p>
  <div class="card-actions">
    <a class="btn" href="{metric["slug"]}.html">View metric</a>
  </div>
</div>
"""
        )

    body = f"""
<section class="hero">
  <div class="container narrow">
    <div class="card" style="background:linear-gradient(135deg, rgba(47,111,237,.10), rgba(15,118,110,.08), #ffffff); border:1px solid rgba(47,111,237,.16); box-shadow:var(--shadow-2, 0 14px 32px rgba(17,24,39,.10));">
      <span class="kicker">Bibliometric ranking system</span>
      <h1>South-South Nigeria university rankings</h1>
      <div class="lead">
        <p>
          This page presents a set of bibliometric indicators developed to compare
          universities in South-South Nigeria using verified Scopus data.
        </p>
        <p>
          The metrics cover institutional output, staff participation, research efficiency,
          age-adjusted productivity, growth patterns, ownership-level contribution, and
          composite performance.
        </p>
      </div>
      <div class="callout">
        <div class="callout-title">Data note</div>
        <div class="callout-text">Verified Scopus records, accurate as of 12 pm, 9 February 2026.</div>
      </div>
    </div>
  </div>
</section>

<section class="section">
  <div class="container narrow">
    <div class="card">
      <h2>Source and methodology</h2>
      <p>{THESIS_SOURCE_LONG}</p>
    </div>
  </div>
</section>

<section class="section">
  <div class="container narrow">
    <div class="card">
      <h2>About the metric pages</h2>
      <p>
        The ranking framework includes eight university-level indicators and three
        block-level indicators. Each metric page gives a clear explanation of what the
        measure means, how it is calculated, why it is useful, its main strengths and
        limitations, and the ranking table generated from the workbook.
      </p>
    </div>
  </div>
</section>

<section class="section alt">
  <div class="container">
    <h2 class="section-title">Metric pages</h2>
    <p class="section-kicker">Open any metric below to read the explanation and view the ranking table.</p>
    <div class="grid-3">
      {''.join(card_html_parts)}
    </div>
  </div>
</section>
"""

    MAIN_PAGE.write_text(
        page_shell("South-South Nigeria university rankings", body, active_page="rankings"),
        encoding="utf-8",
    )
    print(f"Generated {MAIN_PAGE.name}")


def main() -> None:
    university_df, block_df = read_workbook()
    generate_index_page()

    for idx, metric in enumerate(ALL_METRICS):
        generate_metric_page(metric, idx, university_df, block_df)

    print("Done.")


if __name__ == "__main__":
    main()
