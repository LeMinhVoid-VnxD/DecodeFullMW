@echo off
title Minecraft (.mca) to Mini World (.r) Converter
cd /d "%~dp0"

echo ========================================================
echo   MINECRAFT (.MCA) -^> MINI WORLD (.R) MAP CONVERTER
echo ========================================================
echo.

if exist "%~dp0MC_to_MiniWorld_Converter.exe" (
    if "%~1"=="" (
        "%~dp0MC_to_MiniWorld_Converter.exe"
    ) else (
        "%~dp0MC_to_MiniWorld_Converter.exe" %*
    )
    goto end
)

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [!] May chua cai dat Python!
    echo Vui long cai dat Python hoac su dung file .EXE di kem.
    pause
    exit /b
)

if "%~1"=="" (
    python "%~dp0mc2mw_gui.py"
) else (
    python "%~dp0converter_core.py" %*
)

:end
