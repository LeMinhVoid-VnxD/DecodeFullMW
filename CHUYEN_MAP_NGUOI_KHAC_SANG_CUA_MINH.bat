@echo off
title CHUYEN MAP NGUOI KHAC THANH MAP LOCAL EDIT CUA MINH
color 0A
chcp 65001 >nul
cls

echo ======================================================================
echo    CONG CU CHUYEN MAP NGUOI KHAC THANH MAP LOCAL EDIT CUA BAN
echo ======================================================================
echo.

if "%~1"=="" goto MENU

python "%~dp0clone_and_unlock_map.py" "%~1"
pause
goto END

:MENU
python "%~dp0clone_and_unlock_map.py"

:END
