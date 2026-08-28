@echo off

set "PYTHON=%APPDATA%\AutomationMenu\.venv\Scripts\python.exe"
set "AM=G:\Ser\SF_Automatiseringsverktyg\AutomationMenu\main.py"
set "ARGS=--mini"

set "PYTHONPYCACHEPREFIX=%APPDATA%\AutomationMenu\pycache"

"%PYTHON%" "%AM%" "%ARGS%"