import os
from pathlib import Path
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY","dev-secret-change-me")
DEBUG = os.getenv("DEBUG","false").lower()=="true"
ALLOWED_HOSTS = [h.strip() for h in os.getenv("ALLOWED_HOSTS","*").split(",")]

SITE_URL = os.getenv("SITE_URL","http://localhost:8000")

DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL","admin@example.com")
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND","django.core.mail.backends.console.EmailBackend")

# Stripe
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY","")
STRIPE_PRICE_ID = os.getenv("STRIPE_PRICE_ID","")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET","")
STRIPE_PORTAL_RETURN_URL = os.getenv("STRIPE_PORTAL_RETURN_URL", SITE_URL + "/")

# reCAPTCHA
RECAPTCHA_SITE_KEY = os.getenv("RECAPTCHA_SITE_KEY","")
RECAPTCHA_SECRET_KEY = os.getenv("RECAPTCHA_SECRET_KEY","")

INSTALLED_APPS = [
    "django.contrib.admin","django.contrib.auth","django.contrib.contenttypes",
    "django.contrib.sessions","django.contrib.messages","django.contrib.staticfiles",
    "rest_framework","directory","billing",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF="venuehub.urls"
WSGI_APPLICATION="venuehub.wsgi.application"

LANGUAGE_CODE="en-gb"
TIME_ZONE="Europe/London"
USE_I18N=True
USE_TZ=True

# Database (Railway supplies DATABASE_URL for Postgres)
default_db_url=os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR/'db.sqlite3'}")
if default_db_url.startswith("sqlite:///"):
    DATABASES={"default":{"ENGINE":"django.db.backends.sqlite3","NAME":default_db_url.replace("sqlite:///","")}}
else:
    p=urlparse(default_db_url)
    DATABASES={"default":{
        "ENGINE":"django.db.backends.postgresql",
        "NAME":p.path.lstrip("/"), "USER":p.username, "PASSWORD":p.password,
        "HOST":p.hostname, "PORT":p.port or "5432"
    }}

STATIC_URL="static/"
STATIC_ROOT=BASE_DIR/"staticfiles"
STATICFILES_DIRS=[BASE_DIR/"venuehub"/"static"]
if not DEBUG:
    STORAGES={"staticfiles":{"BACKEND":"whitenoise.storage.CompressedManifestStaticFilesStorage"}}

MEDIA_URL="/media/"
MEDIA_ROOT=BASE_DIR/"media"

DEFAULT_AUTO_FIELD="django.db.models.BigAutoField"

TEMPLATES=[{
  "BACKEND":"django.template.backends.django.DjangoTemplates",
  "DIRS":[BASE_DIR/"venuehub"/"templates"],
  "APP_DIRS":True,
  "OPTIONS":{"context_processors":[
    "django.template.context_processors.debug",
    "django.template.context_processors.request",
    "django.contrib.auth.context_processors.auth",
    "django.contrib.messages.context_processors.messages",
    "venuehub.context.recaptcha_keys",
  ]},
}]

LOGIN_REDIRECT_URL="/"
LOGOUT_REDIRECT_URL="/"

REST_FRAMEWORK={"DEFAULT_PAGINATION_CLASS":"rest_framework.pagination.PageNumberPagination","PAGE_SIZE":20}
