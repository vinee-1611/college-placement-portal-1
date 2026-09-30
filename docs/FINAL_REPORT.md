# Final Project Report

## 1. Problem Statement

Placement is a critical phase of every engineering student's career. Traditional placement drives rely on manual processes: students forward resumes over email or fill paper forms, recruiters receive an unstructured flood of applications, and the placement office tracks everything in spreadsheets.

This causes several problems:

- **Eligibility confusion** — students cannot easily tell which jobs they qualify for (CGPA, backlogs, deadline).
- **Missed applications** — students are unaware of new openings or interview schedules.
- **No central records** — resumes, shortlists, interview results and offers are scattered across emails and files.
- **Slow approvals** — company registrations, job posts and placements take days to process.
- **No analytics** — the placement officer has no live view of placed students, packages or department-wise performance.

There is a clear need for a single, centralised, role-based web platform where students, recruiters and the placement office can manage the entire placement lifecycle digitally.

## 2. Objectives

1. Provide a single online platform for students, recruiters, and the placement officer.
2. Allow students to register, maintain profiles, upload resumes, and apply only to jobs for which they are eligible.
3. Let recruiters register companies, post and manage jobs, review applicants, shortlist, schedule interviews, and upload offer letters.
4. Give the placement officer tools to manage companies/recruiters, suspend or reinstate companies, manage all records, publish announcements, view statistics and export data.
5. Enforce eligibility rules (CGPA, backlogs, deadline, no duplicate applications) automatically.
6. Notify users in-app about every important event (application, shortlist, interview, result, offer).
7. Generate placement reports and charts for monitoring performance.
8. Provide a zero-configuration, self-contained system that runs with `python app.py`.

## 3. Existing System

The current system is largely manual:

| Activity           | Current method                     | Drawbacks |
|--------------------|------------------------------------|-----------|
| Job announcements  | Notice board / email / WhatsApp    | Information gaps, no eligibility filtering |
| Resume collection  | Email attachments / print copies   | Duplicates, version confusion, lost files |
| Application        | Paper forms / forwarded emails     | No tracking, no status visibility |
| Shortlisting       | Manual spreadsheets                | Slow, error-prone |
| Interviews         | Phone calls / calendars            | Students miss schedules |
| Offers & results   | Email / notice board               | No central archive |
| Reporting          | Manual tallying                    | Delayed, inaccurate |

## 4. Proposed System

The **College Placement Portal** replaces every step above with a web application. Key characteristics:

- **Three role-based dashboards** — student, recruiter, placement officer (admin).
- **Automatic eligibility engine** — a job is only shown as "apply-able" when the student meets CGPA, backlog and deadline criteria and has not already applied.
- **Status-driven application lifecycle** — `Applied → Shortlisted → Interview Scheduled → Selected / Rejected`, with an offer-letter download for selected students.
- **Built-in notifications** — every stakeholder is notified in-app on each status change.
- **Company status control** — recruiter sign-up makes a company live immediately, and the admin can suspend or reinstate it at any time to gate job posting.
- **Analytics & reports** — Chart.js dashboards, department/company-wise reports, and CSV exports.
- **Zero-config deployment** — Flask + SQLite + SQLAlchemy + Flask-Login; the database and upload folders are created automatically on first run.

## 5. System Architecture

- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5, Chart.js, Font Awesome.
- **Backend:** Python 3 + Flask (blueprints), SQLAlchemy ORM.
- **Database:** SQLite (single file `database.db`).
- **Authentication:** Flask-Login sessions + Werkzeug scrypt password hashing.
- **Security:** CSRF protection, server-side input validation, role-based access control decorators, XSS-safe Jinja2 templates.

See `docs/ARCHITECTURE.md`, `docs/CLASS_DIAGRAM.md` and `docs/DIAGRAMS.md` for detailed diagrams.

## 6. Modules & Their Explanation

| # | Module | Responsibilities |
|---|--------|------------------|
| 1 | **Authentication (auth)** | Login/logout, student & recruiter registration, forgot/reset password, change password, strong-password and email validation, role-based login. |
| 2 | **Student module (student)** | Dashboard, profile & photo, resume upload/download/delete, browse eligible jobs, apply/withdraw, track applications, join interviews, download offer letters. |
| 3 | **Recruiter module (recruiter)** | Dashboard, company profile, job CRUD + active toggle, applicant search, shortlist/reject, interview scheduling, select candidates, upload/download offer letters. |
| 4 | **Admin module (admin)** | Dashboard with charts, manage students/recruiters/companies/jobs, suspend or reinstate companies, manage applications/interviews, publish announcements, reports, settings, CSV exports. |
| 5 | **Eligibility engine** | Filters jobs by active status, deadline, CGPA, backlogs, and duplicate applications; used across browse/apply/reports. |
| 6 | **Notifications** | Central helper that creates in-app notifications for users on every lifecycle event. |
| 7 | **Public module (main)** | Landing page, about, public announcements, notifications UI, static upload serving. |

## 7. Database Schema

11 tables: `users`, `students`, `recruiters`, `admins`, `companies`, `jobs`, `applications`, `interviews`, `offers`, `announcements`, `notifications`, plus a `settings` key–value table. Full design and ER diagram: `docs/DATABASE_DESIGN.md`.

## 8. Advantages

- All placement data in one place; no more email/paper chaos.
- Automatic eligibility filtering saves time and prevents invalid applications.
- Full application tracking with a clear status pipeline.
- In-app notifications keep every stakeholder informed.
- Instant, accurate placement statistics and exportable reports.
- Company status stays under admin control at all times.
- Secure: hashed passwords, CSRF protection, input validation, role-based access.
- Portable: runs offline anywhere with just Python; no internet or DB server needed.

## 9. Future Scope

- Email and SMS notifications in addition to in-app alerts.
- Resume parsing and ranking for recruiters.
- On-campus and off-campus drive scheduling with bulk applicant registration.
- Company ratings, past-recruitment analytics and interview experience sharing.
- ATS-style filtering, aptitude tests and online coding evaluations.
- Deployment to a cloud server with PostgreSQL and Redis caching.
- Mobile app / PWA version of the portal.

## 10. Conclusion

The College Placement Portal digitises the entire placement lifecycle — from registration and resume submission through job posting, applying, interviewing, selection and offer distribution — on a single secure platform. It eliminates manual paperwork, applies eligibility rules automatically, keeps every stakeholder notified, and gives the placement office live analytics. The project is fully functional, tested (82 smoke tests + 15 unit tests), and runs with a single `python app.py` command, making it ready for real-world campus use and easy to extend later.
