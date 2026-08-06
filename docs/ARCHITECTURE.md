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
│   └── queries.py          # Reusable query builders (eligibility, stats)
│
├── docs/                   # All project documentation
└── tests/                  # Automated tests (Phase 14)
```

## 4. Blueprint Routing Table

| Blueprint  | Prefix        | Purpose                                            |
|------------|---------------|----------------------------------------------------|
| main       | `/`           | Landing page, announcements, about                 |
| auth       | `/auth`       | Login, register, logout, forgot/reset password     |
| student    | `/student`    | Profile, resume, jobs, applications, interviews    |
| recruiter  | `/recruiter`  | Company profile, jobs, applicants, interviews      |
| admin      | `/admin`      | Manage all entities, reports, settings, export     |

## 5. Design Decisions

- **Application factory** in `app.py` keeps the app configurable and testable.
- **Extensions kept separate** (`extensions.py`) avoids circular imports.
- **All models in `models.py`** as a single, clearly documented module.
- **Business logic extracted to `utils/`** so routes stay thin and reusable.
- **Role-based access** via decorators + Flask-Login `UserMixin` and a `role` column.
- **Blue & white UI** with Bootstrap 5 sidebar layout, responsive for all devices.
- **Security defaults**: password hashing (Werkzeug), CSRF tokens, parameterized queries (SQLAlchemy), auto-escaping templates (XSS protection), validated uploads.

## 6. Module Boundaries (who talks to whom)

```
main ────────────► auth ────────────► student / recruiter / admin
  │                                   │        │           │
  └──── shared: extensions, models,   │        │           │
              utils, templates/layouts│        │           │
                                      ▼        ▼           ▼
                              All read/write ──► SQLite via models.py
```
