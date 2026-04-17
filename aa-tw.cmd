@echo off
SETLOCAL
SET "PYTHONPATH=Z:\autoagent-TW"
"Z:\autoagent-TW\venv\Scripts\python.exe" "Z:\autoagent-TW\scripts\aa_orchestrate.py" %*
ENDLOCAL