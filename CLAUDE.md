# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Commands

### Development
- Run development server: `python manage.py runserver`
- Apply database migrations: `python manage.py migrate`
- Create admin user: `python manage.py createsuperuser`
- Collect static files: `python manage.py collectstatic --noinput`

### Testing
- Run all tests: `python manage.py test`
- Run tests for a specific app: `python manage.py test <app_name>` (e.g., `python manage.py test videos`)

## Architecture & Structure

YouClone is a monolithic Django application structured into several functional modules (apps) to handle a YouTube-like video sharing platform.

### Core App Modules
- `accounts`: Manages custom user authentication, profiles, and registration.
- `videos`: Handles video uploads, metadata, playback, and view counting.
- `channels`: Manages video channels and their configurations.
- `comments`: Implements the comment system for videos.
- `subscriptions`: Manages the relationship between users and channels they follow.
- `watch_history`: Tracks videos watched by users.
- `recommendations`: Logic for suggesting videos to users.
- `search`: Implements search functionality for videos and channels.
- `pages`: Handles generic static or landing pages.

### Technical Stack
- **Backend**: Django (Python)
- **Database**: SQLite (local development), PostgreSQL (via Vercel deployment)
- **Frontend**: Django Templates, HTML, CSS, Bootstrap/Tailwind
- **Static/Media**: WhiteNoise for static files; `media/` directory for user-uploaded content (videos, thumbnails, profiles).
- **Deployment**: Configured for Vercel via `vercel.json` and `pyproject.toml`.

### Key Paths
- `django_project/`: Main project settings, ASGI/WSGI configuration, and root URL routing.
- `templates/`: Global HTML templates.
- `media/`: Stores uploaded media files (videos, thumbnails, profiles).
- `manage.py`: Django management command-line utility.
