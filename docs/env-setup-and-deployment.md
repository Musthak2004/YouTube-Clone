# Secure Django .env Setup & PythonAnywhere Deployment

## Folder Structure

```
YouTube-Clone/
├── .env                      # Local secrets (gitignored)
├── .env.example              # Template with dummy values (committed to git)
├── .gitignore                # .env listed here
├── deploy/
│   └── pythonanywhere_wsgi.py   # Ready-to-use WSGI file template
├── django_project/
│   ├── settings.py           # Reads all secrets from os.environ
│   └── wsgi.py               # Default Django WSGI (no changes needed)
└── ...
```

## How Secrets Flow

```
                    ┌──────────────────────────────────────┐
                    │         os.environ                    │
                    │  (process environment variables)      │
                    └───┬──────────────────────┬───────────┘
                        │                      │
              ┌─────────▼──────────┐   ┌───────▼──────────┐
              │  Local Dev         │   │  PythonAnywhere   │
              │  .env file         │   │  WSGI file sets   │
              │  loaded by         │   │  os.environ[]     │
              │  python-dotenv     │   │  directly         │
              └────────────────────┘   └──────────────────┘
                        │                      │
                        └──────────┬───────────┘
                                   ▼
                        ┌──────────────────────┐
                        │  settings.py          │
                        │  os.environ.get(...)  │
                        └──────────────────────┘
```

---

## 1. Local Development Setup

### 1a. Create `.env`

Copy the template and fill in real values:

```bash
cp .env.example .env
```

`.env` is in `.gitignore` — it will never be committed.

### 1b. Required Variables

| Variable | Description |
|----------|-------------|
| `DJANGO_SECRET_KEY` | Generate with `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `DJANGO_DEBUG` | `True` for local dev, `False` for production |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated hostnames (e.g. `localhost,127.0.0.1`) |
| `CLOUDINARY_CLOUD_NAME` | From Cloudinary Dashboard |
| `CLOUDINARY_API_KEY` | From Cloudinary Dashboard |
| `CLOUDINARY_API_SECRET` | From Cloudinary Dashboard |

### 1c. Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | SQLite (`db.sqlite3`) | PostgreSQL/MySQL URL for production |
| `EMAIL_HOST` | — | SMTP server for password reset emails |
| `EMAIL_HOST_USER` | — | SMTP username |
| `EMAIL_HOST_PASSWORD` | — | SMTP password |

---

## 2. `settings.py` Integration

### 2a. Load .env (optional dependency)

```python
from pathlib import Path
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass
```

The `try/except` allows the app to boot even when `python-dotenv` is not installed (e.g. on PythonAnywhere where env vars come from the WSGI file).

### 2b. Read secrets with fallbacks

```python
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    from django.core.management.utils import get_random_secret_key
    SECRET_KEY = get_random_secret_key()

DEBUG = os.environ.get('DJANGO_DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
```

### 2c. Database URL support

Uses `dj-database-url` when `DATABASE_URL` is set, otherwise falls back to SQLite:

```python
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.config(default=DATABASE_URL, conn_max_age=600)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
```

PythonAnywhere provides MySQL (`yourusername.mysql.pythonanywhere-services.com`) or you can use the free SQLite.

---

## 3. PythonAnywhere Deployment

### 3a. The Problem

The PythonAnywhere **free plan** does not have a "Environment Variables" UI in the Web tab. You must set env vars inside the WSGI file itself.

### 3b. Solution — WSGI File

Use `deploy/pythonanywhere_wsgi.py` as your WSGI file template. There are two options:

**Option A — Hardcode env vars directly** (simplest, no .env needed on server):

```python
import os

os.environ['DJANGO_SECRET_KEY']       = 'your-production-key'
os.environ['DJANGO_DEBUG']            = 'False'
os.environ['DJANGO_ALLOWED_HOSTS']    = 'yourdomain.pythonanywhere.com'
os.environ['DATABASE_URL']            = 'mysql://user:pass@host/dbname'
os.environ['CLOUDINARY_CLOUD_NAME']   = 'your-cloud-name'
os.environ['CLOUDINARY_API_KEY']      = 'your-api-key'
os.environ['CLOUDINARY_API_SECRET']   = 'your-api-secret'

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings')
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

**Option B — Load from `.env` file** (requires `python-dotenv` installed):

```python
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(dotenv_path=Path('/home/yourusername/YouTube-Clone/.env'))
```

### 3c. On PythonAnywhere, replace the WSGI file at:

```
/var/www/yourusername_pythonanywhere_com_wsgi.py
```

Navigate there via the **Web** tab → **Code** section → click the WSGI file link.

### 3d. Also configure:

1. **Virtualenv**: Web tab → Virtualenv → enter `/home/yourusername/.virtualenvs/venv-name`
2. **Static files** (if not using Cloudinary):
   - URL: `/static/`
   - Directory: `/home/yourusername/YouTube-Clone/staticfiles`
3. **Source code**: `/home/yourusername/YouTube-Clone`
4. **Working directory**: `/home/yourusername/YouTube-Clone`

### 3e. Reload

Click the green **Reload** button after every change.

---

## 4. Verification

### 4a. Local (Windows PowerShell)

```powershell
python manage.py check
python manage.py runserver
```

### 4b. PythonAnywhere

Open the bash console and run:

```bash
python manage.py check
python manage.py migrate
python manage.py collectstatic --noinput
```

Then **Reload** the web app.

---

## Summary

| Environment | How env vars are set | `python-dotenv` needed? |
|-------------|---------------------|------------------------|
| Local dev | `.env` file loaded by `load_dotenv()` | Yes |
| PythonAnywhere (paid) | Web UI → Environment Variables | No |
| PythonAnywhere (free) | Hardcoded in WSGI file | No |

The same `settings.py` and `os.environ.get(...)` calls work identically in all environments.
