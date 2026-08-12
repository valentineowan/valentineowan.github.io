@echo off
setlocal
cd /d "%~dp0.."

title Valentine Owan Website Update

echo.
echo ========================================================
echo        VALENTINE OWAN WEBSITE UPDATE
echo ========================================================
echo Project: %CD%
echo ========================================================
echo.

REM --------------------------------------------------------
REM 1. Check that the project structure exists
REM --------------------------------------------------------
if not exist "data\publications.xlsx" goto :missing_project
if not exist "scripts\sync_openalex_publications.py" if not exist "scripts\openalex_author_sync.py" goto :missing_script
if not exist "scripts\generate_individual_publication_pages.py" goto :missing_script
if not exist "scripts\generate_publications_index.py" goto :missing_script
if not exist "scripts\generate_south_south_rankings.py" goto :missing_script
if not exist "scripts\generate_sitemap.py" goto :missing_script

REM --------------------------------------------------------
REM 2. Show Git status BEFORE the update
REM --------------------------------------------------------
echo [1/7] Checking current Git status...
echo --------------------------------------------------------
git status --short
if errorlevel 1 (
    echo WARNING: Git is not available or this folder is not a Git repository.
    echo The website generators can still run, but Git status will not be checked.
)
echo.

REM --------------------------------------------------------
REM 3. Sync OpenAlex data
REM --------------------------------------------------------
echo [2/7] Updating OpenAlex citation data...
echo --------------------------------------------------------

if exist "scripts\sync_openalex_publications.py" (
    python "scripts\sync_openalex_publications.py"
) else (
    python "scripts\openalex_author_sync.py"
)

if errorlevel 1 goto :error
echo.

REM --------------------------------------------------------
REM 4. Validate + generate individual publication pages
REM --------------------------------------------------------
echo [3/7] Validating and generating individual publication pages...
echo --------------------------------------------------------
python "scripts\generate_individual_publication_pages.py"
if errorlevel 1 goto :error
echo.

REM --------------------------------------------------------
REM 5. Generate publications index
REM --------------------------------------------------------
echo [4/7] Generating publications index...
echo --------------------------------------------------------
python "scripts\generate_publications_index.py"
if errorlevel 1 goto :error
echo.

REM --------------------------------------------------------
REM 6. Generate rankings and sitemap
REM --------------------------------------------------------
echo [5/7] Generating South-South rankings...
echo --------------------------------------------------------
python "scripts\generate_south_south_rankings.py"
if errorlevel 1 goto :error
echo.

echo [6/7] Generating sitemap...
echo --------------------------------------------------------
python "scripts\generate_sitemap.py"
if errorlevel 1 goto :error
echo.

REM --------------------------------------------------------
REM 7. Show exactly what changed
REM --------------------------------------------------------
echo [7/7] Checking what changed...
echo --------------------------------------------------------
echo.
echo Git changes after update:
echo --------------------------------------------------------
git status --short
echo --------------------------------------------------------
echo.

echo Detailed changed-file summary:
echo --------------------------------------------------------
git diff --stat
echo --------------------------------------------------------
echo.

echo ========================================================
echo        WEBSITE UPDATE COMPLETED SUCCESSFULLY
echo ========================================================
echo.
echo No Git commit or push has been performed.
echo.
echo Review the changed files, test the website, then:
echo.
echo     git add .
echo     git commit -m "Update site"
echo     git push
echo.
echo ========================================================
pause
exit /b 0

:missing_project
echo.
echo ========================================================
echo ERROR: This does not appear to be the Git project folder.
echo Expected:
echo   %CD%\data\publications.xlsx
echo.
echo The script has stopped without changing the website.
echo ========================================================
pause
exit /b 1

:missing_script
echo.
echo ========================================================
echo ERROR: One or more required scripts were not found.
echo.
echo Check the scripts folder and make sure the current
echo script names are:
echo   generate_individual_publication_pages.py
echo   generate_publications_index.py
echo   generate_south_south_rankings.py
echo   generate_sitemap.py
echo   sync_openalex_publications.py
echo       OR openalex_author_sync.py
echo.
echo No further website update was performed.
echo ========================================================
pause
exit /b 1

:error
echo.
echo ========================================================
echo        WEBSITE UPDATE STOPPED
echo ========================================================
echo An error occurred in the step shown immediately above.
echo No Git commit or push has been performed.
echo.
echo Check the error message, correct the problem, and run
echo this update script again.
echo ========================================================
pause
exit /b 1
