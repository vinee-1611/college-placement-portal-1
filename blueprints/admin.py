"""
blueprints/admin.py

Admin (placement officer) features: dashboard, manage students / recruiters /
companies / jobs, review applications, interviews, announcements, reports,
system settings, and CSV export.
"""

import csv
import io

from flask import (Blueprint, abort, flash, redirect, render_template,
                   request, Response, url_for)
from flask_login import current_user, login_required

from extensions import db
from models import (Admin, Announcement, Application, Company, Interview,
                    Job, Recruiter, Setting, Student, User)
from utils.decorators import role_required
from utils.queries import app_stats
from utils.validators import is_strong_password

admin_bp = Blueprint("admin", __name__)

ANNOUNCEMENT_CATEGORIES = ["drive", "result", "interview", "news"]
PAGE_SIZE = 15


def current_admin():
    return current_user.admin


@admin_bp.route("/dashboard")
@login_required
@role_required("admin")
def dashboard():
    stats = app_stats()

    applications = Application.query.order_by(Application.applied_at.desc()).limit(8).all()
    pending_companies = Company.query.filter_by(is_approved=False).count()
    pending_students = Student.query.count()

    from sqlalchemy import func
    applications_by_status = (db.session.query(Application.status, func.count(Application.id))
                              .group_by(Application.status).all())
    placements_by_department = (db.session.query(Student.department, func.count(Student.id))
                                .filter(Student.placed.is_(True))
                                .group_by(Student.department).all())
    jobs_by_company = (db.session.query(Company.name, func.count(Job.id))
                       .join(Job, Job.company_id == Company.id)
                       .group_by(Company.name).all())

    return render_template(
        "dashboard/admin_dashboard.html",
        stats=stats,
        applications=applications,
        pending_companies=pending_companies,
        pending_students=pending_students,
        applications_by_status=applications_by_status,
        placements_by_department=placements_by_department,
        jobs_by_company=jobs_by_company,
    )


# --------------------------------------------------------------------------- #
# Students
# --------------------------------------------------------------------------- #
@admin_bp.route("/students")
@login_required
@role_required("admin")
def students():
    page = request.args.get("page", 1, type=int)
    search = request.args.get("q", "").strip()
    department = request.args.get("department", "").strip()
    batch = request.args.get("batch", "").strip()

    query = Student.query.join(User)
    if search:
        term = f"%{search.lower()}%"
        query = query.filter(db.or_(Student.name.ilike(term),
                                    Student.roll_number.ilike(term),
                                    User.email.ilike(term)))
    if department:
        query = query.filter_by(department=department)
    if batch:
        query = query.filter_by(batch=batch)

    departments = [d[0] for d in db.session.query(Student.department).distinct()]
    batches = [b[0] for b in db.session.query(Student.batch).distinct()]

    items = query.order_by(Student.name.asc()).paginate(
        page=page, per_page=PAGE_SIZE, error_out=False)
    return render_template("admin/students.html", students=items,
                           departments=departments, batches=batches,
                           search=search, department=department, batch=batch)


@admin_bp.route("/students/<int:student_id>")
@login_required
@role_required("admin")
def student_detail(student_id):
    student = Student.query.get_or_404(student_id)
    return render_template("admin/student_detail.html", student=student)


@admin_bp.route("/students/<int:student_id>/toggle", methods=["POST"])
@login_required
@role_required("admin")
def student_toggle(student_id):
    student = Student.query.get_or_404(student_id)
    user = student.user
    user.is_active = not user.is_active
    db.session.commit()
    state = "activated" if user.is_active else "deactivated"
    flash(f"Account for {student.name} {state}.", "success")
    return redirect(request.referrer or url_for("admin.students"))


@admin_bp.route("/students/<int:student_id>/reset-password", methods=["POST"])
@login_required
@role_required("admin")
def student_reset_password(student_id):
    student = Student.query.get_or_404(student_id)
    new_password = request.form.get("new_password", "").strip()
    if not is_strong_password(new_password):
        flash("Password must be at least 8 characters with upper, lower, number and symbol.", "danger")
        return redirect(request.referrer or url_for("admin.students"))
    student.user.set_password(new_password)
    db.session.commit()
    flash(f"Password for {student.name} reset.", "success")
    return redirect(request.referrer or url_for("admin.students"))


# --------------------------------------------------------------------------- #
# Recruiters & Companies
# --------------------------------------------------------------------------- #
@admin_bp.route("/recruiters")
@login_required
@role_required("admin")
def recruiters():
    page = request.args.get("page", 1, type=int)
    search = request.args.get("q", "").strip()
    query = Recruiter.query.join(User).join(Company)
    if search:
        term = f"%{search.lower()}%"
        query = query.filter(db.or_(Recruiter.name.ilike(term),
                                    Company.name.ilike(term),
                                    User.email.ilike(term)))
    items = query.order_by(Recruiter.created_at.desc()).paginate(
        page=page, per_page=PAGE_SIZE, error_out=False)
    return render_template("admin/recruiters.html", recruiters=items, search=search)


@admin_bp.route("/recruiters/<int:recruiter_id>/approve", methods=["POST"])
@login_required
@role_required("admin")
def recruiter_approve(recruiter_id):
    recruiter = Recruiter.query.get_or_404(recruiter_id)
    recruiter.company.is_approved = True

    from utils.notifications import notify
    notify(recruiter.user_id, "Company approved",
           f"{recruiter.company.name} has been approved. You can now post jobs.",
           url_for("recruiter.jobs"))
    db.session.commit()
    flash(f"{recruiter.company.name} approved.", "success")
    return redirect(request.referrer or url_for("admin.recruiters"))


@admin_bp.route("/recruiters/<int:recruiter_id>/toggle", methods=["POST"])
@login_required
@role_required("admin")
def recruiter_toggle(recruiter_id):
    recruiter = Recruiter.query.get_or_404(recruiter_id)
    user = recruiter.user
    user.is_active = not user.is_active
    db.session.commit()
    state = "activated" if user.is_active else "deactivated"
    flash(f"Account for {recruiter.name} {state}.", "success")
    return redirect(request.referrer or url_for("admin.recruiters"))


@admin_bp.route("/companies")
@login_required
@role_required("admin")
def companies():
    page = request.args.get("page", 1, type=int)
    search = request.args.get("q", "").strip()
    approval = request.args.get("approval", "").strip()
    query = Company.query
    if search:
        term = f"%{search.lower()}%"
        query = query.filter(db.or_(Company.name.ilike(term),
                                    Company.industry.ilike(term),
                                    Company.location.ilike(term)))
    if approval in ("approved", "pending"):
        query = query.filter_by(is_approved=(approval == "approved"))
    items = query.order_by(Company.created_at.desc()).paginate(
        page=page, per_page=PAGE_SIZE, error_out=False)
    return render_template("admin/companies.html", companies=items,
                           search=search, approval=approval)


@admin_bp.route("/companies/<int:company_id>/approve", methods=["POST"])
@login_required
@role_required("admin")
def company_approve(company_id):
    company = Company.query.get_or_404(company_id)
    company.is_approved = not company.is_approved

    from utils.notifications import notify
    for recruiter in company.recruiters:
        notify(recruiter.user_id,
               "Company status changed",
               f"{company.name} is now {'approved' if company.is_approved else 'pending'}.",
               url_for("recruiter.profile"))
    db.session.commit()
    state = "approved" if company.is_approved else "marked pending"
    flash(f"Company {company.name} {state}.", "success")
    return redirect(request.referrer or url_for("admin.companies"))


# --------------------------------------------------------------------------- #
# Jobs
# --------------------------------------------------------------------------- #
@admin_bp.route("/jobs")
@login_required
@role_required("admin")
def jobs():
    page = request.args.get("page", 1, type=int)
    search = request.args.get("q", "").strip()
    company_filter = request.args.get("company", "").strip()
    query = Job.query.join(Company)
    if search:
        term = f"%{search.lower()}%"
        query = query.filter(db.or_(Job.title.ilike(term),
                                    Company.name.ilike(term),
                                    Job.location.ilike(term)))
    if company_filter:
        try:
            query = query.filter_by(company_id=int(company_filter))
        except ValueError:
            pass
    items = query.order_by(Job.created_at.desc()).paginate(
        page=page, per_page=PAGE_SIZE, error_out=False)
    companies = Company.query.order_by(Company.name.asc()).all()
    return render_template("admin/jobs.html", jobs=items, companies=companies,
                           search=search, company_filter=company_filter)


@admin_bp.route("/jobs/<int:job_id>/toggle", methods=["POST"])
@login_required
@role_required("admin")
def job_toggle(job_id):
    job = Job.query.get_or_404(job_id)
    job.is_active = not job.is_active
    db.session.commit()
    state = "activated" if job.is_active else "deactivated"
    flash(f"Job '{job.title}' {state}.", "success")
    return redirect(request.referrer or url_for("admin.jobs"))


@admin_bp.route("/jobs/<int:job_id>/delete", methods=["POST"])
@login_required
@role_required("admin")
def job_delete(job_id):
    job = Job.query.get_or_404(job_id)
    db.session.delete(job)
    db.session.commit()
    flash(f"Job '{job.title}' deleted.", "info")
    return redirect(request.referrer or url_for("admin.jobs"))


# --------------------------------------------------------------------------- #
# Applications & Interviews
# --------------------------------------------------------------------------- #
@admin_bp.route("/applications")
@login_required
@role_required("admin")
def applications():
    page = request.args.get("page", 1, type=int)
    search = request.args.get("q", "").strip()
    status_filter = request.args.get("status", "").strip()
    query = Application.query.join(Application.student).join(Application.job)
    if search:
        term = f"%{search.lower()}%"
        query = query.filter(db.or_(Student.name.ilike(term),
                                    Student.roll_number.ilike(term),
                                    Job.title.ilike(term)))
    if status_filter:
        query = query.filter_by(status=status_filter)
    items = query.order_by(Application.applied_at.desc()).paginate(
        page=page, per_page=PAGE_SIZE, error_out=False)
    return render_template("admin/applications.html", applications=items,
                           search=search, status_filter=status_filter)


@admin_bp.route("/interviews")
@login_required
@role_required("admin")
def interviews():
    page = request.args.get("page", 1, type=int)
    search = request.args.get("q", "").strip()
    query = (Interview.query
             .join(Application)
             .join(Application.student)
             .join(Application.job))
    if search:
        term = f"%{search.lower()}%"
        query = query.filter(db.or_(Student.name.ilike(term),
                                    Job.title.ilike(term),
                                    Company.name.ilike(term)))
    items = query.order_by(Interview.interview_date.desc()).paginate(
        page=page, per_page=PAGE_SIZE, error_out=False)
    return render_template("admin/interviews.html", interviews=items, search=search)


@admin_bp.route("/interviews/<int:interview_id>/complete", methods=["POST"])
@login_required
@role_required("admin")
def interview_complete(interview_id):
    interview = Interview.query.get_or_404(interview_id)
    interview.status = "Completed"
    interview.remarks = request.form.get("remarks", interview.remarks)
    db.session.commit()
    flash("Interview marked as completed.", "success")
    return redirect(request.referrer or url_for("admin.interviews"))


# --------------------------------------------------------------------------- #
# Announcements
# --------------------------------------------------------------------------- #
@admin_bp.route("/announcements", methods=["GET", "POST"])
@login_required
@role_required("admin")
def announcements():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        category = request.form.get("category", "news").strip()
        if not title or not content:
            flash("Title and content are required.", "danger")
        elif category not in ANNOUNCEMENT_CATEGORIES:
            flash("Invalid category.", "danger")
        else:
            announcement = Announcement(admin_id=current_admin().id,
                                        title=title, content=content,
                                        category=category)
            db.session.add(announcement)

            student_ids = [s.user_id for s in Student.query.all()]
            recruiter_ids = [r.user_id for r in Recruiter.query.all()]
            from utils.notifications import notify_many
            notify_many(student_ids + recruiter_ids, "New announcement",
                        title, url_for("main.announcements"))
            db.session.commit()
            flash("Announcement published.", "success")
            return redirect(url_for("admin.announcements"))

    page = request.args.get("page", 1, type=int)
    items = Announcement.query.order_by(Announcement.created_at.desc()).paginate(
        page=page, per_page=PAGE_SIZE, error_out=False)
    return render_template("admin/announcements.html", announcements=items,
                           categories=ANNOUNCEMENT_CATEGORIES)


@admin_bp.route("/announcements/<int:announcement_id>/delete", methods=["POST"])
@login_required
@role_required("admin")
def announcement_delete(announcement_id):
    announcement = Announcement.query.get_or_404(announcement_id)
    db.session.delete(announcement)
    db.session.commit()
    flash("Announcement deleted.", "info")
    return redirect(url_for("admin.announcements"))


# --------------------------------------------------------------------------- #
# Reports
# --------------------------------------------------------------------------- #
@admin_bp.route("/reports")
@login_required
@role_required("admin")
def reports():
    report_type = request.args.get("type", "placed").strip()
    from sqlalchemy import func

    data = None
    columns = []

    if report_type == "placed":
        columns = ["Roll No", "Name", "Department", "CGPA", "Job", "Company", "Package", "Offer Date"]
        rows = []
        for application in Application.query.filter(
                Application.status.in_(["selected", "offer"])).order_by(Application.applied_at.desc()).all():
            offer = application.offer
            rows.append({
                "roll": application.student.roll_number,
                "name": application.student.name,
                "department": application.student.department,
                "cgpa": application.student.cgpa,
                "job": application.job.title,
                "company": application.job.company.name,
                "package": offer.package if offer else application.job.package,
                "date": offer.offer_date if offer else application.applied_at.date(),
            })
        data = rows

    elif report_type == "company":
        columns = ["Company", "Approved", "Jobs", "Applications", "Selected"]
        rows = []
        for company in Company.query.order_by(Company.name).all():
            job_ids = [j.id for j in company.jobs]
            applications = (Application.query.filter(Application.job_id.in_(job_ids)).count()
                            if job_ids else 0)
            selected = (Application.query
                        .filter(Application.job_id.in_(job_ids),
                                Application.status.in_(["selected", "offer"])).count()
                        if job_ids else 0)
            rows.append({
                "name": company.name,
                "approved": company.is_approved,
                "jobs": len(company.jobs),
                "applications": applications,
                "selected": selected,
            })
        data = rows

    elif report_type == "department":
        columns = ["Department", "Students", "Placed", "Placement %"]
        rows = []
        for dept, total in db.session.query(Student.department, func.count(Student.id)).group_by(Student.department).all():
            placed = Student.query.filter_by(department=dept, placed=True).count()
            pct = round(placed / total * 100, 1) if total else 0.0
            rows.append({"name": dept, "total": total, "placed": placed, "pct": pct})
        data = rows

    elif report_type == "cgpa":
        buckets = [(9, 10), (8, 9), (7, 8), (6, 7), (0, 6)]
        columns = ["CGPA Range", "Students", "Placed", "Placement %"]
        rows = []
        for low, high in buckets:
            students = Student.query.filter(Student.cgpa >= low, Student.cgpa < high).all()
            total = len(students)
            placed = sum(1 for s in students if s.placed)
            pct = round(placed / total * 100, 1) if total else 0.0
            label = f"{low} - {high if high <= 10 else '10'}"
            rows.append({"name": label, "total": total, "placed": placed, "pct": pct})
        data = rows

    elif report_type == "applications":
        columns = ["Student", "Roll No", "Job", "Company", "Status", "Applied On"]
        rows = []
        for application in Application.query.order_by(Application.applied_at.desc()).all():
            rows.append({
                "name": application.student.name,
                "roll": application.student.roll_number,
                "job": application.job.title,
                "company": application.job.company.name,
                "status": application.status,
                "date": application.applied_at,
            })
        data = rows

    elif report_type == "interviews":
        columns = ["Student", "Job", "Company", "Date", "Time", "Round", "Mode", "Status"]
        rows = []
        for interview in Interview.query.join(Application).order_by(Interview.interview_date.desc()).all():
            rows.append({
                "name": interview.application.student.name,
                "job": interview.application.job.title,
                "company": interview.application.job.company.name,
                "date": interview.interview_date,
                "time": interview.interview_time,
                "round": interview.round,
                "mode": interview.mode,
                "status": interview.status,
            })
        data = rows

    return render_template("admin/reports.html", report_type=report_type,
                           columns=columns, rows=data or [])


# --------------------------------------------------------------------------- #
# Settings
# --------------------------------------------------------------------------- #
@admin_bp.route("/settings", methods=["GET", "POST"])
@login_required
@role_required("admin")
def settings():
    if request.method == "POST":
        keys = ["site_name", "college_name", "contact_email", "contact_phone",
                "placement_policy"]
        for key in keys:
            value = request.form.get(key, "").strip()
            record = Setting.query.filter_by(key=key).first()
            if record:
                record.value = value
            else:
                db.session.add(Setting(key=key, value=value))
        db.session.commit()
        flash("System settings saved.", "success")
        return redirect(url_for("admin.settings"))

    settings_map = {s.key: s.value for s in Setting.query.all()}
    return render_template("admin/settings.html", settings_map=settings_map)


# --------------------------------------------------------------------------- #
# CSV Export
# --------------------------------------------------------------------------- #
def csv_response(filename, header, rows):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(header)
    for row in rows:
        writer.writerow(row)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@admin_bp.route("/export/students.csv")
@login_required
@role_required("admin")
def export_students():
    rows = [(s.roll_number, s.name, s.department, s.batch, s.year, s.cgpa,
             s.backlogs, s.phone, "Yes" if s.placed else "No",
             s.user.email) for s in Student.query.order_by(Student.name).all()]
    return csv_response("students.csv",
                        ["Roll No", "Name", "Department", "Batch", "Year",
                         "CGPA", "Backlogs", "Phone", "Placed", "Email"], rows)


@admin_bp.route("/export/companies.csv")
@login_required
@role_required("admin")
def export_companies():
    rows = [(c.name, c.industry, c.location, c.email, c.phone,
             "Yes" if c.is_approved else "No") for c in Company.query.all()]
    return csv_response("companies.csv",
                        ["Company", "Industry", "Location", "Email", "Phone", "Approved"], rows)


@admin_bp.route("/export/jobs.csv")
@login_required
@role_required("admin")
def export_jobs():
    rows = [(j.company.name, j.title, j.package, j.location, j.min_cgpa,
             j.max_backlogs, j.deadline, "Yes" if j.is_active else "No")
            for j in Job.query.all()]
    return csv_response("jobs.csv",
                        ["Company", "Title", "Package (LPA)", "Location", "Min CGPA",
                         "Max Backlogs", "Deadline", "Active"], rows)


@admin_bp.route("/export/applications.csv")
@login_required
@role_required("admin")
def export_applications():
    rows = [(a.student.roll_number, a.student.name, a.job.title, a.job.company.name,
             a.status, a.applied_at.strftime("%Y-%m-%d %H:%M"))
            for a in Application.query.all()]
    return csv_response("applications.csv",
                        ["Roll No", "Student", "Job", "Company", "Status", "Applied At"], rows)
