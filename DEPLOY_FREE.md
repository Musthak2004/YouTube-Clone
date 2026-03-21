# Free Deployment Guide

This project is prepared for a free deployment stack:

- Koyeb for the Django web app
- Neon for PostgreSQL
- Cloudinary for uploaded images and videos

## 1. Create the free services

Create these accounts and copy their connection values:

- Neon: create a Postgres database and copy the connection string
- Cloudinary: copy your `CLOUDINARY_URL`
- Koyeb: create a web service from this Git repository

## 2. Set environment variables in Koyeb

Use these values:

```env
DEBUG=False
SECRET_KEY=replace-this-with-a-long-random-secret
ALLOWED_HOSTS=your-app-name.koyeb.app
CSRF_TRUSTED_ORIGINS=https://your-app-name.koyeb.app
DATABASE_URL=postgresql://username:password@your-neon-host/dbname?sslmode=require
DB_SSL_REQUIRE=True
TIME_ZONE=Asia/Colombo
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
CLOUDINARY_URL=cloudinary://api_key:api_secret@cloud_name
```

## 3. Use these Koyeb commands

Build command:

```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
```

Run command:

```bash
gunicorn django_project.wsgi --log-file -
```

## 4. Important notes

- Local development still falls back to SQLite when `DATABASE_URL` is missing.
- Media uploads switch to Cloudinary automatically when `CLOUDINARY_URL` is set.
- Existing files already stored in the local `media/` folder are not migrated automatically.
- Free Koyeb instances can sleep after inactivity, so the first request may be slow.
