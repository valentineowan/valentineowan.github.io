#!/usr/bin/env python3
"""Idempotently ensure the Educational Projects link survives site generation.

Patches only the primary navigation in root-level HTML pages and generated
publication detail pages. It does not replace headers, footers, page content,
styles, or active-page classes.
"""
from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
NAV_ID = 'site-nav'
LINK_LABEL = 'Educational Projects'


def relative_href(page: Path) -> str:
    return 'research-projects.html' if page.parent == ROOT else '../research-projects.html'


def ensure_link(page: Path) -> bool:
    original = page.read_text(encoding='utf-8')
    updated = original
    pattern = re.compile(r'(<nav\b[^>]*\bid=["\']site-nav["\'][^>]*>)(.*?)(</nav>)', re.I | re.S)
    match = pattern.search(updated)
    if not match:
        return False

    nav = match.group(2)
    href = relative_href(page)
    # Remove duplicate Educational Projects links in this primary navigation,
    # then insert exactly one after Publications while preserving all other links.
    link_pattern = re.compile(r'<a\b(?=[^>]*\bhref=["\'][^"\']*research-projects\.html["\'])[^>]*>\s*Educational Projects\s*</a>', re.I)
    nav_clean = link_pattern.sub('', nav)
    if 'href="publications.html"' in nav_clean or "href='../publications.html'" in nav_clean or 'href="../publications.html"' in nav_clean:
        pub_pattern = re.compile(r'(<a\b(?=[^>]*\bhref=["\'][^"\']*publications\.html["\'])[^>]*>\s*Publications\s*</a>)', re.I)
        link = f'<a class="nav-link" href="{href}">{LINK_LABEL}</a>'
        nav_new, count = pub_pattern.subn(r'\1' + '\n        ' + link, nav_clean, count=1)
        if count == 0:
            nav_new = nav_clean.rstrip() + '\n        ' + link + '\n      '
    else:
        link = f'<a class="nav-link" href="{href}">{LINK_LABEL}</a>'
        nav_new = nav_clean.rstrip() + '\n        ' + link + '\n      '

    updated = updated[:match.start(2)] + nav_new + updated[match.end(2):]
    if updated != original:
        page.write_text(updated, encoding='utf-8')
        return True
    return False


def main() -> int:
    candidates = set(ROOT.glob('*.html'))
    publication_dir = ROOT / 'publications'
    if publication_dir.exists():
        candidates.update(publication_dir.glob('*.html'))
    project_dir = ROOT / 'individual-projects'
    if project_dir.exists():
        candidates.update(project_dir.glob('*.html'))
    changed = 0
    checked = 0
    for page in sorted(candidates):
        if page.name == 'research-projects.html':
            continue
        checked += 1
        if ensure_link(page):
            changed += 1
    print(f'Navigation check complete: {checked} pages checked; {changed} updated.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
