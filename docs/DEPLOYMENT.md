# Deploying AyudaMap

This setup uses a Linux host, Gunicorn, an HTTPS reverse proxy, and Supabase PostgreSQL.

## 1. Configure the environment

Set these in the host's environment or secret manager:

| Variable | Value |
| --- | --- |
| `DJANGO_DEBUG` | `False` |
| `SECRET_KEY` | A long random value. Generate one with `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`. |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated public hostnames, without schemes or ports. |
| `DATABASE_URL` | The connection URL for the intended Supabase PostgreSQL database. Django requires SSL and does not fall back to SQLite with debug off. |
| `DJANGO_MEDIA_ROOT` | An absolute path on persistent storage, writable by Gunicorn and readable by the proxy. |
| `DJANGO_TRUST_PROXY_HTTPS` | `True` if the trusted reverse proxy terminates TLS and overwrites `X-Forwarded-Proto`; otherwise leave it unset. |

See the [README configuration table](../README.md#configuration) for optional settings. Email delivery is disabled; the notification preferences do not send messages.

## 2. Prepare the database and build

Back up the target database. If it contains course demo data, verify access with a new administrator before disabling the old demo logins or resetting their passwords. Review sample listings before launch: any that aren't real, current aid resources should be unpublished. Removing the old seeder did not change Supabase.

From the repository root:

```bash
python -m pip install -r requirements.txt
python manage.py check --deploy
python manage.py migrate --noinput
python manage.py collectstatic --noinput
```

Django enforces HTTPS, uses secure session and CSRF cookies, and sends HSTS for the app host. The deployment check may report `security.W005` and `security.W021` because HSTS does not cover subdomains or request browser preload. Review those options once you know which domains you control.

## 3. Start Gunicorn and route requests

For a reverse proxy on the same host, run this under your service manager:

```bash
gunicorn config.wsgi:application --bind 127.0.0.1:8000
```

Terminate TLS at the proxy. Preserve the original `Host` and overwrite (rather than forward a client-provided) `X-Forwarded-Proto`. Keep the Gunicorn listener private. For nginx, the relevant locations inside the HTTPS server block are:

```nginx
location /static/ {
    alias /srv/ayudamap/staticfiles/;
}

location /media/ {
    alias /var/lib/ayudamap/media/;
    add_header X-Content-Type-Options nosniff;
}

location / {
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_pass http://127.0.0.1:8000;
}
```

Use the actual checkout's `staticfiles/` directory and the configured `DJANGO_MEDIA_ROOT`. Configure HTTP to redirect to HTTPS at the proxy. Back up uploaded media separately from PostgreSQL.

## 4. Verify on staging

1. Load `/` and `/map/` as a guest. Confirm HTTPS redirection, map tiles, styles, and verified listings.
2. Sign in, open `/dashboard/`, submit a staging-only resource, and verify its audit entry in `/reports/`. Confirm guests cannot access Reports.
3. Sign in to `/admin/` as the new administrator and verify resource management.
4. Upload a profile photo, reload it, and confirm it survives a service restart.
