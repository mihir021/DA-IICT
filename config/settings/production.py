import os
from .base import *  # noqa: F403

DEBUG = False

# Render sets the RENDER_EXTERNAL_HOSTNAME env var automatically
RENDER_HOST = os.getenv("RENDER_EXTERNAL_HOSTNAME", "")
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
if RENDER_HOST:
    ALLOWED_HOSTS.append(RENDER_HOST)

# Allow any custom domain set via env var
EXTRA_HOSTS = os.getenv("EXTRA_ALLOWED_HOSTS", "")
if EXTRA_HOSTS:
    ALLOWED_HOSTS += [h.strip() for h in EXTRA_HOSTS.split(",") if h.strip()]

# ── Static files via WhiteNoise ─────────────────────────────────
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",   # right after SecurityMiddleware
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

STATIC_URL   = "/static/"
STATIC_ROOT  = BASE_DIR / "staticfiles"  # noqa: F405
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ── SQLite (sessions / Django admin) ───────────────────────────
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
    }
}

# ── Security ────────────────────────────────────────────────────
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE   = True
CSRF_COOKIE_SECURE      = True

CSRF_TRUSTED_ORIGINS = [
    "https://*.onrender.com",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
if RENDER_HOST:
    CSRF_TRUSTED_ORIGINS.append(f"https://{RENDER_HOST}")
