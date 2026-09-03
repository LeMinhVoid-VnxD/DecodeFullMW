@echo off
title CHUYEN QUYEN SO HUU MAP MINI WORLD
color 0E
chcp 65001 >nul
cls

echo ======================================================================
echo    CONG CU CHUYEN QUYEN SO HUU MAP MINI WORLD - NHAP PATH HOAC KEO THA
echo ======================================================================
echo.

if "%~1"=="" goto PROMPT

python "%~dp0transfer_map_ownership.py" "%~1"
pause
goto END

:PROMPT
python "%~dp0transfer_map_ownership.py"
pause

:END
