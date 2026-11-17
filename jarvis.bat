@echo off
rem Jarvis HUD arayuzunu konsol penceresi olmadan baslatir.
rem Bir sorun olursa ayrintilar jarvis_hata.txt dosyasina yazilir.
cd /d "%~dp0"
start "" pythonw jarvis_arayuz.py
