# User Manual

This manual explains the College Placement Portal from the perspective of all three user roles. A navigation bar (topbar) is present on every page; after login, a sidebar shows the role-specific menu.

---

## 1. Common Features

### 1.1 Registration & Login

| Role      | How to register                                             | What happens next |
|-----------|-------------------------------------------------------------|-------------------|
| Student   | Public → **Register** → student form (name, roll number, email, password) | Can log in immediately and complete the profile. |
| Recruiter | Public → **Recruiter sign-up** → form (name, email, company name, company details, password) | Company is created with status **Pending**. Recruiter can log in; jobs can be posted only after the admin approves the company. |
| Admin     | Seeded automatically. Login with `admin@placement.edu` / `Admin@123`. | Full control panel. |

All passwords are stored as irreversible hashes and must meet the strength policy (minimum 8 characters, at least one uppercase letter, one lowercase letter, one digit and one special symbol).

### 1.2 Forgot Password

On the login page choose **Forgot password?** → enter email → the system shows a reset link (demo mode; in production this would be emailed) → set a new password → login.

### 1.3 Change Password

While logged in, use **Change password** in the user menu to update the current password.

### 1.4 Notifications

The bell icon in the topbar shows unread notifications. Clicking a notification marks it read and opens the related page. Mark all read clears them.

---

## 2. Student Panel

### 2.1 Dashboard
- Placement statistics (placed/total, average package, interviews scheduled).
- Announcements from the placement office.
- Recently posted jobs for which you are eligible.

### 2.2 Profile
Fill and update: personal details, contact, department, batch, year of study, CGPA, number of backlogs, skills, bio, and links. Upload a profile photo.

### 2.3 Resume Management
- Upload a resume (PDF only). A resume is **required** before applying to any job.
- Download or delete the uploaded resume at any time.

### 2.4 Browse Jobs
A list of all **active** jobs for which you are **eligible** (deadline not passed, CGPA ≥ required, backlogs ≤ allowed, not already applied). Open a job to read the full description and click **Apply**.

### 2.5 Applications
Track every application you submitted with its current status:
**Applied → Shortlisted → Interview scheduled → Selected / Rejected**.

- While status is *Applied* you may **Withdraw** the application.
- When shortlisted or scheduled, an interview card shows date/time/location and mode.
- You may **Join** the interview to mark attendance.

### 2.6 Offers
View your selection result and download the official **offer letter** (PDF) uploaded by the recruiter.

### 2.7 Notifications
All application updates, interview schedules and announcements arrive here and via the bell icon.

---

## 3. Recruiter Panel

### 3.1 Dashboard
- Your company overview and approval status.
- Job posting activity and total applicants.
- Counts of shortlisted and selected candidates.

### 3.2 Company Profile
Edit company name, industry, website, contact, location and description. The admin must **approve** the company before you can post jobs.

### 3.3 Jobs
Create, edit, activate/deactivate and delete job postings. Each job specifies title, description, skills, minimum CGPA, maximum backlogs, vacancies, package (LPA), location, employment type, and application deadline.

### 3.4 Applicants
For any of your jobs, view all applicants in one place, search by name/roll, and update status:
- **Shortlist** — move a candidate forward.
- **Reject** — close that application.

### 3.5 Interviews
- Schedule an interview for a shortlisted applicant: date, time, location/mode (online/offline), and notes. The student is notified automatically.
- Update the interview status; once complete, **select** or reject the candidate.

### 3.6 Offers
Upload a signed **offer letter (PDF)** for a selected candidate. The student can download it from their Offers page.

---

## 4. Placement Officer (Admin) Panel

### 4.1 Dashboard
Live charts and cards: students, recruiters, companies, jobs, applications, interviews, placed students, average package, and monthly placement trend.

### 4.2 Students
View and search all registered students, open a detailed profile (with resume), and delete a student if required.

### 4.3 Recruiters
View recruiter accounts and their companies; **approve** or reject company registrations.

### 4.4 Companies
Manage every company: approve/reject, edit, or remove. A company's status controls whether its recruiters can post jobs.

### 4.5 Jobs
Review, edit, activate/deactivate, or delete any job posting across all companies.

### 4.6 Applications
See every application in the system, filter by job or status, and update status where needed.

### 4.7 Interviews
Manage all scheduled interviews and their outcomes.

### 4.8 Announcements
Publish announcements (title + message) that are immediately visible to all students and recruiters.

### 4.9 Reports
Generated reports (filterable by academic year):
- Placed students by department
- Company-wise placements
- Department-wise statistics
- CGPA distribution of placed students
- Applications summary
- Interview summary

### 4.10 Settings
Edit platform settings such as the application name and tagline (used in the browser title and public pages).

### 4.11 CSV Export
One-click CSV downloads for students, recruiters, companies, jobs, and applications — useful for offline records.

---

## 5. Useful Shortcuts

| Task                                   | Where                                  |
|----------------------------------------|----------------------------------------|
| Apply to a job                         | Student → Browse Jobs → Apply          |
| Withdraw an application                | Student → Applications → Withdraw      |
| Upload resume                          | Student → Profile                      |
| Approve a company                      | Admin → Companies / Recruiters         |
| Post a job                             | Recruiter → Jobs → New Job (after approval) |
| Schedule an interview                  | Recruiter → Applicants → Schedule Interview |
| Upload offer letter                    | Recruiter → Applicants → Selected → Upload Offer |
| Publish announcement                   | Admin → Announcements                  |
| View placement statistics              | Student / Recruiter → Dashboard; Admin → Reports |
| Export data                            | Admin → Reports → Export CSV            |
