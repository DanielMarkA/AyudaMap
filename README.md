# AyudaMap

**Community Aid & Disaster Relief Platform**

AyudaMap is a Django web application for mapping and coordinating community aid resources during disasters and relief operations. Volunteers and coordinators can publish verified aid locations (medical facilities, food distribution, shelters, government services, donation drop-offs), see them on an interactive map, confirm that a site is still active, update its operating status, and review relief-operations analytics.

This repository is an individual final project for a Python Django + Supabase course. The SQL JOIN / SUBQUERY requirement is demonstrated through the app's existing resource views and map filters.

---

## Table of contents

- [Features](#features)
- [Tech stack](#tech-stack)
- [Project structure](#project-structure)
- [Quick start (local development)](#quick-start-local-development)
- [Configuration](#configuration)
- [Running the tests](#running-the-tests)
- [Documentation](#documentation)
- [Production notes](#production-notes)

---

## Features

- **Interactive aid map** powered by Leaflet and CARTO basemaps, with category-coloured pins, dark-mode tiles, popups, and "locate me" / click-to-pick coordinates.
- **Verified resources** — only `is_verified=True` entries appear on the public map.
- **Search and filters** by keyword, category, operating status, and urgency level; category defaults to the signed-in user's preference.
- **Live updates** — volunteers can add a resource, confirm a site is still active (atomic `F('confirmations') + 1`), and change its status. Every change writes a `ResourceStatusLog` audit entry.
- **Capacity tracking** — `capacity_total` / `capacity_available` with a computed `occupancy_percentage`.
- **Reports dashboard** (`/reports/`) with totals, utilisation rate, category and urgency breakdowns, critical resources, and a recent field-audit log.
- **Accounts** — registration, login/logout, profile editing (including profile image upload), password change, and user preferences (theme, notifications, preferred category, default map centre/zoom).
- **Volunteer-network filter** — on the map, show only aid sites submitted by volunteers in your city (Django `Subquery`).
- **Django admin** registrations for `Resource` and `ResourceStatusLog`.

## Tech stack

| Layer | Technology |
| --- | --- |
| Backend | Python 3, Django 6.1.1 |
| Database | Supabase PostgreSQL via `DATABASE_URL`; SQLite fallback for local dev |
| DB drivers / utils | `psycopg[binary]` 3.3.9, `dj-database-url` 3.1.2, `sqlparse` 0.6.0 |
| Frontend | Server-rendered Django templates, Leaflet.js, CARTO basemaps, Font Awesome, vanilla CSS/JS |
| Images | Pillow 12.3.0 (profile uploads) |
| Config | `python-dotenv` 1.2.3, timezone `Asia/Manila` |
| Email | Console backend (test/dev only) |

## Project structure

The project uses a **vertical-slice** layout: each feature app owns its models, forms, views, URLs, templates segment, and static assets.

```
AyudaMap/
├── config/                 # Project settings, root URLs, ASGI/WSGI
├── apps/
│   ├── home/               # Resources, map, add/confirm/status, reports
│   ├── login/              # Authentication
│   ├── register/           # Registration (creates Profile + UserSettings)
│   ├── profile/            # User profiles and volunteer activity
│   └── user_settings/      # Preferences and password change
├── templates/              # Shared base + per-app templates
├── static/                 # CSS and JS, mirrored per app
├── requirements.txt
├── .env.example            # Template for required environment variables
└── docs/                   # This documentation set
```

## Quick start (local development)

```powershell
# 1. Create and activate a virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1          # Windows PowerShell
# source venv/bin/activate          # macOS / Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure the environment
Copy-Item .env.example .env          # Windows
# cp .env.example .env              # macOS / Linux
# Keep DJANGO_DEBUG=True and leave DATABASE_URL blank to use local SQLite.

# 4. Apply migrations
python manage.py migrate

# 5. Run the development server
python manage.py runserver
```

Open <http://127.0.0.1:8000/> and register an account. On a fresh database, the map starts empty; add a resource from the dashboard. To access Django admin, create a staff login with `python manage.py createsuperuser`. If you need PostgreSQL for development, point `DATABASE_URL` at a separate development database.

## Configuration

Set configuration in your environment or in a local `.env` file. Environment variables take precedence. See [`.env.example`](.env.example) for local setup.

| Variable | Required | Purpose |
| --- | --- | --- |
| `DJANGO_DEBUG` | No | Defaults to `False`. Set to `True` for local development only. |
| `SECRET_KEY` | With debug off | Django signing key. Use a long, random value in production. |
| `DJANGO_ALLOWED_HOSTS` | With debug off | Comma-separated hostnames, with no scheme or port. |
| `DATABASE_URL` | With debug off | PostgreSQL connection string; Supabase connections use SSL. SQLite is available in debug mode. |
| `DJANGO_TRUST_PROXY_HTTPS` | No | Set to `True` only behind a trusted proxy that replaces `X-Forwarded-Proto`. |
| `DJANGO_MEDIA_ROOT` | No | Filesystem directory for user uploads. Set it to a persistent, writable path on the host. |
| `SUPABASE_URL` | No | Project URL recorded for reference; not consumed directly by the ORM path. |
| `CARTO_API_KEY` | No | Map tile key; falls back to OpenStreetMap when blank. |

## Running the tests

Use the local development configuration with `DATABASE_URL` blank.

```powershell
python manage.py test
```

To run a single app's suite:

```powershell
python manage.py test apps.home
```

Tests cover the auth flow, map filters, resource creation, profile and settings updates, and password changes. Details in [`docs/TESTING.md`](docs/TESTING.md).

## Documentation

| Document | Contents |
| --- | --- |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Vertical-slice architecture, request flow, ERD, model and field reference |
| [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) | End-user walkthrough of every screen |
| [`docs/TESTING.md`](docs/TESTING.md) | Test inventory and how to run/extend it |
| [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) | Production configuration checklist |
| [`CHANGELOG.md`](CHANGELOG.md) | Commit-derived project history |

## Production notes

Production runs behind an HTTPS reverse proxy with Gunicorn, a PostgreSQL database, collected static files, and persistent storage for profile uploads. See [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) for the setup and launch checks, including what to do if the target database still contains course demo data.
