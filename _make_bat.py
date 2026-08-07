import os

bat_content = '@echo off\r\n'
bat_content += 'set "SOURCE=C:\\lab\\vsurf_capital\\common"\r\n'
bat_content += 'set "DEST=G:\\내 드라이브\\vsurf_capital\\_common"\r\n'
bat_content += 'set "LOG=%SOURCE%\\backup_log.txt"\r\n'
bat_content += 'set "TIMESTAMP=%date% %time%"\r\n'
bat_content += 'if not exist "%SOURCE%" (echo [ERROR] SOURCE not found & exit /b 1)\r\n'
bat_content += 'if not exist "%DEST%" (echo [ERROR] Drive not mounted - check Google Drive Desktop & exit /b 1)\r\n'
bat_content += 'echo [%TIMESTAMP%] Backup started >> "%LOG%"\r\n'
bat_content += 'xcopy "%SOURCE%\\*.md" "%DEST%\\" /Y /D >nul\r\n'
bat_content += 'if errorlevel 1 (echo [%TIMESTAMP%] xcopy FAILED >> "%LOG%" & echo [ERROR] xcopy failed & exit /b 1)\r\n'
bat_content += 'echo [%TIMESTAMP%] Backup OK >> "%LOG%"\r\n'
bat_content += 'echo [OK] Backup completed\r\n'
bat_content += 'if exist "%SOURCE%\\.git" (cd /d "%SOURCE%" & git add *.md >nul 2>&1 & git commit -m "auto-backup %TIMESTAMP%" >nul 2>&1)\r\n'
bat_content += 'exit /b 0\r\n'

bat_path = r'C:\lab\vsurf_capital\common\_backup.bat'
with open(bat_path, 'w', encoding='cp949') as f:
    f.write(bat_content)

print(f'OK: {bat_path}')
print(f'Size: {os.path.getsize(bat_path)} bytes')
