@echo off
chcp 65001 >nul
title Jarvis (yazi modu)
cd /d "%~dp0"
python asistan.py --yazi
pause
