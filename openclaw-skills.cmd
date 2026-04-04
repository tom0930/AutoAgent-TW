@echo off
setlocal
set PYTHONPATH=%~dp0
python "%~dp0src\cli\openclaw_skills.py" %*
endlocal
