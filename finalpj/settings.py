from pathlib import Path
from decouple import config
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# --- Core ---
SECRET_KEY = config("SECRET_KEY", default="CHANGE-ME-IN-PROD", cast=str)
DEBUG = config("DEBUG", default=False, cast=bool)

ALLOWED_HOSTS = [
    h.strip()
    for h in config("ALLOWED_HOSTS", default="").split(",")
    if h.strip()
]

CSRF_TRUSTED_ORIGINS = [
    *(f"http://{h}" for h in ALLOWED_HOSTS if h not in ("*", "localhost", "127.0.0.1")),
    *(f"https://{h}" for h in ALLOWED_HOSTS if h not in ("*", "localhost", "127.0.0.1")),
]


# --- Apps ---
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "finalapp",                # <- แอปหลัก
    "django.contrib.humanize",
    "rest_framework",          # API framework
    # "corsheaders",           # (ถ้าใช้ frontend แยก, เปิดใช้ได้)
]

# --- Middleware ---
MIDDLEWARE = [
    # "corsheaders.middleware.CorsMiddleware",  # ถ้าเปิดใช้ CORS
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",   # serve static files
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "finalpj.urls"

# --- Templates ---
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # หรือจะไม่ใส่ถ้าใช้ใน app
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "finalapp.context_processors.user_member",  # ถ้ามีใช้
            ],
        },
    },
]

WSGI_APPLICATION = "finalpj.wsgi.application"

# --- Database (PostgreSQL) ---
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME"),
        "USER": config("DB_USER"),
        "PASSWORD": config("DB_PASSWORD"),
        "HOST": config("DB_HOST", default="db"),  # Docker service name
        "PORT": config("DB_PORT", default="5432"),
        "CONN_MAX_AGE": 60,
    }
}

# --- Password validators ---
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- I18N / TZ ---
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Bangkok"
USE_I18N = True
USE_TZ = True

# --- Static / Media ---
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"] if (BASE_DIR / "static").exists() else []

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Logging (Dev only) ---
if DEBUG:
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "console": {
                "class": "logging.StreamHandler"
            }
        },
        "loggers": {
            "django.db.backends": {
                "handlers": ["console"],
                "level": "INFO",
            }
        }
    }

