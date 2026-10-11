@echo off

setlocal

cd /d "%~dp0.."



echo ========================================================

echo RECENT PUBLICATIONS UPDATE TEST

echo ========================================================

if not exist "data\publications.xlsx" (

    echo ERROR: data\publications.xlsx was not found.

    pause

    exit /b 1

)

if not exist "index.html" (

    echo ERROR: index.html was not found.

    pause

    exit /b 1

)

if not exist "publications.html" (

    echo ERROR: publications.html was not found.

    pause

    exit /b 1

)



echo.

echo [1/2] Rebuilding publication archive...

python "scripts\generate_publications_index.py"

if errorlevel 1 goto :error



echo.

echo [2/2] Writing Excel rows 2-6 to homepage and publications page...

python "scripts\generate_five_recent_publications_lists.py"

if errorlevel 1 goto :error



echo.

echo SUCCESS: The five records in Excel worksheet rows 2-6 have been written.

echo Check the printed titles above, then inspect index.html and publications.html.

echo This batch does not push files to the live website.

pause

exit /b 0



:error

echo.

echo ERROR: Update stopped. Read the Python error above.

pause

exit /b 1

