# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run development server
python manage.py runserver

# Run all tests (27 tests in videos/tests.py)
python manage.py test

# Run tests for a specific app
python manage.py test videos

# Run a single test class
python manage.py test videos.tests.VideoReactionTests

# Run a single test method
python manage.py test videos.tests.VideoReactionTests.test_like_video

# Migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Install dependencies
pip install -r requirements.txt

# Activate virtual environment (Windows)
.venv\Scripts\activate

# Activate virtual environment (Linux/Mac)
source .venv/bin/activate
```

## Project Architecture

Django 6.0 YouTube clone with 9 apps, 12 models, and a custom user model. All views use Class-Based Views (CBVs). Frontend is a custom dark theme with Bootstrap 5.3, CSS variables, glassmorphism navbar, and no JavaScript framework.

### App Layout

```
django_project/       # Project settings, root URL routing, logging filter
├── settings.py       # Env-driven: DATABASE_URL, SECRET_KEY, DEBUG, HSTS in prod
├── urls.py           # Routes to 9 apps + admin
└── logging_filters.py

accounts/             # CustomUser model extending AbstractUser
├── models.py         # CustomUser: email (unique), profile_picture, bio, created_at
├── forms.py          # CustomUserCreationForm, CustomUserChangeForm
├── views.py          # SignUpView (CreateView)
└── urls.py           # /accounts/signup/

videos/               # Core video management (most complex app)
├── models.py         # Video, VideoReaction, VideoView
├── views.py          # 7 views: List, Detail, Create, Update, Delete, Reaction, Liked
├── forms.py          # VideoUploadForm (ModelForm)
├── urls.py           # 7 routes under /videos/
└── tests.py          # 27 tests across 6 test classes

channels/             # Auto-created per user via post_save signal
├── models.py         # Channel (OneToOneField→User)
├── signals.py        # post_save: create Channel when CustomUser is created
├── views.py          # CRUD + detail with aggregated stats
└── urls.py           # 5 routes

comments/             # CRUD on videos with owner-only edit/delete
├── models.py         # Comment (FK→Video, FK→User)
├── views.py          # List, Create, Update, Delete
└── urls.py           # 4 routes

subscriptions/        # User→User subscriptions (not Channel→User)
├── models.py         # Subscription (unique user+channel, self-sub validation)
├── views.py          # ListView + ToggleSubscriptionView
└── urls.py           # 2 routes

search/               # Basic icontains matching + recent history
├── models.py         # SearchHistory (last 8 queries per user)
├── views.py          # SearchView, ClearSearchHistoryView, DeleteSearchHistoryView
└── urls.py           # 3 routes

recommendations/      # Tag system + interest-scoring recommendation engine
├── models.py         # VideoTag, VideoTagMap, UserInterest
├── views.py          # TagVideoListView
├── utils.py          # get_recommendations() — tag-weighted scoring algorithm
└── urls.py           # 1 route

watch_history/        # Auto-tracked, grouped by date, paginated
├── models.py         # WatchHistory (user, video, watch_duration, duration_percent)
├── views.py          # ListView, ClearView, RemoveView
└── urls.py           # 3 routes

pages/                # Landing page only
├── views.py          # HomePageView (TemplateView)
└── urls.py           # /

templates/            # Project-level templates
├── base.html         # Main layout: navbar, collapsible sidebar (mini mode), toasts
├── home.html         # Hero with animated orbs, feature cards
└── registration/     # login.html, signup.html
```

### Key Patterns Used Throughout

**Ownership enforcement**: Every write operation uses `UserPassesTestMixin` with `test_func()` checking `self.request.user == self.get_object().uploader` (or `.user` for comments).

**View tracking**: `VideoDetailView.get()` manually creates `VideoView` records, updates the aggregate counter, and creates `WatchHistory` for authenticated users — all outside the ORM's auto-handling.

**Reaction toggle**: `VideoReactionView` — clicking same reaction removes it, clicking opposite switches. No separate "unlike" endpoint.

**Auto channel creation**: `channels/signals.py` — `@receiver(post_save, sender=settings.AUTH_USER_MODEL)` creates a `Channel` when a user signs up.

**Recommendations**: `recommendations/utils.py` — `get_recommendations(user)` fetches top 5 `UserInterest` tags, finds unwatched videos sharing those tags, ranks by tag-match count + recency bonus (+2 if <14 days) + view count. Returns top 12.

**Env-driven settings**: `SECRET_KEY` auto-generates if unset. `DEBUG` defaults to `False`. Production auto-enables HSTS, SSL redirect, secure cookies.

**Pagination**: Videos list (10/page), liked videos (12/page), watch history (16/page), tag videos (12/page), channels (10/page).

**Sidebar**: Collapsible to mini mode (72px, icons only) on desktop; hidden with toggle on mobile (<992px).

### URL Structure

| Prefix               | App            | Notes                     |
|----------------------|----------------|---------------------------|
| `/`                  | pages          | Landing page only         |
| `/admin/`            | django.contrib |                           |
| `/accounts/`         | accounts + auth| Includes `django.contrib.auth.urls` |
| `/videos/`           | videos         | 7 routes, includes `/videos/liked/` |
| `/comments/`         | comments       | All nested under `video_pk` param |
| `/channels/`         | channels       | 5 routes                   |
| `/subscriptions/`    | subscriptions  | 2 routes                   |
| `/search/`           | search         | 3 routes                   |
| `/recommendations/`  | recommendations| `/recommendations/tag/<pk>/` |
| `/watch_history/`    | watch_history  | 3 routes                   |

### Testing

Tests live only in `videos/tests.py` (27 tests). Pattern across all test classes:
- `@override_settings(STORAGES={...})` to bypass static file backend
- `make_user()` helper creates users with email
- `SimpleUploadedFile` for video file upload simulation

### Models Reference

| Model         | App            | Key FK Relations                    |
|---------------|----------------|-------------------------------------|
| CustomUser    | accounts       | Base user model                     |
| Video         | videos         | uploader→User, channel→Channel       |
| VideoReaction | videos         | user+video, unique_together          |
| VideoView     | videos         | user (nullable)+video               |
| Channel       | channels       | owner→User (OneToOne)               |
| Comment       | comments       | video+user                          |
| Subscription  | subscriptions  | user+channel (both FK→User)         |
| VideoTag      | recommendations| name (unique)                       |
| VideoTagMap   | recommendations| video+tag, unique_together           |
| UserInterest  | recommendations| user+tag, unique_together, ordered -score |
| WatchHistory  | watch_history  | user+video                          |
| SearchHistory | search         | user+query                          |

### Frontend Architecture

- **Bootstrap 5.3** with `data-bs-theme="dark"` — no custom CSS build step
- **CSS custom properties** on `:root` for all colors, spacing, transitions
- **Glassmorphism** navbar with `backdrop-filter: blur(20px)`
- **Bootstrap Icons 1.11** via CDN
- **Google Fonts**: Outfit (headings) + DM Sans (body)
- **Dark theme only** — no light mode toggle
- **Toast notifications**: Injected via Django messages + auto-dismiss JS
- **Sidebar**: Fixed position, mini mode (72px), mobile overlay with backdrop dismiss

### Deployment

Live at streamhub.pythonanywhere.com. Production uses MySQL via `DATABASE_URL`, manual WSGI config in PythonAnywhere web tab, static files served from `/staticfiles/`, media from `/media/`.

## Skill routing

When the user's request matches an available skill, invoke it via the Skill tool. When in doubt, invoke the skill.

Key routing rules:
- Product ideas/brainstorming → invoke /office-hours
- Strategy/scope → invoke /plan-ceo-review
- Architecture → invoke /plan-eng-review
- Design system/plan review → invoke /design-consultation or /plan-design-review
- Full review pipeline → invoke /autoplan
- Bugs/errors → invoke /investigate
- QA/testing site behavior → invoke /qa or /qa-only
- Code review/diff check → invoke /review
- Visual polish → invoke /design-review
- Ship/deploy/PR → invoke /ship or /land-and-deploy
- Save progress → invoke /context-save
- Resume context → invoke /context-restore
- Author a backlog-ready spec/issue → invoke /spec
