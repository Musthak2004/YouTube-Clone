# YouTube Clone

[![Live Demo](https://img.shields.io/badge/demo-live-brightgreen)](https://streamhub.pythonanywhere.com/)
[![Python](https://img.shields.io/badge/python-3.13-blue)](https://python.org)
[![Django](https://img.shields.io/badge/django-6.0-092E20)](https://djangoproject.com)
[![Tests](https://img.shields.io/badge/tests-195-passing-green)](https://github.com/Musthak2004/YouTube-Clone)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen)](https://pre-commit.com)

A production-ready video sharing platform inspired by YouTube, built with Django 6.0. Features video upload and playback, user authentication, channels, subscriptions, comments, like/dislike reactions, watch history, tag-based browsing, a tag-weighted recommendation engine, full REST API, notification system, and keyboard shortcuts for video playback.

**Live Demo:** [streamhub.pythonanywhere.com](https://streamhub.pythonanywhere.com/)

---

## Features

### Core

- **User Authentication** — Custom `CustomUser` model extending `AbstractUser` with email, profile picture, bio. Full signup, login, logout via `django.contrib.auth`.
- **Video Management** — Upload videos with title, description, and optional thumbnail. Inline editing and deletion owned by the uploader. **Server-side file size validation** (500 MB video, 5 MB thumbnail). HTML5 video player with poster support.
- **Channel System** — Every user gets an auto-created channel on signup (`channels/signals.py`). Customizable name, description, and banner. Public channel page with subscriber count, video count, and total views.
- **Comments** — Full CRUD on videos. Owner-only edit/delete. **Paginated** (10 per page). **Threaded replies** with nested display, left-border indentation, and inline reply forms. Reply toggle with auto-focus and expandable textarea.
- **Like / Dislike Reactions** — Toggle-based: click again to remove, click opposite to switch. Unique constraint per user-video pair.
- **Subscriptions** — Subscribe and unsubscribe from channels. Self-subscription prevented via `ValidationError`. Toggle on video detail and channel detail pages.
- **Notification System** — Auto-generated notifications when someone comments on your video or subscribes to your channel. Notification list page with pagination, mark-as-read via AJAX, and an unread count badge on the navbar bell icon.
- **Watch History** — Auto-tracked when authenticated users view a video. Grouped by date. Clear all or remove individual entries. Tracks watch duration with periodic JS `timeupdate` events.
- **Watch Duration Tracking** — JavaScript `timeupdate` events every 15 seconds record seconds watched. Final duration sent via `sendBeacon` on page unload. Enables resume-from-last-position and engagement metrics.
- **Search** — Multi-field full-text search across video title, description, uploader username, and channel name. Relevance-ranked with exact matches ranked first. Recent search history for authenticated users (last 8). Clear all or remove individual entries.
- **Video View Tracking** — `VideoView` records per-user (or anonymous) views. Aggregated counter on the `Video` model updated on each view.
- **Error Reporting** — Optional [Sentry](https://sentry.io) integration via `SENTRY_DSN` env var.

### REST API

- **DRF-based API** at `/api/` with browsable interface.
- **Endpoints**: videos (filterable by tag, search), channels (with subscriber/video counts), comments (create/list), tags, and user profile at `/api/me/`.
- **Authentication**: Session-based (`SessionAuthentication`).
- **Permissions**: Read-only for unauthenticated users; write requires authentication.
- **Pagination**: 20 results per page (`PageNumberPagination`).

### Frontend

- **YouTube-Style Dark UI** — Fully custom dark theme with CSS variables. Glassmorphism navbar with backdrop blur. Collapsible sidebar with icon-only mini mode.
- **Light Mode** — Theme toggle in the user dropdown, persisted in `localStorage`. Toggles between dark and light themes with overrides for all component types.
- **Responsive Design** — Mobile sidebar toggle, adaptive video grids (`auto-fill, minmax`), responsive padding at 600px and 992px breakpoints.
- **Drag-and-Drop Upload** — Enhanced file inputs with drag-over visual feedback, file info panel (name + size), thumbnail image preview, and remove button.
- **Inline Validation** — Title validates on blur (min 3 chars) with green/red border feedback. Char counters on title (100) and description (500) with warning/over states.
- **Upload Progress Simulation** — Button loading spinner + animated progress bar with stages (Validating → Uploading → Processing → Finalizing) on form submit.
- **Staggered Entrance Animations** — Sections fade up sequentially with 80ms delays. `prefers-reduced-motion` respected.
- **Keyboard Shortcuts** — YouTube-style shortcuts on video detail page: `Space`/`K` (play/pause), `F` (fullscreen), `M` (mute), `J`/`L` (-10s/+10s), arrow keys (seek/volume). Skips active input fields.
- **Filter Chips** — Horizontal scrollable chip row on the video list for tag-based category browsing. Click a chip to filter by tag; active chip highlighted. Wired to backend tag filtering.
- **Share Button** — Copies video URL to clipboard with animated confirmation toast.
- **Expandable Description** — Click-to-expand video descriptions with "Show more / Show less" toggle.
- **Unsaved Changes Protection** — `beforeunload` warning when form state differs from initial. Visual "Unsaved changes" badge on the edit page.
- **Toast Notifications** — Auto-dismissing messages (4s) for form actions.
- **Comment Pagination** — Paginated comments on the video detail page with page navigator (first, prev, page numbers, next, last).
- **Threaded Replies** — Nested comment display with left-border indentation, inline reply forms with JS toggle, auto-focus, and expandable textarea.
- **Bootstrap Icons + Google Fonts** — Outfit (headings) and DM Sans (body) typography.

### Playlists

- **Full CRUD** — Create, edit, and delete playlists with title, description, and visibility (public/private/unlisted).
- **Save to Playlist** — Inline "Save" button on the video detail page opens a modal to toggle playlist membership. Create new playlists directly from the modal via AJAX.
- **Playlist Detail** — Videos displayed in a grid with order numbers, "Play All" button, and owner edit/delete controls.
- **Sidebar Integration** — The sidebar Playlists link is wired to the user's playlist list with active highlighting.
- **REST API** — Read-only playlist endpoints at `/api/playlists/`, and an `add-to-playlist` action on the video API endpoint.
- **Ownership Enforcement** — `UserPassesTestMixin` protects all mutation views. Private playlists redirect non-owners.

### Account & Settings

- **Settings Page** — Combined profile and password management. Two-section card with inline form switching and validation.
- **Password Reset Flow** — Full Django auth password reset with styled email form, confirmation page, new password form (with validation/error states), completion page, and plain-text email template. Invalid/expired link handling.

### Advanced

- **Tags & Tag-Based Browsing** — Assign tags to videos via `VideoTagMap`. Browse all videos for a tag at `/recommendations/tag/<pk>/`.
- **Recommendation Engine** — `UserInterest` scores increment when a user visits a tag page. `get_recommendations()` utility matches unwatched videos by tag affinity, weighted by recency (2× bonus for last 14 days), view count, and tag match count. Returns top 12 results.
- **Related Videos** — Up to 10 videos from the same channel shown on the detail page sidebar.
- **Production Security** — HSTS, SSL redirect, secure cookies, and `SECURE_PROXY_SSL_HEADER` all auto-enabled when `DEBUG=False`.

---

## Tech Stack

### Backend

| Technology                              | Purpose                               |
| --------------------------------------- | ------------------------------------- |
| Django 6.0.3                            | Web framework                         |
| Python 3.13                             | Runtime                               |
| SQLite (dev) / MySQL (production)       | Database                              |
| Django REST Framework 3.17              | REST API                              |
| django-filter                           | API query parameter filtering         |
| django-crispy-forms + crispy-bootstrap5 | Form rendering helpers                |
| Pillow                                  | Image processing (thumbnails)         |
| pre-commit                              | Git hook management                   |
| python-dotenv                           | Local environment variable management |
| sentry-sdk (optional)                   | Error tracking                        |

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

### App Structure (11 apps, 15 models)

```text
YouTube-Clone/
├── django_project/                 # Project configuration
│   ├── settings.py                 # Env-driven settings (DATABASE_URL, DEBUG,
│   │                               #   SECRET_KEY, HSTS in prod, Sentry, DRF)
│   ├── urls.py                     # Root URL routing to 10 apps + admin
│   ├── wsgi.py                     # WSGI entry point
│   └── logging_filters.py          # Ignores HTTPS-probe noise in dev logs
│
├── accounts/                       # User authentication (1 model)
│   ├── models.py                   # CustomUser (email, profile_picture, bio)
│   ├── views.py / forms.py / urls.py
│   └── tests.py                    # 14 tests
│
├── videos/                         # Video management — core app (3 models)
│   ├── models.py                   # Video, VideoReaction, VideoView
│   ├── views.py                    # List, Detail, Create, Update, Delete,
│   │                               #   VideoReactionView, LikedVideosView
│   ├── forms.py                    # VideoUploadForm with file size validation
│   ├── urls.py                     # 7 routes under /videos/
│   └── tests.py                    # 27 tests
│
├── channels/                       # Channel system (1 model)
│   ├── models.py                   # Channel (OneToOneField → User)
│   ├── signals.py                  # Auto-create channel on user signup
│   ├── views.py / forms.py / urls.py
│   └── tests.py                    # 26 tests
│
├── comments/                       # Video comments (1 model)
│   ├── models.py                   # Comment (FK → Video, FK → User, parent self-FK)
│   ├── views.py / urls.py
│   └── tests.py                    # 25 tests
│
├── subscriptions/                  # Channel subscriptions (1 model)
│   ├── models.py                   # Subscription (unique user+channel;
│   │                               #   self-sub validation)
│   ├── views.py / urls.py
│   └── tests.py                    # 12 tests
│
├── search/                         # Search (1 model)
│   ├── models.py                   # SearchHistory
│   ├── views.py                    # Multi-field relevance-ranked search
│   ├── urls.py
│   └── tests.py                    # 16 tests
│
├── recommendations/                # Tags & recommendations (3 models)
│   ├── models.py                   # VideoTag, VideoTagMap, UserInterest
│   ├── utils.py                    # get_recommendations() — tag-weighted
│   │                               #   scoring algorithm
│   ├── views.py / urls.py
│   └── tests.py                    # 21 tests
│
├── watch_history/                  # Watch history (1 model)
│   ├── models.py                   # WatchHistory
│   ├── views.py / urls.py
│   └── tests.py                    # 15 tests
│
├── notifications/                  # Notification system (1 model)
│   ├── models.py                   # Notification (recipient, actor, verb,
│   │                               #   target_video)
│   ├── signals.py                  # Auto-create on comment/subscription
│   ├── views.py / urls.py
│   └── tests.py                    # 2 tests
│
├── playlists/                       # Playlist management (2 models)
│   ├── models.py                   # Playlist (owner, title, visibility),
│   │                               #   PlaylistItem (playlist, video, order)
│   ├── forms.py                    # PlaylistForm
│   ├── views.py                    # 7 views: CRUD + add-to-playlist + reorder
│   ├── urls.py                     # 7 routes under /playlists/
│   ├── admin.py                    # Admin registration
│   └── tests.py                    # 37 tests
│
├── pages/                          # Landing page
│   ├── views.py / urls.py
│   └── tests.py                    # 2 tests
│
├── api/                            # REST API (DRF)
│   ├── serializers.py              # User, Channel, Video, Comment serializers
│   ├── views.py                    # ViewSets for videos/channels/tags + MeView
│   ├── urls.py                     # DefaultRouter + /me/ + /auth/
│   └── tests.py
│
├── templates/                      # Project-level templates
│   ├── base.html                   # Main layout: navbar, sidebar, toasts
│   ├── home.html                   # Hero landing page
│   └── registration/               # login.html, signup.html
│
├── static/                         # Static assets
│   └── favicon.png
│
├── deploy/                         # Deployment templates
│   └── pythonanywhere_wsgi.py
│
├── docs/
│   └── env-setup-and-deployment.md
│
├── .env.example                    # Environment variable template
├── .pre-commit-config.yaml         # Black, isort, ruff, Django check, tests
├── manage.py                       # Django CLI
└── requirements.txt                # Python dependencies
```

### Model Relationships

```text
CustomUser ──┬── Channel (OneToOne, auto-created via signal)
              ├── Video.uploader (FK)
              ├── VideoReaction.user (FK)
              ├── Comment.user (FK)
              ├── Subscription.user (FK)
              ├── Subscription.channel (FK → User)
              ├── SearchHistory.user (FK)
              ├── WatchHistory.user (FK)
              ├── UserInterest.user (FK)
              ├── Notification.recipient (FK)
              └── Notification.actor (FK)
              ├── Playlist.owner (FK)

Comment ── parent (self-FK, nullable)

Video ──┬── VideoTagMap (M2M through → VideoTag)
         ├── VideoReaction.video (FK)
         ├── VideoView.video (FK)
         ├── Comment.video (FK)
         ├── WatchHistory.video (FK)
         └── Notification.target_video (FK, nullable)

Channel ── Video.channel (FK, nullable)
```

### Model Reference (15 models)

| App            | Model           | Key Fields                                                        |
| -------------- | --------------- | ----------------------------------------------------------------- |
| accounts       | CustomUser      | email (unique), profile_picture, bio, created_at                  |
| videos         | Video           | uploader, channel (nullable), title, description, video_file,     |
|                |                 | thumbnail, uploaded_at, views, duration                           |
| videos         | VideoReaction   | user, video, reaction (like/dislike), created_at                  |
|                |                 | `unique_together: (user, video)`                                  |
| videos         | VideoView       | user (nullable), video, viewed_at                                 |
| channels       | Channel         | owner (OneToOne→User), name, description, banner, created_at      |
| comments       | Comment         | video, user, parent (nullable self-FK), text, created_at, updated_at |
| subscriptions  | Subscription    | user, channel (FK→User), subscribed_at                            |
|                |                 | `unique_together: (user, channel)`; self-sub blocked              |
| recommendations| VideoTag        | name (unique)                                                     |
| recommendations| VideoTagMap     | video, tag; `unique_together: (video, tag)`                       |
| recommendations| UserInterest    | user, tag, score; ordered by -score                               |
| watch_history  | WatchHistory    | user, video, watched_at, watch_duration; `duration_percent` prop  |
| search         | SearchHistory   | user, query, searched_at                                          |
| notifications  | Notification    | recipient, actor, verb, target_video (nullable), is_read          |
| playlists      | Playlist        | owner, title, description, visibility, created_at, updated_at      |
| playlists      | PlaylistItem    | playlist, video, order, added_at; `UniqueConstraint(playlist, video)` |

### URL Structure

| Prefix               | App            | Notes                             |
|----------------------|----------------|-----------------------------------|
| `/`                  | pages          | Landing page only                 |
| `/admin/`            | django.contrib |                                   |
| `/accounts/`         | accounts + auth| Includes `django.contrib.auth.urls` |
| `/videos/`           | videos         | 7 routes, includes `/videos/liked/` |
| `/comments/`         | comments       | All nested under `video_pk` param |
| `/channels/`         | channels       | 5 routes                          |
| `/subscriptions/`    | subscriptions  | 2 routes                          |
| `/search/`           | search         | 3 routes                          |
| `/recommendations/`  | recommendations| `/recommendations/tag/<pk>/`      |
| `/watch_history/`    | watch_history  | 3 routes                          |
| `/playlists/`        | playlists      | 7 routes                          |
| `/notifications/`    | notifications  | 3 routes                          |
| `/api/`              | api            | DRF browsable API + auth          |

### Key Architectural Patterns

**Ownership Enforcement** — Every write operation uses `UserPassesTestMixin` with `test_func()` checking `self.request.user == self.get_object().uploader` (or `.user` for comments). Ensures only the owner can edit or delete their content.

**View Tracking** — `VideoDetailView.get()` manually creates `VideoView` records, updates the aggregated view counter, and creates `WatchHistory` entries for authenticated users — all outside the ORM's auto-handling.

**Reaction Toggle** — `VideoReactionView` implements a toggle: clicking the same reaction removes it, clicking the opposite switches. No separate "unlike" endpoint needed. Enforced via `unique_together` on `(user, video)`.

**Auto Channel Creation** — `channels/signals.py` uses `@receiver(post_save, sender=settings.AUTH_USER_MODEL)` to create a `Channel` instance with a default name when a user signs up.

**Signal-Based Notifications** — `notifications/signals.py` listens for `post_save` on `Comment` and `Subscription` models, automatically creating `Notification` records for the content owner. Self-actions are excluded.

**Recommendation Engine** — `recommendations/utils.py` — `get_recommendations(user)` fetches the user's top 5 `UserInterest` tags, finds unwatched videos sharing those tags, ranks by tag-match count + recency bonus (+2 if <14 days) + view count, and returns the top 12.

**Multi-Field Search** — Search ranks results by relevance using Django `Case/When`: exact title matches first, then title startswith, then title contains, then description/username matches. Channels searched by name and owner username.

**Env-Driven Settings** — `SECRET_KEY` auto-generates if unset. `DEBUG` defaults to `False`. Production auto-enables HSTS, SSL redirect, secure cookies, and proxy SSL header.

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
| `SENTRY_DSN`           | No       | —                     | Sentry error tracking DSN              |
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

The project has **195 tests** across **42 test classes** covering all 11 apps:

| App            | Test Files | Tests | Coverage Highlights                         |
| -------------- | ---------- | ----- | ------------------------------------------- |
| videos         | 1          | 27    | CRUD, reactions (like/dislike/toggle), views |
| accounts       | 1          | 14    | Signup (valid, mismatched, existing), login, logout |
| channels       | 1          | 26    | CRUD, ownership, pagination, context data    |
| comments       | 1          | 25    | CRUD, ownership, threaded replies, nesting, reply counts |
| subscriptions  | 1          | 12    | Subscribe, unsubscribe, self-sub block, own list |
| search         | 1          | 16    | Query results, empty query, history CRUD     |
| recommendations| 1          | 21    | Tags, tag maps, user interests, tag page views |
| watch_history  | 1          | 15    | CRUD, ownership, clear all, single remove    |
| notifications  | 1          | 2     | Model creation, string representation        |
| pages          | 1          | 2     | Status code, template used                   |
| playlists      | 1          | 37    | CRUD, ownership, toggle add/remove, UniqueConstraint, AJAX creation |

```bash
# Run all tests
python manage.py test

# Run tests for a specific app
python manage.py test videos

# Run a single test class
python manage.py test videos.tests.VideoReactionTests

# Run a single test method
python manage.py test videos.tests.VideoReactionTests.test_like_video

# Run with test runner verbosity
python manage.py test -v 2
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

### Pre-commit Hooks (Optional)

The project includes pre-commit hooks for code quality. Install them after cloning:

```bash
pre-commit install
```

This runs Black (formatter), isort (import sorter), ruff (linter), Django system checks, and the full test suite before each commit.

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

## REST API Endpoints

The API is available at `/api/`:

| Endpoint              | Method | Description                        | Auth Required |
| --------------------- | ------ | ---------------------------------- | ------------- |
| `/api/videos/`        | GET    | List videos (filter by `?tag=`, `?search=`) | No |
| `/api/videos/<id>/`   | GET    | Video detail with URL, tags, counts | No           |
| `/api/videos/<id>/react/` | POST | Like or dislike a video           | Yes           |
| `/api/videos/<id>/comments/` | GET/POST | List or create comments    | Write: Yes    |
| `/api/channels/`      | GET    | List channels                      | No            |
| `/api/channels/<id>/` | GET    | Channel detail with subscriber/video counts | No |
| `/api/tags/`          | GET    | List all tags                      | No            |
| `/api/me/`            | GET    | Current user profile               | Yes           |
| `/api/auth/`          | —      | DRF login/logout                   | —             |

---

## Known Limitations

- **Async video processing** — No transcoding or HLS streaming (requires FFmpeg + Celery/Huey on the server)
- **Real-time features** — No WebSockets/SSE (requires Django Channels + Redis, not available on PythonAnywhere free tier)

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
