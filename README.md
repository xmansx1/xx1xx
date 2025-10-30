# minajli

This is the Django project "minajli" from the local workspace.

Repository remote intended: https://github.com/xmansx1/xx1xx.git

Notes:
- Django project files are under the repository root.
- The local development DB (db.sqlite3) and virtual env are ignored by `.gitignore`.

How to run locally (quick):

1. Create a virtual environment: python -m venv .venv
2. Activate it: on Windows PowerShell: .\.venv\Scripts\Activate.ps1
3. Install Django and deps (if requirements.txt exists): pip install -r requirements.txt
4. Run migrations: python manage.py migrate
5. Run server: python manage.py runserver

If push to the remote fails due to authentication, configure Git credentials or use a personal access token.
