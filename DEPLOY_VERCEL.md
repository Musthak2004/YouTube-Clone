# Vercel Deployment Guide

This project can run on Vercel using the Python runtime for Django.

## Important

Vercel runs Django as a serverless Python function.

- Cloudinary is still needed for uploaded images and videos
- A real database is still needed for app data
- Local SQLite and local `media/` are not suitable for production on Vercel

## 1. Required services

Prepare these first:

- Vercel for hosting
- Neon for PostgreSQL
- Cloudinary for uploaded media

## 2. Environment variables in Vercel

Add these in the Vercel project settings:

```env
DEBUG=False
SECRET_KEY=replace-this-with-a-long-random-secret
ALLOWED_HOSTS=your-project.vercel.app
CSRF_TRUSTED_ORIGINS=https://your-project.vercel.app
DATABASE_URL=postgresql://username:password@your-neon-host/dbname?sslmode=require
DB_SSL_REQUIRE=True
TIME_ZONE=Asia/Colombo
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
CLOUDINARY_URL=cloudinary://api_key:api_secret@cloud_name
```

## 3. Vercel build command

Set the project build command to:

```bash
python manage.py collectstatic --noinput && python manage.py migrate
```

Vercel will install dependencies from `requirements.txt`.

## 4. Deploy

Import the GitHub repository into Vercel and deploy.

## 5. After deploy

- Open the site
- Test signup and login
- Test image and video upload
- Confirm uploads appear in Cloudinary

## Notes

- The first request can be slower after cold start
- Existing local files in `media/` are not migrated automatically
