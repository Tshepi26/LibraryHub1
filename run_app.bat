@echo off
setlocal
cd /d "%~dp0"
echo ============================================
echo   LibraryHub - start the system
echo ============================================
where python >nul 2>nul
if errorlevel 1 (
  echo Python was not found. Install Python from python.org and tick "Add Python to PATH", then run this file again.
  pause
  exit /b 1
)
echo Installing the libraries the system needs ^(first time only^)...
python -m pip install -r requirements.txt
if errorlevel 1 (
  echo Could not install the libraries. Check your internet connection.
  pause
  exit /b 1
)
set "LIBRARY_DB_USER=root"
set /p LIBRARY_DB_USER=MySQL username [press Enter for root]: 
if "%LIBRARY_DB_USER%"=="" set "LIBRARY_DB_USER=root"
set /p LIBRARY_DB_PASSWORD=MySQL password: 
rem Let the Backup page find the MySQL tools automatically
for /d %%D in ("C:\Program Files\MySQL\MySQL Server *") do if exist "%%D\bin\mysqldump.exe" (
  set "MYSQLDUMP_PATH=%%D\bin\mysqldump.exe"
  set "MYSQL_PATH=%%D\bin\mysql.exe"
)
echo.
echo Starting... open http://localhost:5000 in your browser.
echo Keep this window open while you use the system. Press Ctrl+C to stop.
start "" http://localhost:5000
python app.py
pause
