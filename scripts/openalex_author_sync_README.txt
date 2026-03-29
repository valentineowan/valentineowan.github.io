OPENALEX AUTHOR SYNC — QUICK START

1) Install packages:
   python -m pip install pandas openpyxl requests

2) Save the script into your project, for example:
   D:\Documents\E-library\Vowan_Database\Valentine_Site\scripts\openalex_author_sync.py

3) Open the script and confirm:
   - EXCEL_FILE
   - BACKUP_FILE
   - CACHE_FILE
   - OPENALEX_AUTHOR_ID = "A5058462199"

4) Optional:
   Add your email to POLITE_EMAIL in the script.

5) Run:
   cd /d D:\Documents\E-library\Vowan_Database\Valentine_Site
   python scripts\openalex_author_sync.py

WHAT IT DOES
- Pulls all works from your OpenAlex author profile
- Saves a JSON cache of those works
- Matches your Excel records by DOI first, then by title similarity
- Adds / updates these columns in publications.xlsx:
  openalex_id
  openalex_url
  openalex_citations
  openalex_publication_year
  openalex_publication_date
  openalex_source_title
  openalex_type
  openalex_pdf_url
  openalex_last_checked
  openalex_status
  openalex_match_method

NEXT STEP AFTER THIS
- Update your publication page generator so it reads openalex_citations
- Display the citation badge only when a value exists
