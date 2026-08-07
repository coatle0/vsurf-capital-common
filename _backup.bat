@echo off
set "SOURCE=C:\lab\vsurf_capital\common"
set "DEST=G:\내 드라이브\vsurf_capital\_common"
set "LOG=%SOURCE%\backup_log.txt"
set "TIMESTAMP=%date% %time%"
if not exist "%SOURCE%" (echo [ERROR] SOURCE not found & exit /b 1)
if not exist "%DEST%" (echo [ERROR] Drive not mounted - check Google Drive Desktop & exit /b 1)
echo [%TIMESTAMP%] Backup started >> "%LOG%"
xcopy "%SOURCE%\*.md" "%DEST%\" /Y /D >nul
if errorlevel 1 (echo [%TIMESTAMP%] xcopy FAILED >> "%LOG%" & echo [ERROR] xcopy failed & exit /b 1)
echo [%TIMESTAMP%] Backup OK >> "%LOG%"
echo [OK] Backup completed
if exist "%SOURCE%\.git" (cd /d "%SOURCE%" & git add *.md >nul 2>&1 & git commit -m "auto-backup %TIMESTAMP%" >nul 2>&1)
exit /b 0
