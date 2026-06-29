"""
PythonAnywhere WSGI Configuration
==================================
Replace the contents of your PythonAnywhere WSGI file
(/var/www/<username>_pythonanywhere_com_wsgi.py) with this.

Two Options:
  Option A — Hardcode env vars here (simplest, no .env file on server)
  Option B — Load from a .env file on the server

Choose one and delete the other.
"""

import os
from pathlib import Path

# ── Option A: Hardcode Environment Variables ─────────────────────────────────
# Uncomment and fill in your actual values.  PythonAnywhere free plan does not
# expose a UI for env vars, so this is the easiest approach.

# os.environ['DJANGO_SECRET_KEY']       = 'your-production-secret-key'
# os.environ['DJANGO_DEBUG']            = 'False'
# os.environ['DJANGO_ALLOWED_HOSTS']    = 'yourdomain.pythonanywhere.com,localhost,127.0.0.1'
# os.environ['DATABASE_URL']            = 'mysql://user:pass@host/dbname'
# os.environ['CLOUDINARY_CLOUD_NAME']   = 'your-cloud-name'
# os.environ['CLOUDINARY_API_KEY']      = 'your-api-key'
# os.environ['CLOUDINARY_API_SECRET']   = 'your-api-secret'


# ── Option B: Load from .env File ────────────────────────────────────────────
# Upload a .env file to the project root (/home/<user>/<project>/.env)
# and uncomment the lines below.  Requires python-dotenv to be installed.

# from dotenv import load_dotenv
# env_path = Path('/home/yourusername/YouTube-Clone/.env')
# load_dotenv(dotenv_path=env_path)


# ── Django Bootstrap ─────────────────────────────────────────────────────────
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings')

from django.core.wsgi import get_wsgi_application  # noqa: E402
application = get_wsgi_application()
