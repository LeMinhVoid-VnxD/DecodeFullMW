@echo off
title TRA CUU THONG TIN NGUOI CHOI MINI WORLD SIEU NHANH
color 0B
chcp 65001 >nul
cls

echo ======================================================================
echo          CONG CU TRA CUU THONG TIN NGUOI CHOI MINI WORLD SIEU NHANH
echo ======================================================================
echo.

if "%~1"=="" goto LOOP

python "%~dp0lookup_player.py" "%~1"
pause
goto END

:LOOP
python "%~dp0lookup_player.py"
echo.
echo Cam on ban da su dung!
pause

:END
