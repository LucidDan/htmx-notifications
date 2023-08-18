"""
Minimal settings for project 'demo'. This is NOT designed to be used in production.
"""
from os import environ
from pathlib import Path
from django.utils.crypto import get_random_string

BASE_DIR = Path(__file__).resolve().parent.parent
DEBUG = (environ.get("DEBUG", "") == "1")
INTERNAL_IPS = ["127.0.0.1", ]
ALLOWED_HOSTS = ["*", ]
ROOT_URLCONF = "demo.urls"
SECRET_KEY = get_random_string(50)
INSTALLED_APPS = [
    "daphne",
    # "django.contrib.admin",
    # "django.contrib.auth",
    # "django.contrib.contenttypes",
    # "django.contrib.sessions",
    # "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_bootstrap5",
    "django_htmx",
    "demo",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    # "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
    # "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                # "django.contrib.auth.context_processors.auth",
                # "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
ASGI_APPLICATION = "demo.asgi.application"
REDIS_URL = "redis://localhost:6379"
# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
USE_TZ = True
TIME_ZONE = "UTC"
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
BOOTSTRAP5 = {
}
if DEBUG:
    BOOTSTRAP5["css_url"] = {
        "url": "/static/bs/css/bootstrap.min.css",
    }
    BOOTSTRAP5["javascript_url"] = {
        "url": "/static/bs/js/bootstrap.bundle.min.js",
    }
