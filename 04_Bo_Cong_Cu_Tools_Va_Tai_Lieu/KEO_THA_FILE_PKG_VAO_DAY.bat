@echo off
title Mini World PKG Extractor
cd /d "%~dp0"

echo ========================================================
echo         MINI WORLD .PKG EXTRACTOR AUTO-RUNNER
echo ========================================================
echo.

REM Uu tien chay file EXE doc lap (khong can cai dat Python)
if exist "%~dp0MiniWorld_PkgExtractor.exe" (
    "%~dp0MiniWorld_PkgExtractor.exe" %*
    goto end
)

REM Neu khong co file EXE, su dung Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [!] May chua cai dat Python va khong tim thay MiniWorld_PkgExtractor.exe!
    echo Vui long cai dat Python tai https://www.python.org/
    pause
    exit /b
)

python -c "import lz4.block" >nul 2>nul
if %errorlevel% neq 0 (
    echo [*] Dang tu dong cai dat thu vien lz4...
    pip install lz4
)

python "%~dp0extract_all_pkg.py" %*

:end
echo.
pause
