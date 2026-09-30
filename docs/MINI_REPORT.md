# Mini Project Report — College Placement Portal

## Abstract

The College Placement Portal is a web-based campus recruitment management system that connects **students**, **recruiters**, and the **placement officer** on a single platform. Students register, build profiles, upload resumes, and apply to jobs they are eligible for. Recruiters sign up through a single short form and get live job postings instantly, then review and shortlist applicants, schedule interviews, and upload offer letters. The placement officer manages all records, suspends or reinstates companies, publishes announcements, and views live placement statistics. The system automates eligibility checks, tracks the full application lifecycle, and notifies users in-app on every event.

## Tech Stack

- **Backend:** Python 3, Flask (blueprints), SQLAlchemy ORM
- **Database:** SQLite
- **Authentication:** Flask-Login, Werkzeug scrypt hashing
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5, Chart.js, Font Awesome
- **Security:** CSRF, input validation, role-based access control

## Key Features

1. Role-based login for students, recruiters, and the placement officer.
2. One-screen recruiter signup: company, location, designation, experience, vacancies and open roles create the company, the account and live postings in a single submit.
3. Seeded demo data (10 companies, 19 openings in the 3.4–5.0 LPA band) so Browse Jobs is populated on first run.
4. Student profiles with photo, resume upload (PDF), and eligibility-based job browsing.
5. Recruiter job management with applicant search, shortlisting, and rejection.
6. Interview scheduling with automatic student notifications.
7. Offer-letter upload and download for selected candidates.
8. Admin dashboard with Chart.js analytics and department/company-wise reports.
9. Company status controlled by admin, who can suspend or reinstate any company at any time.
10. In-app notifications for all lifecycle events.
11. CSV exports of students, recruiters, companies, jobs, and applications.
12. Zero-configuration run: `python app.py`.

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

- `tests/smoke_test.py` — 82 end-to-end route/flow tests.
- `tests/test_units.py` — 15 unit tests for validators, models, queries, notifications and the recruiter signup helpers.

## Advantages

Centralised data, automatic eligibility filtering, full application tracking, in-app notifications, instant reports, secure auth, and portable offline operation.

## Future Scope

Email/SMS alerts, resume ranking, drive scheduling, online tests, cloud deployment with PostgreSQL.
