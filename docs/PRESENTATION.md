# Presentation Content

A suggested slide-by-slide structure for presenting the College Placement Portal.

---

## Slide 1 — Title
- **College Placement Portal**
- Campus recruitment management system
- Your Name / Roll No / Class & Section / Guide Name

## Slide 2 — Problem Statement
- Placement drives rely on emails, paper forms, and spreadsheets.
- Students don't know eligibility; recruiters get unstructured applications; the office has no analytics.

## Slide 3 — Objectives
- One platform for students, recruiters, and placement officer.
- Automatic eligibility checking, status tracking, notifications, reports.

## Slide 4 — Existing System
- Notice boards, email attachments, manual spreadsheets.
- Slow, error-prone, no central records.

## Slide 5 — Proposed System
- Web portal: student / recruiter / admin dashboards.
- Application pipeline: Applied → Shortlisted → Interview → Selected/Rejected → Offer.
- Automatic eligibility engine + in-app notifications + charts + CSV export.

## Slide 6 — Tech Stack
- Python + Flask | SQLAlchemy | SQLite | Flask-Login
- Bootstrap 5, Chart.js, Font Awesome
- Runs offline with `python app.py`.

## Slide 7 — Architecture
- MVC: Blueprints (controllers) + templates (views) + models.py (models).
- See `docs/CLASS_DIAGRAM.md` for the class diagram.

## Slide 8 — Use Case Overview
- Student: profile, resume, apply, track, interviews, offers.
- Recruiter: company, jobs, applicants, interviews, offers.
- Admin: approvals, users, reports, announcements, export.

## Slide 9 — Database Design
- 11 tables; key relationships (User→Student/Recruiter/Admin, Company→Job→Application→Interview/Offer).
- ER diagram in `docs/DATABASE_DESIGN.md`.

## Slide 10 — Live Demo (10 minutes)
1. Landing page → register a student + a recruiter.
2. Admin approves the company.
3. Recruiter posts a job.
4. Student uploads resume and applies.
5. Recruiter shortlists → schedules interview → selects → uploads offer.
6. Student sees notifications and downloads the offer.
7. Admin dashboard charts + a report + CSV export.

## Slide 11 — Security
- scrypt password hashing, CSRF protection, server-side validation, role-based access decorators, XSS-safe templates.

## Slide 12 — Testing
- 79 end-to-end smoke tests + 12 unit tests, all passing.

## Slide 13 — Advantages
- Centralised, automatic eligibility, full tracking, notifications, instant analytics, portable & offline.

## Slide 14 — Future Scope
- Email/SMS alerts, resume ranking, drive scheduling, online tests, cloud + PostgreSQL.

## Slide 15 — Conclusion
- A complete, secure, tested, zero-configuration placement management platform.

## Slide 16 — Thank You / Questions

---

## Demo Checklist

- [ ] `python app.py` runs cleanly, DB auto-creates.
- [ ] Admin login: `admin@placement.edu` / `Admin@123`.
- [ ] Student registration + profile + resume upload.
- [ ] Recruiter registration; company shows **Pending**.
- [ ] Admin approves company.
- [ ] Recruiter posts a job with CGPA/backlog/deadline.
- [ ] Student sees the job as eligible and applies (reject duplicate).
- [ ] Recruiter shortlists → schedules interview → student notified.
- [ ] Student joins interview; recruiter selects → uploads offer.
- [ ] Student downloads offer; dashboard shows placed stats.
- [ ] Admin Reports page + CSV export.
- [ ] Announcement published and visible to students/recruiters.
