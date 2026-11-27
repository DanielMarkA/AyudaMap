"""
Django settings for AyudaMap project.
Community Aid & Disaster Relief Platform
"""

import os
import dj_database_url
from pathlib import Path
from dotenv import load_dotenv
from django.core.exceptions import ImproperlyConfigured

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env
load_dotenv(BASE_DIR / ".env")


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DJANGO_DEBUG', 'False').lower() == 'true'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = 'django-insecure-local-dev-only-key'
    else:
        raise ImproperlyConfigured("The SECRET_KEY environment variable must be set when DEBUG is False.")

ALLOWED_HOSTS = [
    host.strip() for host in os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')
    if host.strip()
]
if DEBUG and not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]']
if not DEBUG and (not ALLOWED_HOSTS or '*' in ALLOWED_HOSTS):
    raise ImproperlyConfigured("Set DJANGO_ALLOWED_HOSTS to your deployment hostnames.")

SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_HSTS_SECONDS = 0 if DEBUG else 3600
if os.environ.get('DJANGO_TRUST_PROXY_HTTPS', '').lower() == 'true':
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# Application definition
INSTALLED_APPS = [
    # Django core apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Feature apps
    'apps.login',
    'apps.register',
    'apps.home',
    'apps.profile',
    'apps.user_settings',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

LOGIN_URL = 'login:login'
LOGIN_REDIRECT_URL = 'home:dashboard'
LOGOUT_REDIRECT_URL = 'login:login'

WSGI_APPLICATION = 'config.wsgi.application'


# SQLite is available for local development only.
database_url = os.environ.get('DATABASE_URL', '').strip()
if database_url:
    DATABASES = {
        "default": dj_database_url.parse(
            database_url,
            conn_max_age=0,
            ssl_require=True,
        )
    }
elif DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    raise ImproperlyConfigured("Set DATABASE_URL to your production PostgreSQL database.")

if not DEBUG and DATABASES['default']['ENGINE'] != 'django.db.backends.postgresql':
    raise ImproperlyConfigured("DATABASE_URL must point to PostgreSQL when DEBUG is False.")


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Manila'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = 'media/'
MEDIA_ROOT = Path(os.environ.get('DJANGO_MEDIA_ROOT') or BASE_DIR / 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# AyudaMap does not send email. Keep development output out of production logs.
EMAIL_BACKEND = (
    'django.core.mail.backends.console.EmailBackend' if DEBUG
    else 'django.core.mail.backends.dummy.EmailBackend'
)

# Map tiles (CARTO Basemaps API key; falls back to OSM if unset)
CARTO_API_KEY = os.environ.get('CARTO_API_KEY', '').strip()
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
