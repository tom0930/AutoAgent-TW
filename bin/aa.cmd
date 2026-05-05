@echo off
SETLOCAL EnableDelayedExpansion

:: AutoAgent-TW Global CLI Wrapper
:: Resolves AA_CORE to the parent directory of this bin script.
SET "BIN_DIR=%~dp0"
:: Remove trailing slash if present
IF "%BIN_DIR:~-1%"=="\" SET "BIN_DIR=%BIN_DIR:~0,-1%"
FOR %%I IN ("%BIN_DIR%\..") DO SET "AA_CORE=%%~fI"

:: Set environment variables
SET "PYTHONPATH=%AA_CORE%"

:: Check for virtual environment
SET "PYTHON_EXE=%AA_CORE%\venv\Scripts\python.exe"
IF NOT EXIST "%PYTHON_EXE%" (
    SET "PYTHON_EXE=python"
)

:: Execute the CLI router
"%PYTHON_EXE%" "%AA_CORE%\scripts\aa_cli.py" %*

ENDLOCAL
