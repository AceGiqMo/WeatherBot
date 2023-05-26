@echo off

call %~dp0virtual\Scripts\acitvate

SET TOKEN=TOKEN

python weather_reporto.py

pause

