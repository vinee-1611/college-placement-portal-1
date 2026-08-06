# UML & DFD Diagrams

The diagrams below use [Mermaid](https://mermaid.js.org/) syntax. Render them in any Mermaid-compatible editor (GitHub, VS Code with Mermaid plugin, or mermaid.live).

---

## 1. Use Case Diagram

```mermaid
graph TD
    subgraph System[College Placement Portal]
        UC1[Register / Login]
        UC2[Manage Profile & Resume]
        UC3[Browse & Apply to Jobs]
        UC4[Track Applications]
        UC5[View Interviews & Offers]
        UC6[Manage Company Profile]
        UC7[Post / Manage Jobs]
        UC8[Review & Shortlist Applicants]
        UC9[Schedule Interviews & Upload Offers]
        UC10[Approve Companies & Recruiters]
        UC11[Manage Users & Jobs]
        UC12[Publish Announcements]
        UC13[View Reports & Export CSV]
    end

    Student --> UC1
    Student --> UC2
    Student --> UC3
    Student --> UC4
    Student --> UC5

    Recruiter --> UC1
    Recruiter --> UC6
    Recruiter --> UC7
    Recruiter --> UC8
    Recruiter --> UC9

    Admin --> UC1
    Admin --> UC10
    Admin --> UC11
    Admin --> UC12
    Admin --> UC13

    UC4 -. includes .-> UC3
    UC5 -. includes .-> UC4
    UC9 -. includes .-> UC8
```

---

## 2. Class Diagram (Core Entities)

```mermaid
classDiagram
    class User {
        +id
        +email
        +password_hash
        +role
        +is_active
        +created_at
        +set_password(password)
        +check_password(password)
    }
    class Student {
        +user_id
        +name
        +roll_number
        +department
        +batch
        +year
        +cgpa
        +backlogs
        +skills
        +resume_path
        +is_placed
    }
    class Recruiter {
        +user_id
        +name
        +designation
        +company_id
    }
    class Admin {
        +user_id
        +name
    }
    class Company {
        +name
        +industry
        +website
        +is_approved
    }
    class Job {
        +company_id
        +title
        +description
        +skills
        +min_cgpa
        +max_backlogs
        +vacancies
        +package
        +deadline
        +is_active
    }
    class Application {
        +student_id
        +job_id
        +status
        +applied_at
    }
    class Interview {
        +application_id
        +interview_date
        +time
        +mode
        +location
        +status
        +result
    }
    class Offer {
        +application_id
        +package
        +offer_path
    }
    class Announcement {
        +title
        +message
        +created_at
    }
    class Notification {
        +user_id
        +title
        +message
        +link
        +is_read
    }

    User "1" -- "0..*" Student : has
    User "1" -- "0..*" Recruiter : has
    User "1" -- "0..*" Admin : has
    Company "1" -- "0..*" Recruiter : employs
    Company "1" -- "0..*" Job : posts
    Job "1" -- "0..*" Application : receives
    Student "1" -- "0..*" Application : submits
    Application "1" -- "0..1" Interview : has
    Application "1" -- "0..1" Offer : has
    User "1" -- "0..*" Notification : receives
```

---

## 3. Sequence Diagram — Student Applies to a Job

```mermaid
sequenceDiagram
    participant S as Student
    participant B as Browser
    participant A as Flask App
    participant D as Database

    S->>B: Login (email + password)
    B->>A: POST /auth/login
    A->>D: Verify credentials
    D-->>A: User found
    A-->>B: Session cookie + redirect to dashboard

    S->>B: Browse Jobs
    B->>A: GET /student/jobs
    A->>D: Query eligible active jobs
    D-->>A: Job list
    A-->>B: Render jobs page

    S->>B: Click Apply on job
    B->>A: POST /student/jobs/<id>/apply
    A->>D: Check resume + duplicate + eligibility
    D-->>A: Valid
    A->>D: INSERT application
    A->>D: INSERT notification for recruiter
    A-->>B: Success flash + redirect to Applications
```

---

## 4. Sequence Diagram — Recruiter Schedules Interview

```mermaid
sequenceDiagram
    participant R as Recruiter
    participant B as Browser
    participant A as Flask App
    participant D as Database

    R->>B: Login
    B->>A: POST /auth/login
    A-->>B: Session established

    R->>B: Open applicants of a job
    B->>A: GET /recruiter/applicants?job_id=...
    A->>D: Query applications
    D-->>A: Applicant list

    R->>B: Schedule interview for shortlisted applicant
    B->>A: POST /recruiter/applications/<id>/schedule-interview
    A->>D: Check applicant is shortlisted
    A->>D: INSERT interview (date, time, mode)
    A->>D: UPDATE application -> Interview Scheduled
    A->>D: INSERT notification for student
    A-->>B: Redirect with success message
```

---

## 5. Activity Diagram — Application Lifecycle

```mermaid
flowchart TD
    Start([Student browses eligible jobs]) --> Apply[Click Apply]
    Apply --> HasResume{Resume uploaded?}
    HasResume -- No --> Upload[Upload resume in profile] --> Apply
    HasResume -- Yes --> CheckDup{Already applied?}
    CheckDup -- Yes --> Stop([Application rejected with message])
    CheckDup -- No --> Create[Application created - status APPLIED]
    Create --> Review[Recruiter reviews applicants]
    Review --> Choice{Recruiter decision}
    Choice -- Shortlist --> Interview[Recruiter schedules interview]
    Choice -- Reject --> Rejected([Status REJECTED - student notified])
    Interview --> Attend[Student joins interview]
    Attend --> Result{Interview result}
    Result -- Selected --> Offer[Recruiter uploads offer letter]
    Result -- Not selected --> Rejected2([Status REJECTED - student notified])
    Offer --> Done([Student downloads offer - is_placed = True])
```

---

## 6. Data Flow Diagram — Level 0 (Context)

```mermaid
flowchart LR
    subgraph External
        St[Student]
        Re[Recruiter]
        Ad[Placement Officer]
    end

    St -- "Profile, resume, job applications" --> CPS
    Re -- "Company, jobs, interviews, offers" --> CPS
    Ad -- "Approvals, announcements, reports" --> CPS

    subgraph CPS[College Placement Portal]
        Core["Single online system (Flask + SQLite)"]
    end

    CPS -- "Eligible jobs, status updates, offers" --> St
    CPS -- "Applicant lists, notifications, results" --> Re
    CPS -- "Statistics, CSV exports" --> Ad
```

---

## 7. Data Flow Diagram — Level 1

```mermaid
flowchart TD
    St[Student] --> P1[Authentication]
    Re[Recruiter] --> P1
    Ad[Placement Officer] --> P1
    P1 --> DB[(User Database)]

    St --> P2[Profile & Resume Management] --> DB2[(Student Records)]
    Re --> P3[Company & Job Management] --> DB3[(Company / Job Records)]
    St --> P4[Job Search & Application] --> DB2
    P4 --> DB3
    Re --> P5[Applicant Review & Shortlist] --> DB2
    Re --> P6[Interview Scheduling] --> DB4[(Interview Records)]
    Re --> P7[Offer Management] --> DB5[(Offer Records)]
    P6 --> DB2
    Ad --> P8[Approvals & User Management] --> DB2
    Ad --> P9[Announcements] --> DB2
    Ad --> P10[Reports & Export] --> DB2
    Ad --> P10
```
