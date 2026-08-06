# Mini Project Report — College Placement Portal

## Abstract

The College Placement Portal is a web-based campus recruitment management system that connects **students**, **recruiters**, and the **placement officer** on a single platform. Students register, build profiles, upload resumes, and apply to jobs they are eligible for. Recruiters post and manage jobs, review and shortlist applicants, schedule interviews, and upload offer letters. The placement officer approves companies, manages all records, publishes announcements, and views live placement statistics. The system automates eligibility checks, tracks the full application lifecycle, and notifies users in-app on every event.

## Tech Stack

- **Backend:** Python 3, Flask (blueprints), SQLAlchemy ORM
- **Database:** SQLite
- **Authentication:** Flask-Login, Werkzeug scrypt hashing
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5, Chart.js, Font Awesome
- **Security:** CSRF, input validation, role-based access control

## Key Features

1. Role-based login for students, recruiters, and the placement officer.
2. Student profiles with photo, resume upload (PDF), and eligibility-based job browsing.
3. Recruiter job management with applicant search, shortlisting, and rejection.
4. Interview scheduling with automatic student notifications.
5. Offer-letter upload and download for selected candidates.
6. Admin dashboard with Chart.js analytics and department/company-wise reports.
7. Company approval workflow before job posting.
8. In-app notifications for all lifecycle events.
9. CSV exports of students, recruiters, companies, jobs, and applications.
10. Zero-configuration run: `python app.py`.

## Application Lifecycle

```
Applied → Shortlisted → Interview Scheduled → Selected / Rejected
                                              └→ Offer letter download
```

## Database (11 tables)

`users`, `students`, `recruiters`, `admins`, `companies`, `jobs`, `applications`, `interviews`, `offers`, `announcements`, `notifications`, `settings`.

## How to Run

```bash
pip install -r requirements.txt
python app.py
# Open http://127.0.0.1:5000
# Admin: admin@placement.edu / Admin@123
```

The database and upload folders are created automatically on first run.

## Testing

- `tests/smoke_test.py` — 79 end-to-end route/flow tests.
- `tests/test_units.py` — 12 unit tests for validators, models, queries, and notifications.

## Advantages

Centralised data, automatic eligibility filtering, full application tracking, in-app notifications, instant reports, secure auth, and portable offline operation.

## Future Scope

Email/SMS alerts, resume ranking, drive scheduling, online tests, cloud deployment with PostgreSQL.
