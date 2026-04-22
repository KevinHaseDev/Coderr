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

## Setup (Copy/Paste)

Run these commands from the repository root.

```bash
python -m venv .venv
```

```bash
.\.venv\Scripts\activate.bat
```

```bash
python -m pip install --upgrade pip
```

```bash
python -m pip install -r requirements.txt
```

```bash
copy .env.example .env
```

```bash
python manage.py migrate
```

```bash
python manage.py runserver
```

If you do not want to activate the environment, use the virtual environment Python directly.

```bash
.\.venv\Scripts\python.exe manage.py runserver
```

The API is available under `/api/` and admin under `/admin/`.

## Environment Template

Use the provided template file and copy it to `.env`.

```bash
copy .env.example .env
```

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

```bash
.\.venv\Scripts\python.exe manage.py test
```

Run app-specific tests:

```bash
.\.venv\Scripts\python.exe manage.py test auth_app info_app offers_app orders_app profiles_app reviews_app
```

## Useful Quality Checks

```bash
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
```

## Notes

- `db.sqlite3` is ignored and must not be committed.
- The repository is backend-only.
