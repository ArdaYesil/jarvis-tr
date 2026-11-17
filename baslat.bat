@echo off
chcp 65001 >nul
title Jarvis
cd /d "%~dp0"
python asistan.py %*
pause
