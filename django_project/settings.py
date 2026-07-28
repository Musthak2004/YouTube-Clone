import os
from pathlib import Path

# ── Load .env file (optional — allows production to skip python-dotenv) ──
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

BASE_DIR = Path(__file__).resolve().parent.parent

# ── Django Core ──────────────────────────────────────────────────────────────
# SECURITY WARNING: keep the secret key used in production secret!
# Generate one: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    from django.core.management.utils import get_random_secret_key

    SECRET_KEY = get_random_secret_key()

DEBUG = os.environ.get("DJANGO_DEBUG", "False") == "True"
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# Auto-add Vercel deployment URL if present
VERCEL_URL = os.environ.get("VERCEL_URL")
if VERCEL_URL:
    ALLOWED_HOSTS.append(VERCEL_URL)
    ALLOWED_HOSTS.append(VERCEL_URL.replace("https://", ""))
    # Allow all *.vercel.app domains for aliased preview URLs
    ALLOWED_HOSTS.append(".vercel.app")

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# ── Database ─────────────────────────────────────────────────────────────────
# Supports DATABASE_URL (PostgreSQL/MySQL) or falls back to SQLite.
DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL:
    import dj_database_url

    DATABASES = {
        "default": dj_database_url.config(default=DATABASE_URL, conn_max_age=600)
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# ── Storage ─────────────────────────────────────────────────────────────────
# Static files served from staticfiles/ after collectstatic.
# Media files: use Cloudinary when configured, else local media/ directory.

cloudinary_name = os.environ.get("CLOUDINARY_CLOUD_NAME")
cloudinary_key = os.environ.get("CLOUDINARY_API_KEY")
cloudinary_secret = os.environ.get("CLOUDINARY_API_SECRET")

if cloudinary_name and cloudinary_key and cloudinary_secret:
    CLOUDINARY_STORAGE = {
        "CLOUD_NAME": cloudinary_name,
        "API_KEY": cloudinary_key,
        "API_SECRET": cloudinary_secret,
    }
    STORAGES = {
        "default": {
            "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
    MEDIA_URL = f"https://res.cloudinary.com/{cloudinary_name}/"
    # Also set legacy CLOUDINARY_URL so the cloudinary SDK picks it up
    os.environ.setdefault(
        "CLOUDINARY_URL",
        f"cloudinary://{cloudinary_key}:{cloudinary_secret}@{cloudinary_name}",
    )
else:
    MEDIA_URL = "/media/"
    MEDIA_ROOT = BASE_DIR / "media"

# ── Sentry (optional) ────────────────────────────────────────────────────────
# Set SENTRY_DSN in your environment or .env to enable error tracking.
SENTRY_DSN = os.environ.get("SENTRY_DSN")
if SENTRY_DSN:
    import sentry_sdk

    sentry_sdk.init(dsn=SENTRY_DSN, send_default_pii=True)

# ── Email (optional) ─────────────────────────────────────────────────────────
EMAIL_HOST = os.environ.get("EMAIL_HOST", "")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "True") == "True"
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "webmaster@localhost")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "cloudinary",
    "crispy_forms",
    "crispy_bootstrap5",
    "rest_framework",
    "api.apps.ApiConfig",
    "accounts.apps.AccountsConfig",
    "videos.apps.VideosConfig",
    "comments.apps.CommentsConfig",
    "subscriptions.apps.SubscriptionsConfig",
    "channels.apps.ChannelsConfig",
    "search.apps.SearchConfig",
    "recommendations.apps.RecommendationsConfig",
    "watch_history.apps.HistoryConfig",
    "pages.apps.PagesConfig",
    "playlists.apps.PlaylistsConfig",
    "notifications.apps.NotificationsConfig",
    "livestream.apps.LivestreamConfig",
]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "django_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "django_project.wsgi.application"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

AUTH_USER_MODEL = "accounts.CustomUser"
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# ── Django REST Framework ────────────────────────────────────────────────────
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "ignore_https_probe": {
            "()": "django_project.logging_filters.IgnoreHttpsProbeFilter",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "filters": ["ignore_https_probe"],
        },
    },
    "loggers": {
        "django.server": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
