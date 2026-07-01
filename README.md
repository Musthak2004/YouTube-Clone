# YouTube Clone

[![Live Demo](https://img.shields.io/badge/demo-live-brightgreen)](https://streamhub.pythonanywhere.com/)
[![Python](https://img.shields.io/badge/python-3.13-blue)](https://python.org)
[![Django](https://img.shields.io/badge/django-6.0-092E20)](https://djangoproject.com)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

A production-ready video sharing platform inspired by YouTube, built with Django 6.0. Features video upload and playback, user authentication, channels, subscriptions, comments, like/dislike reactions, watch history, tag-based browsing, and a tag-weighted recommendation engine.

**Live Demo:** [streamhub.pythonanywhere.com](https://streamhub.pythonanywhere.com/)

---

## Features

### Core

- **User Authentication** — Custom `CustomUser` model extending `AbstractUser` with email, profile picture, bio. Full signup, login, logout via django.contrib.auth.
- **Video Management** — Upload videos with title, description, and optional thumbnail. Inline editing and deletion owned by the uploader. HTML5 video player with poster support.
- **Channel System** — Every user gets an auto-created channel on signup (`channels/signals.py`). Customizable name, description, and banner. Public channel page with subscriber count, video count, and total views.
- **Comments** — Full CRUD on videos. Owner-only edit/delete. Comment list sorted newest-first.
- **Like / Dislike Reactions** — Toggle-based: click again to remove, click opposite to switch. Unique constraint per user-video pair.
- **Subscriptions** — Subscribe and unsubscribe from channels. Self-subscription prevented via `ValidationError`. Toggle view on video detail and channel detail pages.
- **Watch History** — Auto-tracked when authenticated users view a video. Grouped by date. Clear all or remove individual entries. Tracks watch duration percentage.
- **Search** — Search videos by title and channels by name using `icontains`. Recent search history saved for authenticated users (last 8). Clear all or remove individual entries.
- **Video View Tracking** — `VideoView` records per-user (or anonymous) views. Aggregated counter on the `Video` model updated on each view.
- **Watch Duration Tracking** — Periodic JS `timeupdate` events record seconds watched per video, enabling resume-from-last-position and engagement metrics.
- **Error Reporting** — Optional [Sentry](https://sentry.io) integration via `SENTRY_DSN` env var.
- **REST API** — DRF-based API at `/api/` with browsable interface. Endpoints for videos (filterable by tag/search), channels, comments, tags, and user profile.
- **Light Mode** — Theme toggle in the user dropdown, persisted in `localStorage`.

### Advanced

- **Tags & Tag-Based Browsing** — Assign tags to videos via `VideoTagMap`. Browse all videos for a tag at `/recommendations/tag/<pk>/`.
- **Recommendation Engine** — `UserInterest` scores increment when a user visits a tag page. `get_recommendations()` utility matches unwatched videos by tag affinity, weighted by recency (2x bonus for last 14 days), view count, and tag match count. Returns top 12 results.
- **Related Videos** — Up to 10 videos from the same channel shown on the detail page sidebar.
- **Pagination** — Video list (10/page), liked videos (12/page), watch history (16/page), tag videos (12/page).
- **Production Security** — HSTS, SSL redirect, secure cookies, and `SECURE_PROXY_SSL_HEADER` all auto-enabled when `DEBUG=False`.
- **Favicon** — Custom 32×32 play-button favicon in `static/`.

### Frontend

- **YouTube-Style Dark UI** — Fully custom dark theme with CSS variables. Glassmorphism navbar with backdrop blur. Collapsible sidebar with icon-only mini mode.
- **Responsive Design** — Mobile sidebar toggle, adaptive video grids (`auto-fill, minmax`), responsive padding at 600px and 992px breakpoints.
- **Drag-and-Drop Upload** — Enhanced file inputs with drag-over visual feedback, file info panel (name + size), thumbnail image preview, and remove button.
- **Inline Validation** — Title validates on blur (min 3 chars) with green/red border feedback. Char counters on title (100) and description (500) with warning/over states.
- **Staggered Entrance Animations** — Sections fade up sequentially with 80ms delays. `prefers-reduced-motion` respected.
- **Upload Progress Simulation** — Button loading spinner + animated progress bar with stages (Validating → Uploading → Processing → Finalizing) on form submit.
- **Unsaved Changes Protection** — `beforeunload` warning when form state differs from initial. Visual "Unsaved changes" badge on the edit page.
- **Toast Notifications** — Auto-dismissing messages (4s) for form actions.
- **Filter Chips** — Horizontal scrollable chip row on the video list for category browsing (visual only — filter logic not yet wired).
- **Share Button** — Copies video URL to clipboard with animated confirmation toast.
- **Expandable Description** — Click-to-expand video descriptions with "Show more / Show less" toggle.
- **Bootstrap Icons + Google Fonts** — Outfit (headings) and DM Sans (body) typography.

---

## Tech Stack

### Backend

| Technology                              | Purpose                               |
| --------------------------------------- | ------------------------------------- |
| Django 6.0                              | Web framework                         |
| Python 3.13                             | Runtime                               |
| SQLite (dev) / MySQL (production)       | Database                              |
| django-crispy-forms + crispy-bootstrap5 | Form rendering helpers                |
| Pillow                                  | Image processing (thumbnails)         |
| python-dotenv (optional)                | Local environment variable management |
| dj-database-url                         | `DATABASE_URL` connection parsing     |

### Frontend

| Technology                      | Purpose                   |
| ------------------------------- | ------------------------- |
| Bootstrap 5.3                   | CSS framework (dark mode) |
| Bootstrap Icons 1.11            | SVG icon set              |
| Google Fonts (Outfit + DM Sans) | Typography                |
| HTML5 Video Element             | Video playback            |

### Deployment

| Platform       | Purpose                |
| -------------- | ---------------------- |
| PythonAnywhere | Production hosting     |
| GitHub         | Version control        |

---

## Project Architecture

```text
YouTube-Clone/
├── django_project/             # Project configuration
│   ├── __init__.py
│   ├── settings.py             # Env-driven settings (DATABASE_URL, SECRET_KEY, etc.)
│   ├── urls.py                 # Root URL routing to 9 apps
│   ├── wsgi.py                 # WSGI entry point
│   └── logging_filters.py      # Ignores HTTPS-probe noise in dev logs
│
├── accounts/                   # User authentication
│   ├── models.py               # CustomUser (email, profile_picture, bio)
│   ├── views.py                # SignUpView (CreateView)
│   ├── forms.py                # CustomUserCreationForm / CustomUserChangeForm
│   └── urls.py                 # /accounts/signup/
│
├── videos/                     # Video management (core app)
│   ├── models.py               # Video, VideoReaction, VideoView
│   ├── views.py                # ListView, DetailView, CreateView, UpdateView,
│   │                           # DeleteView, VideoReactionView, LikedVideosView
│   ├── forms.py                # VideoUploadForm (ModelForm)
│   ├── urls.py                 # /videos/* (7 routes)
│   ├── tests.py                # 27 tests across 6 test classes
│   └── templates/videos/       # 6 templates (list, detail, create, update, delete, liked)
│
├── channels/                   # Channel system
│   ├── models.py               # Channel (OneToOneField → User)
│   ├── views.py                # CRUD + detail with aggregated stats
│   ├── signals.py              # Auto-create channel on user signup
│   ├── forms.py                # ChannelForm
│   └── urls.py                 # /channels/* (5 routes)
│
├── comments/                   # Video comments
│   ├── models.py               # Comment (FK → Video, FK → User)
│   ├── views.py                # CRUD with owner-only edit/delete
│   └── urls.py                 # /comments/* (4 routes)
│
├── subscriptions/              # Channel subscriptions
│   ├── models.py               # Subscription (unique user+channel; self-sub validation)
│   ├── views.py                # ListView + ToggleSubscriptionView
│   └── urls.py                 # /subscriptions/* (2 routes)
│
├── search/                     # Search
│   ├── models.py               # SearchHistory
│   ├── views.py                # SearchView (title + channel icontains, history)
│   └── urls.py                 # /search/* (3 routes)
│
├── recommendations/            # Tags & recommendations
│   ├── models.py               # VideoTag, VideoTagMap, UserInterest
│   ├── views.py                # TagVideoListView (browse by tag)
│   ├── utils.py                # get_recommendations() — tag-weighted scoring
│   └── urls.py                 # /recommendations/tag/<pk>/
│
├── watch_history/              # Watch history
│   ├── models.py               # WatchHistory (user, video, watch_duration, duration_percent)
│   ├── views.py                # ListView, ClearView, RemoveView
│   └── urls.py                 # /watch_history/* (3 routes)
│
├── pages/                      # Landing page
│   ├── views.py                # HomePageView (TemplateView)
│   └── urls.py                 # /
│
├── templates/
│   ├── base.html               # Main layout: navbar, collapsible sidebar, main content
│   ├── home.html               # Hero landing page with animated orbs, CTA, feature cards
│   └── registration/           # login.html, signup.html (Django auth)
│
├── static/
│   └── favicon.png             # Custom 32×32 play-button favicon
│
├── deploy/
│   └── pythonanywhere_wsgi.py  # WSGI template with Option A (hardcode) / Option B (.env)
│
├── docs/
│   └── env-setup-and-deployment.md
│
├── .env.example                # Environment variable template
├── manage.py                   # Django CLI
└── requirements.txt            # Python dependencies
```

### App Relationships

```text
CustomUser ──┬── Channel (OneToOne, auto-created via signal)
              ├── Video.uploader (FK)
              ├── VideoReaction.user (FK)
              ├── Comment.user (FK)
              ├── Subscription.user (FK)
              ├── Subscription.channel (FK → User)
              ├── SearchHistory.user (FK)
              ├── WatchHistory.user (FK)
              └── UserInterest.user (FK)

Video ──┬── VideoTagMap (M2M through → VideoTag)
         ├── VideoReaction.video (FK)
         ├── VideoView.video (FK)
         ├── Comment.video (FK)
         └── WatchHistory.video (FK)

Channel ── Video.channel (FK, nullable)
```

### Model Reference (12 models across 8 apps)

| App            | Model           | Key Fields                                                        |
| -------------- | --------------- | ----------------------------------------------------------------- |
| accounts       | CustomUser      | email (unique), profile_picture, bio, created_at                  |
| videos         | Video           | uploader, channel (nullable), title, description, video_file,     |
|                |                 | thumbnail, uploaded_at, views, duration                           |
| videos         | VideoReaction   | user, video, reaction (like/dislike), created_at                  |
|                |                 | `unique_together: (user, video)`                                  |
| videos         | VideoView       | user (nullable), video, viewed_at                                 |
| channels       | Channel         | owner (OneToOne→User), name, description, banner, created_at      |
| comments       | Comment         | video, user, text, created_at, updated_at                         |
| subscriptions  | Subscription    | user, channel (FK→User), subscribed_at                            |
|                |                 | `unique_together: (user, channel)`; self-subscription blocked     |
| recommendations| VideoTag        | name (unique)                                                     |
| recommendations| VideoTagMap     | video, tag; `unique_together: (video, tag)`                       |
| recommendations| UserInterest    | user, tag, score; ordered by -score                               |
| watch_history  | WatchHistory    | user, video, watched_at, watch_duration; `duration_percent` prop  |
| search         | SearchHistory   | user, query, searched_at                                          |

---

## Installation

### Prerequisites

- Python 3.10+
- Git

### Local Setup

```bash
# Clone the repository
git clone https://github.com/Musthak2004/YouTube-Clone.git
cd YouTube-Clone

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
# Edit .env — at minimum set DJANGO_SECRET_KEY and DJANGO_DEBUG=True

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Start development server
python manage.py runserver
```

### Environment Variables

| Variable               | Required | Default               | Description                            |
| ---------------------- | -------- | --------------------- | -------------------------------------- |
| `DJANGO_SECRET_KEY`    | No *     | Random fallback       | Django secret key                      |
| `DJANGO_DEBUG`         | No       | `False`               | Set `True` for development             |
| `DJANGO_ALLOWED_HOSTS` | No       | `localhost,127.0.0.1` | Comma-separated hostnames              |
| `DATABASE_URL`         | No       | SQLite                | `mysql://user:pass@host/dbname`        |
| `EMAIL_HOST`           | No       | —                     | SMTP host (password reset etc.)        |

\* `SECRET_KEY` is auto-generated if not set (production should set it explicitly).

```ini
# .env example
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
```

---

## Testing

There are **27 tests** across 6 test classes in `videos/tests.py`:

| Test Class              | Tests | Coverage                                      |
| ----------------------- | ----- | --------------------------------------------- |
| `VideoListTests`        | 4     | Status code, template used, content display, empty state |
| `VideoCreateTests`      | 5     | Page access, login required, video creation, uploader set, channel link |
| `VideoDetailTests`      | 4     | Status code, template, title display, view tracking |
| `VideoReactionTests`    | 6     | Like, dislike, toggle off, switch, login required |
| `VideoUpdateDeleteTests`| 6     | Login required, owner allowed/denied, update, delete |
| `LikedVideosTests`      | 3     | Display liked, login required, exclude not-liked |

```bash
# Run all tests
python manage.py test

# Run tests for a specific app
python manage.py test videos
```

---

## Deployment

### PythonAnywhere

Live at **[streamhub.pythonanywhere.com](https://streamhub.pythonanywhere.com/)**.

#### One-time Setup

1. On PythonAnywhere, clone the repo and set up the virtual environment:

   ```bash
   git clone https://github.com/Musthak2004/YouTube-Clone.git
   cd YouTube-Clone
   git checkout musthak
   python3.13 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py collectstatic --noinput
   ```

2. **Create Web App**: Web tab → Add new web app → Manual Configuration → Python 3.13

3. **Configure**:
   - Virtualenv: `/home/streamhub/YouTube-Clone/.venv`
   - Source code: `/home/streamhub/YouTube-Clone`
   - Working directory: `/home/streamhub/YouTube-Clone`
   - Static files: URL `/static/` → `/home/streamhub/YouTube-Clone/staticfiles`
   - Media files: URL `/media/` → `/home/streamhub/YouTube-Clone/media`

4. **Set environment variables** in the WSGI file (`/var/www/streamhub_pythonanywhere_com_wsgi.py`):

   ```python
   import os, sys
   os.environ['DJANGO_DEBUG'] = 'False'
   os.environ['DJANGO_ALLOWED_HOSTS'] = 'streamhub.pythonanywhere.com'
   os.environ['DJANGO_SECRET_KEY'] = 'your-production-secret-key'
   path = '/home/streamhub/YouTube-Clone'
   if path not in sys.path:
       sys.path.insert(0, path)
   os.environ['DJANGO_SETTINGS_MODULE'] = 'django_project.settings'
   from django.core.wsgi import get_wsgi_application
   application = get_wsgi_application()
   ```

5. **Reload** the web app.

#### Future Updates

```bash
cd ~/YouTube-Clone
git pull origin musthak
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

Then click **Reload** on the PythonAnywhere Web tab.

---

## Recommendation Engine

The tag-based recommendation system works as follows:

1. **Interest Scoring** — When a user visits a tag page (`/recommendations/tag/<pk>/`), their `UserInterest.score` for that tag increments by 1.
2. **Tag Matching** — `get_recommendations()` queries the user's top 5 tags by score and finds unwatched videos that share at least one of those tags.
3. **Ranking** — Results are sorted by:
   - **Tag match count** (descending) — videos matching more user-interest tags rank higher
   - **Recency bonus** (+2 if uploaded within 14 days)
   - **View count** (descending)
   - **Upload date** (descending)
4. **Exclusions** — Already-watched videos are filtered out.

---

## Known Limitations

- **Video upload** — No server-side file size validation (browser-side hint only)
- **Search** — Uses basic `icontains` matching, not full-text search
- **Notifications** — Bell icon is decorative; no notification system yet
- **Settings page** — Placeholder link in the dropdown menu
- **Password reset** — Not implemented
- **Playlists** — Not supported

---

## License

MIT — see [LICENSE](LICENSE) for details.

---

## Acknowledgments

- Built with [Django](https://djangoproject.com)
- Deployed on [PythonAnywhere](https://pythonanywhere.com)
- Icons by [Bootstrap Icons](https://icons.getbootstrap.com)
- Fonts by [Google Fonts](https://fonts.google.com) (Outfit + DM Sans)
- Inspired by [YouTube](https://youtube.com)
