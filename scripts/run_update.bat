@echo off
cd /d D:\Documents\E-library\Vowan_Database\Valentine_Site

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
echo Generating sitemap...
echo ========================================
python scripts\generate_sitemap.py
if errorlevel 1 goto :error

echo.
echo ========================================
echo All updates completed successfully.
echo ========================================
pause
exit /b 0

:error
echo.
echo ========================================
echo Update stopped because of an error.
echo Check the message above.
echo ========================================
pause
exit /b 1