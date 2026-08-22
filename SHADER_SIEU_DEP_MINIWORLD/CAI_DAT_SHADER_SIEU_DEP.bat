@echo off
title CAI DAT GOI SHADER ULTRA RTX V2.0 CHO MINI WORLD
color 0B
chcp 65001 >nul
cls

echo ======================================================================
echo     CAI DAT GOI SHADER ULTRA RTX V2.0 TRUC TIEP VAO GAME MINI WORLD
echo ======================================================================
echo.

python "%~dp0build_ultra_shaders.py"
python "%~dp0repack_dx_res_with_ultra_shaders.py"
pause
