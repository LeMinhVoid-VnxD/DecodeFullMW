@echo off
title KHOI PHUC SHADER MAC DINH MINI WORLD
color 0E
chcp 65001 >nul
cls

echo ======================================================================
echo           KHOI PHUC SHADER GOC VE BAN DAU (DEFAULT SHADERS)
echo ======================================================================
echo.

python "%~dp0build_ultra_shaders.py" restore
pause
