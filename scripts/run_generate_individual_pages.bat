@echo off
cd /d "%~dp0.."
python scripts\generate_individual_publication_pages.py
echo.
echo ========================================
echo Generation finished.
echo ========================================
pause