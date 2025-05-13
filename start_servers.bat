@echo off
start cmd /k "cd backend && python app.py"
start cmd /k "cd pet_adoption && python manage.py runserver"
