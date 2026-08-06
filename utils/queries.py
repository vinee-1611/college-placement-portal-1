"""
queries.py

Reusable query builders for eligibility, dashboard stats and reports.
"""

from datetime import date

from models import Application, Company, Job, Student


def is_eligible(student, job):
    """Return True if the student meets the job's eligibility criteria."""
    if student.cgpa < job.min_cgpa:
        return False
    if student.backlogs > job.max_backlogs:
        return False
    return True


def job_visible(job):
    """A job is visible to students only if the company is approved and the job is open."""
    return job.is_open and job.company.is_approved


def eligible_jobs_query(student):
    """Query of all open, visible jobs the student is eligible for."""
    today = date.today()
    query = (Job.query
             .join(Company)
             .filter(Company.is_approved.is_(True),
                     Job.is_active.is_(True),
                     Job.deadline >= today)
             .order_by(Job.deadline.asc()))
    jobs = [j for j in query.all() if is_eligible(student, j)]
    return jobs


def already_applied(student, job):
    return Application.query.filter_by(student_id=student.id,
                                       job_id=job.id).first() is not None


def student_stats(student):
    applied = student.applications
    applied_count = len(applied)
    shortlisted = sum(1 for a in applied if a.status == "shortlisted")
    interviews = sum(1 for a in applied for _ in a.interviews)
    selected = sum(1 for a in applied if a.status in ("selected", "offer"))
    return {
        "applied": applied_count,
        "shortlisted": shortlisted,
        "interviews": interviews,
        "selected": selected,
    }


def company_stats(company):
    jobs = company.jobs
    job_ids = [j.id for j in jobs]
    applications = Application.query.filter(Application.job_id.in_(job_ids)).all() if job_ids else []
    shortlisted = sum(1 for a in applications if a.status == "shortlisted")
    selected = sum(1 for a in applications if a.status in ("selected", "offer"))
    return {
        "jobs": len(jobs),
        "applications": len(applications),
        "shortlisted": shortlisted,
        "selected": selected,
    }


def app_stats():
    total_students = Student.query.count()
    placed_students = Student.query.filter_by(placed=True).count()
    companies = Company.query.count()
    approved_companies = Company.query.filter_by(is_approved=True).count()
    jobs = Job.query.count()
    applications = Application.query.count()
    selected = Application.query.filter(Application.status.in_(["selected", "offer"])).count()
    ratio = (round((selected / applications) * 100, 1)
             if applications else 0.0)
    return {
        "students": total_students,
        "placed": placed_students,
        "companies": companies,
        "approved_companies": approved_companies,
        "jobs": jobs,
        "applications": applications,
        "selected": selected,
        "ratio": ratio,
    }
