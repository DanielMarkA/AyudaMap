# Deployment Notes

The repository ships with development-friendly defaults. **Do not expose it publicly without completing this checklist.**

## Production checklist

### 1. Environment

Create a real `.env` from [`.env.example`](../.env.example):

- `SECRET_KEY` — a long random value. Generate one with:
  ```powershell
  python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
  ```
  `config/settings.py` currently falls back to a hard-coded insecure key, so setting this is mandatory.
- `DATABASE_URL` — your Supabase PostgreSQL connection string with SSL (the ORM path already sets `ssl_require=True`).
- `SUPABASE_URL` — informational project URL.

### 2. Settings to change in `config/settings.py`

| Setting | Current | Production |
| --- | --- | --- |
| `DEBUG` | `True` | `False` (ideally read from an env var) |
| `ALLOWED_HOSTS` | `['*']` | Your exact domain(s) |
| `EMAIL_BACKEND` | Console backend | A real SMTP/email backend — password reset and notifications otherwise print to stdout |
| Static files | Served by Django | `python manage.py collectstatic` + a web server / CDN for `staticfiles/` |
| Media files | Served by Django when `DEBUG` | Serve `media/` through the web server; the `static()` URL helper is disabled when `DEBUG = False` |

### 3. Database

```powershell
python manage.py migrate
python manage.py check --deploy
```

Run `check --deploy` with production settings to see Django's security warnings. Do **not** run `seed_data.py` in production: it hard-codes demo passwords (`AdminAyuda2026!`, `AyudaPass123!`) and resets them on every run. Create real accounts via `/register/` or the admin site instead.

### 4. Application server

The project provides both ASGI and WSGI entry points:

```
config/asgi.py   → config.asgi:application
config/wsgi.py   → config.wsgi:application
```

For example, with Gunicorn (WSGI):

```powershell
pip install gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

Terminate TLS at a reverse proxy (e.g. nginx), and let that proxy serve `/static/` and `/media/`.

### 5. Post-deploy smoke test

1. Load `/login/` — page renders, no debug traceback.
2. Sign in with a real account; confirm the map loads and shows verified resources.
3. Submit a test resource and confirm an audit entry appears in `/reports/`.
4. Open `/admin/` as staff and verify `Resource` / `ResourceStatusLog` are manageable.
5. Check that no secret values appear in logs or error pages.

## Known development-only behaviours

- `DEBUG = True` is hard-coded rather than env-driven.
- `ALLOWED_HOSTS = ['*']` accepts every host.
- Passwords are stored in plain text inside `seed_data.py`.
- Reports (`/reports/`) are publicly accessible.
- `TIME_ZONE = 'Asia/Manila'` is appropriate for the target region but should be reviewed if the app is deployed elsewhere.
