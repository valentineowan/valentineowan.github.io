from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML_FILE = ROOT / "publications.html"

html = HTML_FILE.read_text(encoding="utf-8")

# Replace button text
html = html.replace("Read article", "View details")

HTML_FILE.write_text(html, encoding="utf-8")

print("Button text updated to 'View details'")