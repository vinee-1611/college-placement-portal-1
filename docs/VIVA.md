# Viva Questions & Answers

## General / Project Overview

**Q1. What is your project?**
A web-based College Placement Portal that manages the full campus recruitment lifecycle — student profiles and resumes, job postings, applications, shortlisting, interviews, and offer letters — for three roles: students, recruiters, and the placement officer (admin).

**Q2. Why did you choose this project?**
Traditional placement drives depend on emails, paper forms and spreadsheets, which cause missed applications, eligibility confusion and slow processing. The portal automates eligibility checks, centralises records, sends notifications and produces reports.

**Q3. What is the architecture?**
Model–View–Controller. Models: `models.py` (SQLAlchemy). Views: Jinja2 templates in `templates/`. Controllers: route functions in `blueprints/` (`main`, `auth`, `student`, `recruiter`, `admin`). Helpers live in `utils/`.

**Q4. Which language and framework?**
Python with the Flask micro-framework; SQLAlchemy ORM; SQLite database; Flask-Login for sessions; Bootstrap 5 + Chart.js + Font Awesome for the frontend.

## Database

**Q5. How many tables?**
12: `users`, `students`, `recruiters`, `admins`, `companies`, `jobs`, `applications`, `interviews`, `offers`, `announcements`, `notifications`, `settings`.

**Q6. What is the relationship between User and Student?**
One-to-one: a `User` holds the login credentials (email, password hash, role); a `Student` (or `Recruiter`/`Admin`) holds role-specific data linked by `user_id`. This is a specialization / inheritance-style design.

**Q7. Explain the application lifecycle table relationships.**
`Company 1—N Job`; `Job 1—N Application`; `Student 1—N Application`; each `Application 0..1 Interview` and `0..1 Offer`. Status flow: Applied → Shortlisted → Interview Scheduled → Selected/Rejected.

**Q8. Why SQLite?**
Zero configuration, single-file, works offline, sufficient for a campus-scale project, and supported directly by SQLAlchemy.

## Authentication & Security

**Q9. How is the password stored?**
Hashed with Werkzeug's `scrypt` (salt + hash). We never store plaintext. Verified with `check_password`.

**Q10. How is role-based access enforced?**
Custom decorators — `login_required`, `student_required`, `recruiter_required`, `admin_required` — placed on each route; they check the session user's role and redirect/403 otherwise.

**Q11. What security measures exist?**
scrypt password hashing, CSRF protection, server-side input validation (email, phone, CGPA, password strength), file-type checks on uploads, XSS-safe Jinja2 templates, and role-based decorators.

## Business Logic

**Q12. How is eligibility decided?**
A helper (`utils/queries.py`) filters jobs by: active status, deadline not passed, student CGPA ≥ `min_cgpa`, backlogs ≤ `max_backlogs`, and no existing application by that student. The same logic powers browse and apply.

**Q13. What happens if a student applies twice?**
The server checks for an existing application and rejects the duplicate with a flash message.

**Q14. Why is a resume required to apply?**
The recruiters need a resume to evaluate candidates; the apply route validates that `resume_path` exists before creating an application.

**Q15. What is the company approval workflow?**
Recruiters register with a company; the company starts as `is_approved=False`. Jobs can only be posted after the admin approves the company.

## Features / Implementation

**Q16. How are notifications implemented?**
`utils/notifications.py` `notify(user_id, title, message, link)` inserts a `Notification` row. Templates count unread rows for the bell badge; marking read flips `is_read`.

**Q17. How do the charts work?**
The admin dashboard and reports endpoints pass aggregated JSON data to Chart.js, which renders bar/line/doughnut charts client-side.

**Q18. What is CSRF and how does Flask handle it?**
CSRF (Cross-Site Request Forgery) prevents attackers forging requests. Flask-WTF/CSRF middleware embeds a per-session token in forms and validates it on POST.

**Q19. How are CSV exports done?**
The admin reports route builds CSV in memory with Python's `csv` module and streams it as a `text/csv` download via `Response`.

## Testing & Deployment

**Q20. How did you test it?**
`tests/smoke_test.py` runs 79 end-to-end requests through Flask's test client (registration → apply → interview → offer → reports) and `tests/test_units.py` runs 12 unit tests for validators, models, eligibility and notifications.

**Q21. How is the application deployed/run?**
```bash
pip install -r requirements.txt
python app.py   # serves on http://127.0.0.1:5000
```
Database and uploads are created automatically on first run.

**Q22. How would you deploy it to production?**
Use a WSGI server (Gunicorn/uWSGI) behind Nginx, switch to PostgreSQL, set a secret key from environment variables, enable HTTPS, and serve static files via Nginx.

## Future Enhancements

**Q23. What would you improve?**
Email/SMS notifications, resume parsing/ranking, on-campus drive scheduling, online aptitude tests, company ratings, cloud deployment, and a mobile/PWA frontend.

**Q24. What are the biggest limitations of the current system?**
Notifications are in-app only (no email), the demo reset link is not a real email flow, and SQLite is single-writer — fine for campus scale but not high concurrency.
