# Secure Django .env Setup & PythonAnywhere Deployment

## Folder Structure

```
YouTube-Clone/
├── .env                  # Local secrets (gitignored)
├── .env.example          # Template with dummy values (committed)
├── .gitignore
├── requirements.txt
├── manage.py
├── django_project/
│   ├── settings.py       # Reads from .env via python-dotenv
│   ├── wsgi.py           # Django's WSGI entry point
│   └── ...
└── ...
```

---

## 1. `.env` File (Local Development)

Never commit this file. Keep it in `.gitignore`.

```
DJANGO_SECRET_KEY=django-insecure-abc123...
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

CLOUDINARY_CLOUD_NAME=your_cloud
CLOUDINARY_API_KEY=123456789
CLOUDINARY_API_SECRET=your_secret
```

## 2. `.env.example` (Committed to Git)

Template with placeholder values so other devs know what to define:

```
DJANGO_SECRET_KEY=changeme
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

CLOUDINARY_CLOUD_NAME=changeme
CLOUDINARY_API_KEY=changeme
CLOUDINARY_API_SECRET=changeme
```

## 3. `.gitignore`

```
.env
.env.*
!.env.example
```

---

## 4. `settings.py` — Load `.env` & Read Variables

```python
from pathlib import Path
import os

# ── Load .env file (optional — allows production to skip python-dotenv) ──
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BASE_DIR = Path(__file__).resolve().parent.parent

# ── Core Django settings from environment ──
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'fallback-dev-only')
DEBUG = os.environ.get('DJANGO_DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# ── Production security (auto-enabled when DEBUG=False) ──
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ── Third-party API keys ──
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY'),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET'),
}
```

### Key Pattern: `os.environ.get('KEY', 'default')`

- Reading from `os.environ` works whether the value came from `.env` (via `load_dotenv()`) or from the hosting platform's environment variables tab.
- The second argument is a **fallback default** — safe for development, but in production the env var should always be set.

### Why wrap `load_dotenv()` in try/except?

```python
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass
```

On **PythonAnywhere**, you set environment variables through the Web UI, not via `.env`. The `python-dotenv` package may not be installed. This try/except lets the app boot regardless.

---

## 5. PythonAnywhere Deployment: Two Ways to Set Env Vars

### Option A: PythonAnywhere Web UI (Recommended)

1. Go to **Web tab** → **Environment variables** section
2. Add each variable (one per line):

```
DJANGO_SECRET_KEY     →  django-insecure-abc...
DJANGO_DEBUG          →  False
DJANGO_ALLOWED_HOSTS  →  streamhub.pythonanywhere.com,localhost,127.0.0.1
CLOUDINARY_CLOUD_NAME →  your_cloud
CLOUDINARY_API_KEY    →  123456789
CLOUDINARY_API_SECRET →  your_secret
```

3. Click **Save**, then **Reload**

PythonAnywhere injects these directly into the WSGI process's `os.environ` — no WSGI file changes needed. Your `settings.py` already reads them with `os.environ.get(...)`.

### Option B: Manual WSGI File Edit (Alternative)

If you prefer to hardcode env var loading in the WSGI file (e.g., if you deploy a `.env` file to the server):

```python
# /var/www/streamhub_pythonanywhere_com_wsgi.py
import os
from pathlib import Path

# ── Load .env from project root ──
from dotenv import load_dotenv
env_path = Path('/home/streamhub/YouTube-Clone/.env')
load_dotenv(dotenv_path=env_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

**Downside:** You'd need to upload a `.env` file to the server and keep it in sync. The Web UI is simpler and more secure.

---

## 6. The Default WSGI File (No Changes Needed)

```python
# django_project/wsgi.py
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings')

application = get_wsgi_application()
```

This is Django's default WSGI file. It does **not** need to load `.env` because:
- **Locally:** `settings.py` calls `load_dotenv()` when the module imports
- **PythonAnywhere:** The Web UI injects env vars into the process before Django starts

---

## 7. `requirements.txt`

```
python-dotenv>=1.0.0
```

Not strictly needed on PythonAnywhere (where env vars come from the Web UI), but harmless to include. The try/except in `settings.py` handles the case where it's missing.

---

## Summary

| Environment | How env vars are set | `python-dotenv` needed? |
|-------------|---------------------|------------------------|
| Local dev   | `.env` file          | Yes (in `settings.py`) |
| PythonAnywhere | Web UI → Environment Variables | No (handled by try/except) |

The same `settings.py` and `os.environ.get(...)` calls work in both environments without modification.
