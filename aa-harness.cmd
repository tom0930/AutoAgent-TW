@echo off
REM AI Harness CLI Wrapper
REM 將 aa-harness 命令添加到 PATH

setlocal

REM 找到 Python 解釋器
set PYTHON_EXE=python
where python >nul 2>&1 || set PYTHON_EXE=python3

REM 取得腳本目錄
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%

REM 執行 CLI
%PYTHON_EXE% -m src.harness.cli.main %*

endlocal
