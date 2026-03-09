@echo off
cd /d "%~dp0"
python trello_auto_organizer.py >> organize_log.txt 2>&1
