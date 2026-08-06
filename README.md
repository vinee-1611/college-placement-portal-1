# College Placement Portal

A complete web-based campus recruitment management system built with **Flask**, **SQLAlchemy**, **SQLite**, **Bootstrap 5**, and **Chart.js**. It runs with a single command and works offline (all vendor assets are bundled locally).

It connects three user roles on a single digital platform:

- **Students** — register, build profile, upload resume, apply to eligible jobs, track applications, attend interviews, download offer letters.
- **Recruiters** — register company, post/manage jobs, review and shortlist applicants, schedule interviews, upload results and offer letters.
- **Placement Officers (Admins)** — manage students, recruiters, companies and jobs, approve profiles, schedule interviews, generate reports, view statistics, publish announcements, export data.

## Key Features

- Role-based dashboards for student, recruiter and placement officer.
- Automatic **eligibility engine** (CGPA, backlogs, deadline, duplicate checks) — students only see and apply to jobs they qualify for.
- Full application pipeline: **Applied → Shortlisted → Interview Scheduled → Selected / Rejected**, with offer-letter download.
- Company **approval workflow** before recruiters can post jobs.
- In-app **notifications** for every lifecycle event.
- Admin analytics with **Chart.js** (placements, average package, department/company-wise reports) and **CSV exports**.
- Secure: scrypt password hashing, CSRF protection, input validation, role-based access control.

## Tech Stack

| Layer      | Technology                          |
|------------|-------------------------------------|
| Backend    | Python 3, Flask                     |
| ORM        | SQLAlchemy                          |
| Database   | SQLite                             |
| Auth       | Flask-Login, Werkzeug password hash |
| Frontend   | HTML5, CSS3, JavaScript, Bootstrap 5|
| Charts     | Chart.js                            |
| Icons      | Font Awesome                        |
| Security   | CSRF, input validation, XSS-safe templates |

## Quick Start

```bash
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000

The SQLite database (`database.db`) and all upload folders are created automatically on first run. No virtual environment, Docker, or extra configuration is required.

## Project Structure

See `docs/ARCHITECTURE.md` for the full tree and module explanation.

## Documentation

All project documentation lives in the `docs/` folder:

| Document | Contents |
|----------|----------|
| `INSTALLATION.md` | System requirements, setup, running, troubleshooting |
| `USER_MANUAL.md` | How-to guide for all three roles |
| `ARCHITECTURE.md` | System architecture & folder structure |
| `DATABASE_DESIGN.md` | Schema, relationships, ER diagram |
| `CLASS_DIAGRAM.md` | Code-level class diagram & controller map |
| `DIAGRAMS.md` | Use case, sequence, activity, DFD (Level 0 & 1) diagrams |
| `FINAL_REPORT.md` | Problem statement, objectives, modules, report |
| `MINI_REPORT.md` | Concise project summary |
| `PRESENTATION.md` | Slide structure + live demo checklist |
| `VIVA.md` | Viva questions & answers |

## Testing

```bash
python tests\smoke_test.py    # 79 end-to-end tests (deletes/recreates database.db)
python tests\test_units.py    # 12 unit tests (validators, models, queries, notifications)
```
