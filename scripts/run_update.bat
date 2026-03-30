@echo off
cd /d D:\Documents\E-library\Vowan_Database\Valentine_Site_Clean

echo ========================================
echo Updating OpenAlex citation data...
echo ========================================
python scripts\openalex_author_sync.py
if errorlevel 1 goto :error

echo.
echo ========================================
echo Generating individual publication pages...
echo ========================================
python scripts\generate_publication_pages.py
if errorlevel 1 goto :error

echo.
echo ========================================
echo Generating publications index page...
echo ========================================
python scripts\generate_publications_index.py
if errorlevel 1 goto :error

echo.
echo ========================================
echo Generating South-South rankings pages...
echo ========================================
python scripts\generate_south_south_rankings.py
if errorlevel 1 goto :error

echo.
echo ========================================
echo Generating sitemap...
echo ========================================
python scripts\generate_sitemap.py
if errorlevel 1 goto :error

echo.
echo ========================================
echo All updates completed successfully.
echo ========================================
echo.
echo Next steps:
echo 1. Close Excel before Git commands
echo 2. Review changed HTML pages
echo 3. Run: git add .
echo 4. Run: git commit -m "Update site"
echo 5. Run: git push
echo ========================================
pause
exit /b 0

:error
echo.
echo ========================================
echo Update stopped because of an error.
echo Check the message above.
echo Make sure:
echo - Excel is closed
echo - The workbook path is correct
echo - Python is available in PATH
echo ========================================
pause
exit /b 1