# Class Diagram

The application follows a **Model–View–Controller (MVC)** architecture. The diagrams below describe the design at the code level and at the database level.

---

## 1. Overview

```
Browser (HTML/CSS/JS + Bootstrap 5)
        |
        v
Flask Router (Blueprints: main, auth, student, recruiter, admin)
        |
        v
Controllers (route functions) <--> Services / Helpers (utils/)
        |
        v
Models (SQLAlchemy ORM) <--> SQLite database
```

- **Models** — `models.py` defines 11 ORM classes.
- **Views** — Jinja2 templates in `templates/`, organised by role.
- **Controllers** — route functions in `blueprints/`, organised by role.
- **Helpers** — `utils/` (validators, decorators, files, notifications, queries, demo_data).

---

## 2. Model Classes (Code Level)

```mermaid
classDiagram
    class User {
        +int id
        +str email
        +str password_hash
        +str role
        +bool is_active
        +datetime created_at
        +set_password(raw)
        +check_password(raw)
        +recent_notifications(limit)
        +unread_notifications()
        +all_notifications()
    }
    class Student {
        +int user_id
        +str name
        +str roll_number
        +str department
        +str batch
        +str phone
        +int year
        +float cgpa
        +int backlogs
        +str skills
        +str bio
        +str photo_path
        +str resume_path
        +bool is_placed
        +property user
        +property applications
    }
    class Recruiter {
        +int user_id
        +str name
        +str designation
        +str experience
        +str contact_phone
        +int company_id
    }
    class Admin {
        +int user_id
        +str name
    }
    class Company {
        +int id
        +str name
        +str industry
        +str website
        +str email
        +str phone
        +str location
        +str description
        +bool is_approved
        +property jobs
        +property recruiters
    }
    class Job {
        +int company_id
        +str title
        +str description
        +str skills
        +float min_cgpa
        +int max_backlogs
        +int vacancies
        +float package
        +str location
        +str employment_type
        +date deadline
        +bool is_active
        +property company
        +property applications
    }
    class Application {
        +int student_id
        +int job_id
        +str status
        +datetime applied_at
        +property student
        +property job
        +property interview
        +property offer
    }
    class Interview {
        +int application_id
        +date interview_date
        +str time
        +str mode
        +str location
        +str notes
        +str status
        +str result
        +str result_notes
    }
    class Offer {
        +int application_id
        +float package
        +str offer_path
        +datetime issued_at
    }
    class Announcement {
        +str title
        +str message
        +datetime created_at
    }
    class Notification {
        +int user_id
        +str title
        +str message
        +str link
        +bool is_read
        +datetime created_at
    }
    class Setting {
        +str key
        +str value
    }

    User "1" *-- "0..*" Student
    User "1" *-- "0..*" Recruiter
    User "1" *-- "0..*" Admin
    User "1" *-- "0..*" Notification
    Company "1" *-- "0..*" Recruiter
    Company "1" *-- "0..*" Job
    Job "1" *-- "0..*" Application
    Student "1" *-- "0..*" Application
    Application "1" *-- "0..1" Interview
    Application "1" *-- "0..1" Offer
```

---

## 3. Route / Controller Map

| Blueprint  | URL prefix     | Key routes |
|------------|----------------|------------|
| `main`     | `/`            | index, about, announcements, notifications (view/mark-read), uploaded_file |
| `auth`     | `/auth`        | login, logout, student register, quick recruiter signup, forgot/reset/change password |
| `student`  | `/student`     | dashboard, profile, resume upload/delete, jobs, job_detail, apply, withdraw, applications, interviews (join), offers, download_offer |
| `recruiter`| `/recruiter`   | dashboard, company update, jobs CRUD, applicants, applicant_detail, schedule_interview, select/reject, offers (upload/download) |
| `admin`    | `/admin`       | dashboard, students/recruiters/companies/jobs/applications/interviews management, approvals, announcements, reports, settings, CSV exports |

All role-gated routes are protected by decorators (`login_required`, `student_required`, `recruiter_required`, `admin_required`) from `utils/decorators.py`.

---

## 4. Design Patterns Used

- **Factory pattern** — `create_app()` builds and configures the Flask app.
- **MVC separation** — models, blueprints (controllers), templates (views) are strictly separated.
- **Repository-style helpers** — `utils/queries.py` centralises statistics and eligibility logic so controllers stay thin.
- **Notification service** — `utils/notifications.py` is a single entry point for creating in-app notifications.
