# Coderr Backend

Django REST backend for the Coderr marketplace domain.

## Tech Stack

- Python 3.14+
- Django 6
- Django REST Framework
- Token authentication (`rest_framework.authtoken`)
- SQLite (default local development database)

## Project Apps

- `auth_app`: registration and login endpoints
- `profiles_app`: profile read/update endpoints
- `offers_app`: offer and offer detail endpoints
- `orders_app`: order lifecycle endpoints
- `reviews_app`: review endpoints
- `info_app`: platform summary endpoint

## Prerequisites

- Python 3.14+
- Git (optional)

## Environment Template

Use the provided template file and copy it to `.env`.

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Windows CMD:

```bat
copy .env.example .env
```

macOS/Linux:

```bash
cp .env.example .env
```

## Setup (Copy/Paste)

Run these commands from the repository root.

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py runserver
```

### Windows CMD

```bat
python -m venv .venv
.\.venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py runserver
```

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

If you do not want to activate the environment, use the virtual environment Python directly.

```powershell
.\.venv\Scripts\python.exe manage.py runserver
```

The API is available under `/api/` and admin under `/admin/`.

## Authentication

The API uses DRF token authentication.

- Register: `POST /api/registration/`
- Login: `POST /api/login/`

Both endpoints return a token. Use it in requests:

```text
Authorization: Token <your_token>
```

## Running Tests

Run all tests:

```powershell
.\.venv\Scripts\python.exe manage.py test
```

Run app-specific tests:

```powershell
.\.venv\Scripts\python.exe manage.py test auth_app info_app offers_app orders_app profiles_app reviews_app
```

## Useful Quality Checks

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
```

## Notes

- `db.sqlite3` is ignored and must not be committed.
- The repository is backend-only.
