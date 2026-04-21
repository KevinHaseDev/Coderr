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

- Python installed
- Virtual environment support

## Setup

1. Clone the repository.
2. Create and activate a virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the repository root:

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
```

5. Apply migrations:

```bash
python manage.py migrate
```

6. Start the development server:

```bash
python manage.py runserver
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
python manage.py test
```

Run app-specific tests:

```bash
python manage.py test auth_app info_app offers_app orders_app profiles_app reviews_app
```

## Useful Quality Checks

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
```

## Notes

- `db.sqlite3` is ignored and must not be committed.
- The repository is backend-only.
