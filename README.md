# YouTube-Clone — Django YouTube Clone

[![Live Demo](https://img.shields.io/badge/demo-live-brightgreen)](https://streamhub.pythonanywhere.com/)
[![Python](https://img.shields.io/badge/python-3.13-blue)](https://python.org)
[![Django](https://img.shields.io/badge/django-6.0-092E20)](https://djangoproject.com)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

A production-ready video sharing platform inspired by YouTube, built with Django 6.0. Features include video upload/playback, user authentication, channels, subscriptions, comments, reactions, watch history, search, and tag-based browsing.

**Live Demo:** [https://streamhub.pythonanywhere.com/](https://streamhub.pythonanywhere.com/)

---

## Features

### Core

- **User Authentication** — Custom user model with email, profile picture, bio; signup, login, logout
- **Video Management** — Upload, watch, edit, delete with HTML5 player and thumbnail support
- **Channel System** — Auto-created on signup; customizable name, description, banner; public profile page
- **Comments** — Full CRUD on videos with timestamps and owner-only edit/delete
- **Reactions** — Like/dislike toggle with unique user-video constraint
- **Subscriptions** — Subscribe/unsubscribe to channels; owner cannot self-subscribe
- **Watch History** — Auto-tracked per user; grouped by date; clear or remove individual entries
- **Search** — Search videos by title and channels by name; search history tracking
- **Video Views** — Per-user view logging with aggregated counter

### Advanced

- **Tags & Recommendations** — Assign tags to videos; browse by tag; UserInterest scoring
- **Related Videos** — Up to 10 related videos from the same channel on detail pages
- **Cloudinary CDN** — Video and image storage served via Cloudinary with automatic optimization
- **Pagination** — Video feed, liked videos, watch history, search results
- **Production Security** — HSTS, SSL redirect, secure cookies (enabled automatically when `DEBUG=False`)

### Frontend

- **YouTube-Style UI** — Dark theme, custom navbar with search, collapsible sidebar, channel bar
- **Bootstrap 5 Dark Mode** — `data-bs-theme="dark"` with custom CSS variables
- **Responsive Design** — Mobile sidebar toggle, adaptive grids
- **Interactive Forms** — Drag-drop upload, thumbnail preview, tag selection, password strength meter
- **Toast Notifications** — Auto-dismissing messages for actions

---

## Tech Stack

### Backend

| Technology                              | Purpose                               |
| --------------------------------------- | ------------------------------------- |
| Django 6.0                              | Web framework                         |
| Python 3.13                             | Runtime                               |
| SQLite (dev) / PostgreSQL (prod)        | Database                              |
| Cloudinary                              | Media storage & CDN                   |
| django-cloudinary-storage               | Django storage backend for Cloudinary |
| django-crispy-forms + crispy-bootstrap5 | Form rendering                        |
| Pillow                                  | Image processing                      |
| python-dotenv                           | Environment variable management       |

### Frontend

| Technology                      | Purpose                   |
| ------------------------------- | ------------------------- |
| Bootstrap 5.3                   | CSS framework (dark mode) |
| Bootstrap Icons 1.11            | Icon set                  |
| Google Fonts (Outfit + DM Sans) | Typography                |
| HTML5 Video Player              | Video playback            |

### Deployment

| Platform       | Purpose                |
| -------------- | ---------------------- |
| PythonAnywhere | Production hosting     |
| Cloudinary     | CDN for uploaded media |
| GitHub         | Version control        |

---

## Project Architecture

```text
YouTube-Clone/
├── django_project/           # Project configuration
│   ├── settings.py           # Django settings (env-driven)
│   ├── urls.py               # Root URL configuration
│   ├── wsgi.py               # WSGI entry point
│   ├── asgi.py               # ASGI entry point
│   └── logging_filters.py    # Custom log filter
│
├── accounts/                 # User authentication
│   ├── models.py             # CustomUser (email, profile_pic, bio)
│   ├── views.py              # SignUpView
│   ├── forms.py              # CustomUserCreationForm
│   └── urls.py               # /accounts/signup/
│
├── videos/                   # Video management
│   ├── models.py             # Video, VideoReaction, VideoView
│   ├── views.py              # CRUD, reaction, liked videos
│   ├── forms.py              # VideoUploadForm
│   └── urls.py               # /videos/* (7 routes)
│
├── channels/                 # Channel system
│   ├── models.py             # Channel (OneToOne→User)
│   ├── views.py              # CRUD + detail with stats
│   ├── signals.py            # Auto-create channel on signup
│   └── urls.py               # /channels/* (5 routes)
│
├── comments/                 # Comment system
│   ├── models.py             # Comment (FK→Video, FK→User)
│   ├── views.py              # CRUD
│   └── urls.py               # /comments/* (4 routes)
│
├── subscriptions/            # Channel subscriptions
│   ├── models.py             # Subscription (user, channel, unique)
│   ├── views.py              # List + toggle
│   └── urls.py               # /subscriptions/* (2 routes)
│
├── search/                   # Search functionality
│   ├── models.py             # SearchHistory
│   ├── views.py              # Search, clear/delete history
│   └── urls.py               # /search/* (3 routes)
│
├── recommendations/          # Tags & recommendations
│   ├── models.py             # VideoTag, VideoTagMap, UserInterest
│   ├── views.py              # Tag-based video listing
│   └── urls.py               # /recommendations/tag/<pk>/
│
├── watch_history/            # Watch history
│   ├── models.py             # WatchHistory (user, video, duration)
│   ├── views.py              # List, clear, remove
│   └── urls.py               # /watch_history/* (3 routes)
│
├── pages/                    # Landing page
│   ├── views.py              # HomePageView
│   └── urls.py               # /
│
├── templates/                # Project-level templates
│   ├── base.html             # Main layout (navbar + sidebar)
│   ├── home.html             # Hero landing page
│   └── registration/         # Login + signup pages
│
├── .env.example              # Environment variable template
├── manage.py                 # Django CLI
└── requirements.txt          # Python dependencies
```

### App Relationships

```text
CustomUser ──┬── Channel (OneToOne)
              ├── Video.uploader (FK)
              ├── VideoReaction.user (FK)
              ├── Comment.user (FK)
              ├── Subscription.user / .channel (FK)
              ├── SearchHistory.user (FK)
              ├── WatchHistory.user (FK)
              └── UserInterest.user (FK)

Video ──┬── VideoTagMap (M2M through)
         ├── VideoReaction.video (FK)
         ├── VideoView.video (FK)
         ├── Comment.video (FK)
         └── WatchHistory.video (FK)
```

---

## Database Schema

### accounts_customuser

| Column          | Type          | Constraints  |
| --------------- | ------------- | ------------ |
| id              | BigAutoField  | PK           |
| email           | EmailField    | unique       |
| profile_picture | ImageField    | nullable     |
| bio             | TextField     |              |
| created_at      | DateTimeField | auto_now_add |

### videos_video

| Column      | Type                 | Constraints          |
| ----------- | -------------------- | -------------------- |
| id          | BigAutoField         | PK                   |
| uploader_id | FK→CustomUser        | CASCADE              |
| channel_id  | FK→Channel           | nullable             |
| title       | CharField(255)       |                      |
| description | TextField            |                      |
| video_file  | FileField            | Cloudinary           |
| thumbnail   | ImageField           | nullable, Cloudinary |
| uploaded_at | DateTimeField        | auto_now_add         |
| views       | PositiveIntegerField | default=0            |
| duration    | IntegerField         | seconds              |

### channels_channel

| Column      | Type                | Constraints          |
| ----------- | ------------------- | -------------------- |
| id          | BigAutoField        | PK                   |
| owner_id    | OneToOne→CustomUser | CASCADE              |
| name        | CharField(255)      |                      |
| description | TextField           |                      |
| banner      | ImageField          | nullable, Cloudinary |

See individual app models for the complete schema (12 models total across 8 apps).

---

## Installation

### Prerequisites

- Python 3.10+
- Git
- Cloudinary account (free tier: [cloudinary.com](https://cloudinary.com))

### Local Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/YouTube-Clone.git
cd YouTube-Clone

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate        # Linux/Mac
# .venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
# Edit .env with your settings (see Environment Variables section)

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Start development server
python manage.py runserver

# Open in browser
open http://127.0.0.1:8000/
```

### Environment Variables

| Variable                | Required   | Default               | Description                |
| ----------------------- | ---------- | --------------------- | -------------------------- |
| `DJANGO_SECRET_KEY`     | No         | Hardcoded fallback    | Django secret key          |
| `DJANGO_DEBUG`          | No         | `False`               | Set `True` for development |
| `DJANGO_ALLOWED_HOSTS`  | No         | `localhost,127.0.0.1` | Comma-separated            |
| `CLOUDINARY_CLOUD_NAME` | Yes (prod) | —                     | Cloudinary cloud name      |
| `CLOUDINARY_API_KEY`    | Yes (prod) | —                     | Cloudinary API key         |
| `CLOUDINARY_API_SECRET` | Yes (prod) | —                     | Cloudinary API secret      |

```ini
# .env example
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

---

## Deployment

### PythonAnywhere

The site is currently live at **[streamhub.pythonanywhere.com](https://streamhub.pythonanywhere.com/)**.

#### One-time Setup

1. **Push code to GitHub**, then on PythonAnywhere:

   ```bash
   git clone https://github.com/yourusername/YouTube-Clone.git
   cd YouTube-Clone
   python3.13 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py collectstatic --noinput
   ```

2. **Create Web App**: Web tab → Add new web app → **Manual Configuration** → Python 3.13

3. **Configure**:
   - **Virtualenv**: `/home/yourusername/YouTube-Clone/.venv`
   - **Source code**: `/home/yourusername/YouTube-Clone`
   - **Working directory**: `/home/yourusername/YouTube-Clone`
   - **Static files**: `/static/` → `/home/yourusername/YouTube-Clone/staticfiles`

4. **Set environment variables** in the WSGI file (`/var/www/yourusername_pythonanywhere_com_wsgi.py`):

   ```python
   import os, sys
   os.environ['CLOUDINARY_CLOUD_NAME'] = 'your-cloud-name'
   os.environ['CLOUDINARY_API_KEY'] = 'your-api-key'
   os.environ['CLOUDINARY_API_SECRET'] = 'your-api-secret'
   os.environ['DJANGO_DEBUG'] = 'False'
   os.environ['DJANGO_ALLOWED_HOSTS'] = 'yourusername.pythonanywhere.com'
   os.environ['DJANGO_SECRET_KEY'] = 'your-secret-key'
   path = '/home/yourusername/YouTube-Clone'
   if path not in sys.path:
       sys.path.insert(0, path)
   os.environ['DJANGO_SETTINGS_MODULE'] = 'django_project.settings'
   from django.core.wsgi import get_wsgi_application
   application = get_wsgi_application()
   ```

5. **Reload** the web app.

#### Future Updates

```bash
cd ~/YouTube-Clone && git pull
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

Then click **Reload** on the Web tab.

### Vercel

1. Add a Postgres database from Vercel Storage
2. Set environment variables:
   ```
   DEBUG=False
   SECRET_KEY=<your-secret-key>
   ALLOWED_HOSTS=.vercel.app,your-domain.com
   CSRF_TRUSTED_ORIGINS=https://*.vercel.app
   DATABASE_URL=<postgres-connection-string>
   SECURE_SSL_REDIRECT=True
   ```
3. Deploy with build commands:
   ```bash
   python manage.py collectstatic --noinput
   python manage.py migrate --noinput
   ```

---

## Testing

Test files exist in all 9 apps but contain placeholder stubs only. No tests have been implemented yet.

```bash
# Run all tests
python manage.py test

# Run tests for a specific app
python manage.py test videos
```

---

## API

Currently no REST API is available. Planned for a future iteration using Django REST Framework.

---

## Roadmap

### Short Term

- [ ] Server-side upload validation (file size, format)
- [x] Fix double-nested URL patterns
- [ ] Paginated search results
- [ ] Email notifications for new subscribers/comments
- [ ] Fix double-nested URL patterns (`/comments/comments/`)

### Medium Term

- [ ] REST API with DRF
- [ ] Recommendation engine (collaborative filtering)
- [ ] Notifications system (in-app + email)
- [ ] Video streaming optimization (chunked uploads, HLS)

### Long Term

- [ ] Social login (Google, GitHub)
- [ ] Playlists
- [ ] User settings page
- [ ] Moderation tools
- [ ] Analytics dashboard for creators

---

## Known Limitations

- **Video upload**: No server-side file size validation (client-side "500MB" claim only)
- **Comments**: Not paginated on video detail pages
- **Double-nested URLs**: Fixed (`/comments/comments/` → `/comments/`, etc.)
- **Search**: Uses basic `icontains` matching (not full-text search)
- **Notifications**: Bell icon is decorative only
- **Settings page**: Placeholder link only
- **Password reset**: Not implemented
- **Playlists**: Not supported
- **Tests**: Placeholder stubs only (0% coverage)

---

## License

This project is built for learning and portfolio purposes. See [LICENSE](LICENSE) for details.

---

## Acknowledgments

- Built with [Django](https://djangoproject.com)
- Media hosting by [Cloudinary](https://cloudinary.com)
- Deployed on [PythonAnywhere](https://pythonanywhere.com)
- Inspired by [YouTube](https://youtube.com)
