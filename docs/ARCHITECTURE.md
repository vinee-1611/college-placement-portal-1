# Architecture & Folder Structure

## 1. System Architecture

The application follows the **Model–View–Controller (MVC)** pattern using Flask Blueprints for modular routing.

```
Browser (HTML5 / CSS3 / Bootstrap 5 / JS / Chart.js)
          │  HTTP
          ▼
┌──────────────────────────────────────────────────────────┐
│                      Flask Application                   │
│                                                          │
│  Blueprints (Controllers / Routes)                       │
│   ├─ main.py        (public pages)                       │
│   ├─ auth.py        (login, register, forgot password)   │
│   ├─ student.py     (student features)                   │
│   ├─ recruiter.py   (recruiter features)                 │
│   └─ admin.py       (admin features)                     │
│                                                          │
│  Services / Utilities  (business logic, validators)      │
│                                                          │
│  SQLAlchemy Models (models.py)  ←  the "Model"           │
│                                                          │
│  Jinja2 Templates (the "View")                           │
└──────────────────────────────────────────────────────────┘
          │
          ▼
      SQLite database.db  (+ uploads/ for resumes & offers)
```

## 2. Request Lifecycle

1. Browser sends a request to a route registered by a Blueprint.
2. The route function calls business-logic helpers (validators, file handlers, query builders).
3. Data is read/written through SQLAlchemy models.
4. The route renders a Jinja2 template with context data.
5. Flask-Login manages the session and role-based access; CSRF tokens protect all POST forms.

## 3. Folder Structure

```
PlacementPortal/
│
├── app.py                  # Application factory + entry point (python app.py)
├── config.py               # All configuration constants
├── models.py               # All SQLAlchemy models (11 tables)
├── extensions.py           # Flask/SQLAlchemy/LoginManager instances
├── requirements.txt        # Python dependencies
├── database.db             # SQLite database (auto-created at first run)
│
├── instance/               # Instance-specific data (DB override)
├── uploads/
│   ├── resumes/            # Student resume PDFs
│   ├── offers/             # Recruiter offer-letter PDFs
│   └── images/             # Company logos, profile images
│
├── static/
│   ├── css/                # Global + page CSS
│   ├── js/                 # Global + page JavaScript
│   └── images/             # Static images (logo, favicon, placeholders)
│
├── templates/              # Jinja2 templates grouped by feature
│   ├── layouts/            # Base layout, sidebar, navbar, alerts
│   ├── main/               # Landing page, about, contact, announcements
│   ├── auth/               # Login, register, forgot/reset password
│   ├── dashboard/          # Role dashboards
│   ├── student/            # Student profile, jobs, applications
│   ├── recruiter/          # Company profile, jobs, applicants
│   ├── admin/              # Manage all entities, reports, settings
│   └── errors/             # 404, 403, 500 pages
│
├── blueprints/             # MVC Controllers (routes)
│   ├── __init__.py         # Blueprint registration
│   ├── main.py
│   ├── auth.py
│   ├── student.py
│   ├── recruiter.py
│   └── admin.py
│
├── utils/                  # Business logic helpers
│   ├── __init__.py
│   ├── validators.py       # Email/phone/strong-password/PDF validation
│   ├── files.py            # Resume/offer upload & download helpers
│   ├── decorators.py       # Role-required decorators
│   ├── demo_data.py        # Reference companies & openings seeded on first run
│   └── queries.py          # Reusable query builders (eligibility, stats)
│
├── docs/                   # All project documentation
└── tests/                  # Automated tests (Phase 14)
```

## 4. Blueprint Routing Table

| Blueprint  | Prefix        | Purpose                                            |
|------------|---------------|----------------------------------------------------|
| main       | `/`           | Landing page, announcements, about                 |
| auth       | `/auth`       | Login, quick recruiter signup, logout, forgot/reset password |
| student    | `/student`    | Profile, resume, jobs, applications, interviews    |
| recruiter  | `/recruiter`  | Company profile, jobs, applicants, interviews      |
| admin      | `/admin`      | Manage all entities, reports, settings, export     |

## 5. Design Decisions

- **Application factory** in `app.py` keeps the app configurable and testable. It also owns the first-run bootstrap: `db.create_all()` → `_ensure_schema()` → `_seed_defaults()` (admin + settings) → `_seed_demo_jobs()` (demo companies/jobs, skipped when the `jobs` table is non-empty) → `_sync_demo_data()` (re-applies `utils/demo_data.py` to an already-seeded database).
- **Extensions kept separate** (`extensions.py`) avoids circular imports.
- **All models in `models.py`** as a single, clearly documented module.
- **Business logic extracted to `utils/`** so routes stay thin and reusable.
- **Role-based access** via decorators + Flask-Login `UserMixin` and a `role` column.
- **Blue & white UI** with Bootstrap 5 sidebar layout, responsive for all devices.
- **One-screen recruiter signup** — a single POST creates the company, the recruiter account and one job per listed role, then logs the recruiter in, so there is no empty-state onboarding.
- **Lightweight additive migrations** — `_ensure_schema()` ALTERs tables for columns added to shipped models, because `create_all()` only creates missing tables.
- **`utils/demo_data.py` as the single source of truth for demo content** — `_sync_demo_data()` re-applies it to an already-seeded database (so edits to the demo data take effect without deleting `database.db`) and pushes deadlines forward so demo postings never expire. Jobs that already have applications, and any job a recruiter or admin has deactivated (`is_active`), are never overwritten.
- **Security defaults**: password hashing (Werkzeug), parameterized queries (SQLAlchemy), auto-escaping templates (XSS protection), validated uploads.

## 6. Module Boundaries (who talks to whom)

```
main ────────────► auth ────────────► student / recruiter / admin
  │                                   │        │           │
  └──── shared: extensions, models,   │        │           │
              utils, templates/layouts│        │           │
                                      ▼        ▼           ▼
                              All read/write ──► SQLite via models.py
```
