@echo off

cd /d "C:\Users\Lenovo\Desktop\My Project\Ticket"
..\venv\Scripts\python.exe manage.py migrate
start "Django Server" cmd /k "cd /d panel && ..\venv\Scripts\python.exe manage.py runserver"

start "Telegram Bot" cmd /k "cd /d panel && ..\venv\Scripts\python.exe manage.py run_bot"