@echo off
cd /d D:\Documents\E-library\Vowan_Database\Valentine_Site_Git

echo ========================================================
echo        VALENTINE OWAN WEBSITE UPDATE
echo ========================================================
echo Project: D:\Documents\E-library\Vowan_Database\Valentine_Site_Git
echo ========================================================

echo.
echo [1/8] Updating OpenAlex citation data...
echo --------------------------------------------------------
python scripts\openalex_author_sync.py
if errorlevel 1 goto :error

echo.
echo [2/8] Validating and generating individual publication pages...
echo --------------------------------------------------------
python scripts\generate_individual_publication_pages.py
if errorlevel 1 goto :error

echo.
echo [3/8] Generating Books catalogue...
echo --------------------------------------------------------
python scripts\generate_books_catalog.py
if errorlevel 1 goto :error

echo.
echo [4/8] Generating publications index...
echo --------------------------------------------------------
python scripts\generate_publications_index.py
if errorlevel 1 goto :error

echo.
echo [5/8] Generating South-South rankings...
echo --------------------------------------------------------
python scripts\generate_south_south_rankings.py
if errorlevel 1 goto :error

echo.
echo [6/8] Generating sitemap...
echo --------------------------------------------------------
python scripts\generate_sitemap.py
if errorlevel 1 goto :error

echo.
echo [7/8] Final site update check...
echo --------------------------------------------------------
git status --short

echo.
echo [8/8] Update completed. No Git commit or push is performed automatically.
echo --------------------------------------------------------
echo Next steps:
echo 1. Inspect the generated pages and books.html.
echo 2. If everything is correct, run:
echo    git add .
echo    git commit -m "Update publications and books"
echo    git push
echo ========================================================
pause
exit /b 0

:error
echo.
echo ========================================================
echo UPDATE STOPPED BECAUSE OF AN ERROR
echo ========================================================
echo Check the message above.
echo Make sure Excel is closed and Python is available.
pause
exit /b 1
