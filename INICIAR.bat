@echo off
title Sistema de Inventario
color 0A

echo ========================================
echo   SISTEMA DE INVENTARIO PROFESIONAL
echo ========================================
echo.
echo Iniciando aplicacion...
echo.

cd /d "%~dp0"
python main.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: No se pudo iniciar la aplicacion
    echo Verifica que Python este instalado correctamente
    echo.
    pause
) else (
    exit
)
