@echo off
setlocal
cd /d "%~dp0"
echo ============================================
echo   LibraryHub - create the database
echo ============================================
echo.
set "MYSQL_EXE="
for /d %%D in ("C:\Program Files\MySQL\MySQL Server *") do if exist "%%D\bin\mysql.exe" set "MYSQL_EXE=%%D\bin\mysql.exe"
if not defined MYSQL_EXE if exist "C:\xampp\mysql\bin\mysql.exe" set "MYSQL_EXE=C:\xampp\mysql\bin\mysql.exe"
if not defined MYSQL_EXE where mysql >nul 2>nul && set "MYSQL_EXE=mysql"
if not defined MYSQL_EXE (
  echo Could not find mysql.exe automatically.
  echo Look in C:\Program Files\MySQL\MySQL Server 8.0\bin and paste the full path to mysql.exe below.
  set /p MYSQL_EXE=Path to mysql.exe: 
)
set "DBUSER=root"
set /p DBUSER=MySQL username [press Enter for root]: 
if "%DBUSER%"=="" set "DBUSER=root"
echo.
echo Type your MySQL password when asked (nothing shows while you type), then press Enter.
"%MYSQL_EXE%" -u %DBUSER% -p < database\02_COMPLETE_database_with_sample_data.sql
if errorlevel 1 (
  echo.
  echo SOMETHING WENT WRONG. Check the message above. Common causes:
  echo   - wrong MySQL password
  echo   - the MySQL service is not running ^(Win+R, type services.msc, start MySQL80^)
  echo   - mysql.exe path is wrong
  echo You can also open database\02_COMPLETE_database_with_sample_data.sql in MySQL Workbench and run it there.
  pause
  exit /b 1
)
echo.
echo SUCCESS: database "library_management_db" is ready.
echo Next step: double-click run_app.bat
pause
