@echo off
title KHOI PHUC SHADER MAC DINH MINI WORLD
color 0E
chcp 65001 >nul
cls

echo ======================================================================
echo           KHOI PHUC SHADER GOC VE BAN DAU (DEFAULT SHADERS)
echo ======================================================================
echo.

copy /Y "C:\Users\Le Minh\AppData\Roaming\miniworddata410\pkg_assets\dx_res.pkg.original_backup" "C:\Users\Le Minh\AppData\Roaming\miniworddata410\pkg_assets\dx_res.pkg"
python "%~dp0build_ultra_shaders.py" restore

echo.
echo [V] Da khoi phuc toan bo Shader va file dx_res.pkg ve mac dinh thanh cong!
pause
