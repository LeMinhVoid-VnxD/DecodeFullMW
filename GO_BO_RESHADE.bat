@echo off
title GO BO RESHADE MINI WORLD
color 0E
chcp 65001 >nul
cls

echo ======================================================================
echo                 GO BO RESHADE VE MAC DINH
echo ======================================================================
echo.

set "GAME_DIR=%AppData%\miniworldOverseasgame"
if exist "%GAME_DIR%\dxgi.dll" del /f /q "%GAME_DIR%\dxgi.dll"
if exist "%GAME_DIR%\d3d11.dll" del /f /q "%GAME_DIR%\d3d11.dll"

echo [V] Da go bo ReShade khoi game Mini World thanh cong!
pause
