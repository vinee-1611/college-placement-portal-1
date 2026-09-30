# User Manual

This manual explains the College Placement Portal from the perspective of all three user roles. A navigation bar (topbar) is present on every page; after login, a sidebar shows the role-specific menu.

---

## 1. Common Features

### 1.1 Registration & Login

| Role      | How to register                                             | What happens next |
|-----------|-------------------------------------------------------------|-------------------|
| Student   | Public → **Register** → student form (name, roll number, email, password) | Can log in immediately and complete the profile. |
| Recruiter | Public → **Post Jobs** → short form (company name, company location, roles you are hiring for, total vacancies, your designation, your experience, email, password) | The company, your account and one live job posting per listed role are created automatically, vacancies are split across the roles, and you are logged straight in. |
| Admin     | Seeded automatically. Login with `admin@placement.edu` / `Admin@123`. | Full control panel. |

All passwords are stored as irreversible hashes and must meet the strength policy (minimum 8 characters, at least one uppercase letter, one lowercase letter, one digit and one special symbol).

On first run the portal seeds demo data so **Browse Jobs** is never empty: 10 partner companies with 19 open positions, all in the 3.4–5.0 LPA band. The demo recruiters share the password `Recruiter@123`, e.g. `tcs.recruiter@demo.edu` / `Recruiter@123`.

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

### 3.1 Getting Started
Sign-up is a single screen — you enter your company name, company location, the roles you are hiring for, your total vacancies, your designation and your experience, plus an email and password to log in with. The portal then:
1. Creates your company and marks it **live** so your postings show up in student Browse Jobs.
2. Creates your recruiter account and signs you in.
3. Creates one job posting per role you listed, splitting your vacancies evenly across them (a role shows **On request** until you add a package).

Use **My Jobs** to refine the generated postings — add the full description, required skills, package, eligibility criteria and a deadline.

### 3.2 Dashboard
- Your company overview and status.
- Job posting activity and total applicants.
- Counts of shortlisted and selected candidates.

### 3.3 Company Profile
Edit company name, industry, website, contact, location and description, and update your own name, designation, experience and phone. The admin can suspend the company at any time, which immediately blocks further job posting.

### 3.4 Jobs
Create, edit, activate/deactivate and delete job postings. Each job specifies title, description, skills, minimum CGPA, maximum backlogs, vacancies, package (LPA), location, employment type, and application deadline.

### 3.5 Applicants
For any of your jobs, view all applicants in one place, search by name/roll, and update status:
- **Shortlist** — move a candidate forward.
- **Reject** — close that application.

### 3.6 Interviews
- Schedule an interview for a shortlisted applicant: date, time, location/mode (online/offline), and notes. The student is notified automatically.
- Update the interview status; once complete, **select** or reject the candidate.

### 3.7 Offers
Upload a signed **offer letter (PDF)** for a selected candidate. The student can download it from their Offers page.

---

## 4. Placement Officer (Admin) Panel

### 4.1 Dashboard
Live charts and cards: students, recruiters, companies, jobs, applications, interviews, placed students, average package, and monthly placement trend.

### 4.2 Students
View and search all registered students, open a detailed profile (with resume), and delete a student if required.

### 4.3 Recruiters
View recruiter accounts and their companies, including the designation and experience each recruiter signed up with.

### 4.4 Companies
Manage every company: suspend or reinstate it, edit, or remove. A company's status controls whether its recruiters can post jobs — suspending one immediately hides its jobs from student Browse Jobs.

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
| Post a job                             | Recruiter → Jobs → New Job |
| Schedule an interview                  | Recruiter → Applicants → Schedule Interview |
| Upload offer letter                    | Recruiter → Applicants → Selected → Upload Offer |
| Publish announcement                   | Admin → Announcements                  |
| View placement statistics              | Student / Recruiter → Dashboard; Admin → Reports |
| Export data                            | Admin → Reports → Export CSV            |
