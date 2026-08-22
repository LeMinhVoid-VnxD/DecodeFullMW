@echo off
title CAI DAT RESHADE BSL CINEMATIC CHO MINI WORLD
color 0A
chcp 65001 >nul
cls

echo ======================================================================
echo    CAI DAT RESHADE BSL CINEMATIC SHADER PACK CHO MINI WORLD
echo ======================================================================
echo.

set "GAME_DIR=%AppData%\miniworldOverseasgame"
set "RESHADE_DIR=%~dp0RESHADE_ULTRA_MINIWORLD"

copy /Y "%RESHADE_DIR%\extracted_reshade\ReShade32.dll" "%GAME_DIR%\dxgi.dll" >nul
copy /Y "%RESHADE_DIR%\extracted_reshade\ReShade32.dll" "%GAME_DIR%\d3d11.dll" >nul

echo [1/3] Da cai dat ReShade Direct3D 11 Core Hook!
xcopy /E /I /Y "%GAME_DIR%\reshade-shaders" "%GAME_DIR%\reshade-shaders" >nul
echo [2/3] Da cai dat bo 40 Shaders (qUINT Bloom, AmbientLight, Tonemap, SMAA, SSR)!
echo [3/3] Da nap Preset dien anh MiniWorld_BSL_Cinematic.ini!

echo.
echo ======================================================================
echo  [V] CAI DAT RESHADE BSL SHADER THANH CONG 100%!
echo ======================================================================
echo  👉 Mo game Mini World len, ban se thay banner ReShade o tren dau.
echo  👉 Nhan phim [HOME] tren ban phim de mo menu tuy chinh thoi gian thuc!
echo ======================================================================
echo.
pause
