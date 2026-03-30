OPENALEX AUTHOR SYNC — QUICK START

1) Install required packages
   Run:
   python -m pip install pandas openpyxl requests

2) Save the script in the clean website folder
   Save it here:
   D:\Documents\E-library\Vowan_Database\Valentine_Site_Clean\scripts\openalex_author_sync.py

3) Confirm the script uses the clean site paths automatically
   The script should not contain any hard-coded path to:
   D:\Documents\E-library\Vowan_Database\Valentine_Site

   Instead, it should use:

   ROOT = Path(__file__).resolve().parents[1]
   DATA_DIR = ROOT / "data"

   EXCEL_FILE = DATA_DIR / "publications.xlsx"
   BACKUP_FILE = DATA_DIR / "publications.backup.before_openalex.xlsx"
   CACHE_FILE = DATA_DIR / "openalex_author_works_cache.json"

4) Confirm the OpenAlex author ID
   Check that the script contains:
   OPENALEX_AUTHOR_ID = "A5058462199"

5) Optional
   Add your email address to the script for polite API requests:
   POLITE_EMAIL = "your_email@example.com"

6) Run the script
   Open Command Prompt and run:

   cd /d D:\Documents\E-library\Vowan_Database\Valentine_Site_Clean
   python scripts\openalex_author_sync.py

WHAT THE SCRIPT DOES

- Fetches all works from the OpenAlex author profile
- Saves a JSON cache of the fetched records
- Matches Excel records using DOI first
- Uses title similarity where DOI is missing or unmatched
- Updates publications.xlsx with OpenAlex metadata

COLUMNS ADDED OR UPDATED IN publications.xlsx

- openalex_id
- openalex_url
- openalex_citations
- openalex_publication_year
- openalex_publication_date
- openalex_source_title
- openalex_type
- openalex_pdf_url
- openalex_last_checked
- openalex_status
- openalex_match_method

IMPORTANT

- Use only the clean site folder:
  D:\Documents\E-library\Vowan_Database\Valentine_Site_Clean

- Do not use the old folder again:
  D:\Documents\E-library\Vowan_Database\Valentine_Site

- Make sure Excel is closed before running the script

NEXT STEP AFTER RUNNING

- Ensure the publication page generator reads openalex_citations
- Show the OpenAlex citation badge only when a citation value exists
- Run the full website update pipeline after the sync completes