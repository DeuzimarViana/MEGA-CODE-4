@echo off
setlocal
title MEGA-CODE-4 Portable

rem ============================================================
rem MEGA-CODE-4 - launcher Windows
rem Delega para tools\launch.py (mesma logica do start.sh):
rem   * redireciona HOME/APPDATA/XDG_* para data\
rem   * credenciais cifradas, senha e chave lidas sem eco
rem   * devolve o codigo de saida do engine
rem Requer Python 3 e o pacote "cryptography" (pip install cryptography).
rem ============================================================

set "ROOT_DIR=%~dp0"
set "LAUNCHER=%ROOT_DIR%tools\launch.py"

if not exist "%LAUNCHER%" (
    echo [ERROR] Nao encontrei %LAUNCHER%
    pause
    exit /b 1
)

set "PYTHON_CMD="
py -3 --version >nul 2>nul && set "PYTHON_CMD=py -3"
if not defined PYTHON_CMD python --version >nul 2>nul && set "PYTHON_CMD=python"
if not defined PYTHON_CMD (
    echo [ERROR] Python 3 nao encontrado. Instale em https://www.python.org/downloads/
    pause
    exit /b 1
)

%PYTHON_CMD% "%LAUNCHER%" %*
set "STATUS=%ERRORLEVEL%"

if not "%STATUS%"=="0" (
    echo.
    echo   Codigo de saida: %STATUS%
    pause
)
exit /b %STATUS%
