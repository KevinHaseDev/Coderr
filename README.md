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

clone the repository
```bash
git clone <REPOSITORY-LINK>
```

create the virtual environment (.venv)
Creates an isolated Python environment for this project.

```bash
python -m venv .venv
```
activate the venv
Activates the environment so Python and pip use the packages inside .venv.

```bash
.\.venv\Scripts\activate.bat
```
upgrade pip
Ensures you are using the latest package installer.

```bash
python -m pip install --upgrade pip
```
install dependencies
Installs all required packages listed in requirements.txt.

```bash
python -m pip install -r requirements.txt
```
apply database migrations
Creates all database tables based on your Django models.

```bash
copy .env.example .env
```

```bash
python manage.py migrate
```
start server
Starts the Django development server at http://127.0.0.1:8000/.

```bash
python manage.py runserver
```
If you do not want to activate the environment, use the virtual environment Python directly.
Runs the server using the Python executable inside .venv without activating it.

```bash
.\.venv\Scripts\python.exe manage.py runserver
```
create a .env file
Stores sensitive settings like SECRET_KEY outside the codebase.

## Environment Template

Use the provided template file and copy it to `.env`.
Example:

```text
SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
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
