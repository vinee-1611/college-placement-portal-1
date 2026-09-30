import io
import os
import sys
import traceback

# Clean database for a deterministic run
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "database.db"))
if os.path.exists(db_path):
    os.remove(db_path)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app

client = app.test_client()
passed, failed = [], []


def check(name, resp, expect_status=200):
    if resp.status_code == expect_status:
        passed.append(name)
    else:
        failed.append((name, resp.status_code))


try:
    # Public pages
    check("GET /", client.get("/"))
    check("GET /about", client.get("/about"))
    check("GET /announcements", client.get("/announcements"))

    # Auth pages
    check("GET login", client.get("/auth/login"))
    check("GET register", client.get("/auth/register"))
    check("GET register/recruiter", client.get("/auth/register/recruiter"))
    check("GET forgot-password", client.get("/auth/forgot-password"))

    # Unauthenticated dashboard should redirect to login
    check("GET /student/dashboard (anon)", client.get("/student/dashboard", follow_redirects=True))
    check("GET /admin/dashboard (anon)", client.get("/admin/dashboard", follow_redirects=True))

    # Admin login
    r = client.post("/auth/login", data={"email": "admin@placement.edu", "password": "Admin@123"}, follow_redirects=True)
    check("POST admin login", r)
    assert "Admin Dashboard" in r.get_data(as_text=True), "admin dashboard not rendered"

    # Admin pages
    for path in ["/admin/dashboard", "/admin/students", "/admin/recruiters",
                 "/admin/companies", "/admin/jobs", "/admin/applications",
                 "/admin/interviews", "/admin/announcements", "/admin/reports",
                 "/admin/reports?type=company", "/admin/reports?type=department",
                 "/admin/reports?type=cgpa", "/admin/reports?type=applications",
                 "/admin/reports?type=interviews", "/admin/settings",
                 "/admin/export/students.csv", "/admin/export/companies.csv",
                 "/admin/export/jobs.csv", "/admin/export/applications.csv"]:
        check(f"GET {path}", client.get(path))

    # Demo data seeded on first run populates Browse Jobs
    check("GET / (with demo jobs)", client.get("/"))
    with app.app_context():
        from models import Job as _Job
        demo_job_count = _Job.query.count()
    assert demo_job_count > 0, "demo jobs were not seeded"
    check("demo jobs seeded", client.get("/admin/dashboard"))

    # Quick recruiter signup: company details + vacancies + roles, auto login
    client.get("/auth/logout")
    r = client.post("/auth/register/recruiter", data={
        "email": "hr@techcorp.com", "password": "Hr@12345", "confirm_password": "Hr@12345",
        "company_name": "TechCorp Solutions", "location": "Hyderabad",
        "designation": "HR Manager", "experience": "2-5 years",
        "vacancies": "5", "roles": "Software Engineer, Data Analyst",
        "name": "Ravi Kumar",
    }, follow_redirects=True)
    check("POST recruiter quick signup", r)
    body = r.get_data(as_text=True)
    assert "Recruiter Dashboard" in body, "quick signup did not log the recruiter in"
    assert "go live" in body or "live" in body.lower()

    # Company is active straight away and one posting per role was created
    from models import Company as _Company
    from models import Job as _Job
    from models import User as _User
    with app.app_context():
        test_company = _Company.query.filter_by(name="TechCorp Solutions").first()
        assert test_company is not None, "company not created by quick signup"
        assert test_company.is_approved, "quick signup company should be live immediately"
        recruiter_job_ids = sorted(j.id for j in test_company.jobs)
        test_company_id = test_company.id
    assert len(recruiter_job_ids) == 2, f"expected one posting per role, got {recruiter_job_ids}"
    posted_job_id, analyst_job_id = recruiter_job_ids
    check("GET /recruiter/jobs (auto-posted)", client.get("/recruiter/jobs"))
    check("GET auto-posted job detail", client.get(f"/recruiter/jobs/{posted_job_id}"))

    # Recruiter pages
    for path in ["/recruiter/dashboard", "/recruiter/profile", "/recruiter/jobs",
                 "/recruiter/applicants", "/recruiter/interviews", "/recruiter/offers"]:
        check(f"GET {path}", client.get(path))

    # Admin can suspend an approved company, which blocks job posting
    client.get("/auth/logout")
    client.post("/auth/login", data={"email": "admin@placement.edu", "password": "Admin@123"})
    r = client.post(f"/admin/companies/{test_company_id}/approve", follow_redirects=True)
    check("POST admin suspend company", r)
    client.get("/auth/logout")
    client.post("/auth/login", data={"email": "hr@techcorp.com", "password": "Hr@12345"})
    check("GET /recruiter/jobs/new (suspended)", client.get("/recruiter/jobs/new"), expect_status=302)
    r = client.post("/recruiter/jobs/new", data={
        "title": "Software Engineer", "description": "Build web apps",
        "skills": "Python, Flask", "min_cgpa": "7", "max_backlogs": "2",
        "vacancies": "5", "package": "8", "location": "Hyderabad",
        "employment_type": "Full-time", "deadline": "2026-12-31",
    }, follow_redirects=True)
    check("POST job while suspended (blocked)", r)
    assert "must be approved" in r.get_data(as_text=True).lower()

    # Re-approve the company
    client.get("/auth/logout")
    client.post("/auth/login", data={"email": "admin@placement.edu", "password": "Admin@123"})
    r = client.post(f"/admin/companies/{test_company_id}/approve", follow_redirects=True)
    check("POST admin re-approve company", r)

    # Recruiter posts an extra job manually
    client.get("/auth/logout")
    client.post("/auth/login", data={"email": "hr@techcorp.com", "password": "Hr@12345"})
    r = client.post("/recruiter/jobs/new", data={
        "title": "Backend Engineer", "description": "Build web apps with Python",
        "skills": "Python, Flask, SQL", "min_cgpa": "7", "max_backlogs": "2",
        "vacancies": "5", "package": "8", "location": "Hyderabad",
        "employment_type": "Full-time", "deadline": "2026-12-31",
    }, follow_redirects=True)
    check("POST job (approved)", r)
    assert "posted successfully" in r.get_data(as_text=True).lower()
    check("GET /recruiter/jobs", client.get("/recruiter/jobs"))
    check("GET job applicants", client.get(f"/recruiter/jobs/{posted_job_id}/applicants"))

    # Student registration + login
    client.get("/auth/logout")
    r = client.post("/auth/register", data={
        "email": "student1@college.edu", "password": "Student@123", "confirm_password": "Student@123",
        "name": "Ananya Sharma", "roll_number": "20CS101", "department": "Computer Science Engineering",
        "batch": "2022-2026", "year": "4", "cgpa": "8.7", "backlogs": "0",
        "phone": "+919876543210", "skills": "Python, SQL, Java",
    }, follow_redirects=True)
    check("POST student register", r)

    r = client.post("/auth/login", data={"email": "student1@college.edu", "password": "Student@123"}, follow_redirects=True)
    check("POST student login", r)
    assert "Student Dashboard" in r.get_data(as_text=True), "student dashboard not rendered"

    # Student pages
    for path in ["/student/dashboard", "/student/profile", "/student/jobs",
                 "/student/applications", "/student/interviews", "/student/offers",
                 "/notifications"]:
        check(f"GET {path}", client.get(path))

    # Browse jobs: demo postings plus the recruiter's own are all listed
    r = client.get("/student/jobs")
    check("GET /student/jobs", r)
    jobs_body = r.get_data(as_text=True)
    assert "Software Engineer" in jobs_body, "recruiter's posted job missing from Browse Jobs"
    assert "Tata Consultancy Services" in jobs_body, "seeded demo company missing from Browse Jobs"
    check("GET job detail (student)", client.get(f"/student/jobs/{posted_job_id}"))

    # Apply without resume -> blocked
    r = client.post(f"/student/jobs/{posted_job_id}/apply", follow_redirects=True)
    check("apply without resume blocked", r)
    assert "resume" in r.get_data(as_text=True).lower()

    # Resume upload (bad extension)
    r = client.post("/student/resume/upload", data={"resume": (io.BytesIO(b"x"), "resume.txt")},
                    content_type="multipart/form-data", follow_redirects=True)
    check("resume upload rejected (txt)", r)
    assert "Only PDF files" in r.get_data(as_text=True)

    # Resume upload (valid PDF)
    r = client.post("/student/resume/upload", data={"resume": (io.BytesIO(b"%PDF-1.4 fake"), "resume.pdf")},
                    content_type="multipart/form-data", follow_redirects=True)
    check("resume upload ok", r)
    check("resume download", client.get("/student/resume/download"))

    # Apply for the job
    r = client.post(f"/student/jobs/{posted_job_id}/apply", follow_redirects=True)
    check("apply to job", r)
    assert "submitted" in r.get_data(as_text=True).lower()
    check("GET /student/applications (applied)", client.get("/student/applications"))
    check("GET /student/dashboard (after apply)", client.get("/student/dashboard"))

    with app.app_context():
        from models import Application as _Application
        application_id = (_Application.query
                          .filter_by(job_id=posted_job_id)
                          .order_by(_Application.id.desc())
                          .first()).id

    # Duplicate apply blocked
    r = client.post(f"/student/jobs/{posted_job_id}/apply", follow_redirects=True)
    check("duplicate apply blocked", r)
    assert "already applied" in r.get_data(as_text=True).lower()

    # Change password wrong current
    r = client.post("/auth/change-password",
                    data={"current_password": "wrong", "new_password": "New@12345", "confirm_password": "New@12345"},
                    follow_redirects=True)
    check("change password wrong current", r)

    # Forgot password
    client.get("/auth/logout")
    r = client.post("/auth/forgot-password", data={"email": "student1@college.edu"}, follow_redirects=True)
    check("POST forgot-password", r)
    assert "password reset link" in r.get_data(as_text=True).lower()

    # Recruiter shortlists applicant
    client.post("/auth/login", data={"email": "hr@techcorp.com", "password": "Hr@12345"})
    check("GET applicant detail", client.get(f"/recruiter/applicants/{application_id}"))
    r = client.post(f"/recruiter/applicants/{application_id}/status", data={"action": "shortlist"}, follow_redirects=True)
    check("POST shortlist applicant", r)
    r = client.post(f"/recruiter/applicants/{application_id}/interview", data={
        "interview_date": "2026-09-15", "interview_time": "10:30", "round": "Technical",
        "mode": "Online", "venue": "https://meet.example.com", "remarks": "Aptitude passed",
    }, follow_redirects=True)
    check("POST schedule interview", r)
    check("GET /recruiter/interviews", client.get("/recruiter/interviews"))

    # Recruiter selects the applicant and uploads offer letter
    r = client.post(f"/recruiter/applicants/{application_id}/select", follow_redirects=True)
    check("POST select applicant", r)
    r = client.post(f"/recruiter/applicants/{application_id}/offer", data={
        "package": "9", "offer_letter": (io.BytesIO(b"%PDF-1.4 offer"), "offer.pdf"),
    }, content_type="multipart/form-data", follow_redirects=True)
    check("POST upload offer", r)
    check("GET /recruiter/offers", client.get("/recruiter/offers"))

    # Student sees offer + interview
    client.get("/auth/logout")
    client.post("/auth/login", data={"email": "student1@college.edu", "password": "Student@123"})
    with app.app_context():
        from models import Offer as _Offer
        offer_id = _Offer.query.filter_by(application_id=application_id).first().id
    check("GET /student/offers", client.get("/student/offers"))
    check("GET /student/interviews", client.get("/student/interviews"))
    check("GET offer download", client.get(f"/student/offers/{offer_id}/download"))

    # Role isolation
    client.get("/auth/logout")
    r = client.get("/student/dashboard", follow_redirects=True)
    check("anon /student redirects", r)
    check("anon /recruiter redirects", client.get("/recruiter/dashboard", follow_redirects=True))
    check("anon /admin redirects", client.get("/admin/dashboard", follow_redirects=True))

    # 404 page renders with 404 status
    r = client.get("/does-not-exist")
    check("GET 404 page", r, expect_status=404)
    assert "Page Not Found" in r.get_data(as_text=True)

    print(f"PASSED: {len(passed)}")
    for name in passed:
        print("  OK", name)
    if failed:
        print("FAILED:")
        for name, code in failed:
            print("  FAIL", name, code)
except Exception:
    traceback.print_exc()
    failed.append(("EXCEPTION", -1))

print(f"\nTOTAL: {len(passed)} passed, {len(failed)} failed")
