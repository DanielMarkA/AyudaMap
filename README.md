# AyudaMap

**Community Aid & Disaster Relief Platform**

AyudaMap is a Django web application for mapping and coordinating community aid resources during disasters and relief operations. Volunteers and coordinators can publish verified aid locations (medical facilities, food distribution, shelters, government services, donation drop-offs), see them on an interactive map, confirm that a site is still active, update its operating status, and review relief-operations analytics.

This repository is an individual final project for a Python Django + Supabase course. The SQL JOIN / SUBQUERY requirement is implemented in the app at `/queries/`.

---

## Table of contents

- [Features](#features)
- [Tech stack](#tech-stack)
- [Project structure](#project-structure)
- [Quick start (local development)](#quick-start-local-development)
- [Demo accounts](#demo-accounts)
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
- **JOIN / SUBQUERY demo page** (`/queries/`) — resource rows joined with their submitter and profile, plus a volunteer-filtered subquery; generated SQL is shown on the page.
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
├── seed_data.py            # Demo data seeder
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
# Edit .env and set SECRET_KEY. Leave DATABASE_URL unset to use SQLite.

# 4. Apply migrations
python manage.py migrate

# 5. (Optional) Load demo accounts and resources
python seed_data.py

# 6. Run the development server
python manage.py runserver
```

Open <http://127.0.0.1:8000/> and sign in. To connect to Supabase instead of SQLite, set `DATABASE_URL` in `.env` (see [Configuration](#configuration)).

## Demo accounts

`seed_data.py` creates the following accounts for demonstration:

| Username | Password | Role |
| --- | --- | --- |
| `admin` | `AdminAyuda2026!` | Superuser / National Coordinator |
| `juan_delacruz` | `AyudaPass123!` | Community volunteer |

It also seeds six verified aid resources around Metro Manila. **These credentials are hard-coded in the seed script and are for local/demo use only — never deploy with them.**

## Configuration

All configuration is read from `.env` in the project root (loaded by `python-dotenv` in `config/settings.py`). See [`.env.example`](.env.example) for the full template.

| Variable | Required | Purpose |
| --- | --- | --- |
| `SECRET_KEY` | **Yes** | Django signing key. `settings.py` currently falls back to a hard-coded *insecure* development key; always set this outside local development. |
| `DATABASE_URL` | No | Supabase/Postgres connection string. When absent, Django falls back to `db.sqlite3`. |
| `SUPABASE_URL` | No | Project URL recorded for reference; not consumed directly by the ORM path. |

Current development defaults in `config/settings.py`: `DEBUG = True`, `ALLOWED_HOSTS = ['*']`, console email backend, and static/media served locally. See [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) before exposing the app publicly.

## Running the tests

```powershell
python manage.py test
```

To run a single app's suite:

```powershell
python manage.py test apps.home
```

There are 19 tests across five apps covering the auth flow, home map filters, resource creation, profile and settings updates, and password changes. Details in [`docs/TESTING.md`](docs/TESTING.md).

## Documentation

| Document | Contents |
| --- | --- |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Vertical-slice architecture, request flow, ERD, model and field reference |
| [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) | End-user walkthrough of every screen |
| [`docs/TESTING.md`](docs/TESTING.md) | Test inventory and how to run/extend it |
| [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) | Production configuration checklist |
| [`CHANGELOG.md`](CHANGELOG.md) | Commit-derived project history |

## Production notes

The repository is currently configured for development. Before deploying, at minimum: set a real `SECRET_KEY`, set `DEBUG = False`, restrict `ALLOWED_HOSTS`, configure `DATABASE_URL` with SSL, replace the console email backend, run `collectstatic`, serve media through the web server, and remove the seeded demo credentials. The full checklist is in [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md).
