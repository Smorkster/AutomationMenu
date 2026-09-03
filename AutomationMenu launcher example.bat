@echo off

set "PYTHON=%APPDATA%\AutomationMenu\.venv\Scripts\python.exe"
set "AM=G:\AutomatiseringTools\AutomationMenu\main.py"

set "PYTHONPYCACHEPREFIX=%APPDATA%\AutomationMenu\pycache"

start "" /b "%PYTHON%" "%AM%"
exit