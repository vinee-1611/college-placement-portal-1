"""
blueprints/recruiter.py

Recruiter features: dashboard, company & recruiter profile, job management,
applicant review, shortlist/reject, interview scheduling, results, offer upload.
"""

from datetime import date, datetime

from flask import (Blueprint, abort, flash, redirect, render_template,
                   request, url_for)
from flask_login import current_user, login_required

from extensions import db
from models import Application, Interview, Job, Offer, Recruiter, Student
from utils.decorators import role_required
from utils.files import delete_upload, download_upload, save_offer
from utils.queries import company_stats
from utils.validators import has_pdf_extension, is_valid_cgpa, is_valid_phone

recruiter_bp = Blueprint("recruiter", __name__)

EMPLOYMENT_TYPES = ["Full-time", "Internship", "Contract", "Part-time"]


def current_recruiter():
    return current_user.recruiter


def recruiter_company():
    return current_recruiter().company


def can_manage_job(job):
    return job.company_id == recruiter_company().id


@recruiter_bp.route("/dashboard")
@login_required
@role_required("recruiter")
def dashboard():
    company = recruiter_company()
    stats = company_stats(company)
    recent_jobs = (Job.query
                   .filter_by(company_id=company.id)
                   .order_by(Job.created_at.desc())
                   .limit(5).all())
    job_ids = [j.id for j in company.jobs]
    recent_applications = (Application.query
                           .filter(Application.job_id.in_(job_ids))
                           .order_by(Application.applied_at.desc())
                           .limit(8).all()) if job_ids else []
    notifications = current_user.recent_notifications(5)
    return render_template(
        "dashboard/recruiter_dashboard.html",
        company=company,
        stats=stats,
        recent_jobs=recent_jobs,
        recent_applications=recent_applications,
        notifications=notifications,
    )


@recruiter_bp.route("/profile")
@login_required
@role_required("recruiter")
def profile():
    return render_template("recruiter/profile.html",
                           recruiter=current_recruiter(),
                           company=recruiter_company())


@recruiter_bp.route("/profile/update", methods=["POST"])
@login_required
@role_required("recruiter")
def update_profile():
    recruiter = current_recruiter()
    form = request.form
    errors = []
    if not form.get("name", "").strip():
        errors.append("Name is required.")
    if not form.get("designation", "").strip():
        errors.append("Designation is required.")
    if form.get("phone", "").strip() and not is_valid_phone(form.get("phone")):
        errors.append("Please enter a valid phone number.")

    if errors:
        for error in errors:
            flash(error, "danger")
    else:
        recruiter.name = form.get("name").strip()
        recruiter.designation = form.get("designation").strip()
        recruiter.phone = form.get("phone", "").strip() or None
        db.session.commit()
        flash("Profile updated successfully.", "success")
    return redirect(url_for("recruiter.profile"))


@recruiter_bp.route("/company/update", methods=["POST"])
@login_required
@role_required("recruiter")
def update_company():
    company = recruiter_company()
    form = request.form
    if not form.get("name", "").strip():
        flash("Company name is required.", "danger")
        return redirect(url_for("recruiter.profile"))

    company.name = form.get("name").strip()
    company.industry = form.get("industry", "").strip() or None
    company.website = form.get("website", "").strip() or None
    company.email = form.get("email", "").strip() or None
    company.phone = form.get("phone", "").strip() or None
    company.location = form.get("location", "").strip() or None
    company.description = form.get("description", "").strip() or None
    db.session.commit()
    flash("Company profile updated successfully.", "success")
    return redirect(url_for("recruiter.profile"))


@recruiter_bp.route("/jobs")
@login_required
@role_required("recruiter")
def jobs():
    company = recruiter_company()
    status = request.args.get("status", "").strip()
    query = Job.query.filter_by(company_id=company.id)
    if status in ("active", "inactive"):
        query = query.filter_by(is_active=(status == "active"))
    items = query.order_by(Job.created_at.desc()).all()
    return render_template("recruiter/jobs.html", jobs=items, status=status)


@recruiter_bp.route("/jobs/new", methods=["GET", "POST"])
@login_required
@role_required("recruiter")
def job_new():
    company = recruiter_company()
    if not company.is_approved:
        flash("Your company must be approved before you can post jobs.", "warning")
        return redirect(url_for("recruiter.profile"))

    if request.method == "POST":
        errors, data = validate_job_form(request.form)
        if errors:
            for error in errors:
                flash(error, "danger")
        else:
            job = Job(company_id=company.id, **data)
            db.session.add(job)
            db.session.commit()
            flash(f"Job '{job.title}' posted successfully.", "success")
            return redirect(url_for("recruiter.jobs"))

    return render_template("recruiter/job_form.html",
                           job=None, employment_types=EMPLOYMENT_TYPES,
                           today=date.today())


@recruiter_bp.route("/jobs/<int:job_id>")
@login_required
@role_required("recruiter")
def job_detail(job_id):
    job = Job.query.get_or_404(job_id)
    if not can_manage_job(job):
        abort(403)
    return render_template("recruiter/job_detail.html", job=job)


@recruiter_bp.route("/jobs/<int:job_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("recruiter")
def job_edit(job_id):
    job = Job.query.get_or_404(job_id)
    if not can_manage_job(job):
        abort(403)

    if request.method == "POST":
        errors, data = validate_job_form(request.form)
        if errors:
            for error in errors:
                flash(error, "danger")
        else:
            for key, value in data.items():
                setattr(job, key, value)
            db.session.commit()
            flash("Job updated successfully.", "success")
            return redirect(url_for("recruiter.job_detail", job_id=job.id))

    return render_template("recruiter/job_form.html",
                           job=job, employment_types=EMPLOYMENT_TYPES,
                           today=date.today())


@recruiter_bp.route("/jobs/<int:job_id>/delete", methods=["POST"])
@login_required
@role_required("recruiter")
def job_delete(job_id):
    job = Job.query.get_or_404(job_id)
    if not can_manage_job(job):
        abort(403)
    db.session.delete(job)
    db.session.commit()
    flash(f"Job '{job.title}' deleted.", "info")
    return redirect(url_for("recruiter.jobs"))


@recruiter_bp.route("/jobs/<int:job_id>/toggle", methods=["POST"])
@login_required
@role_required("recruiter")
def job_toggle(job_id):
    job = Job.query.get_or_404(job_id)
    if not can_manage_job(job):
        abort(403)
    job.is_active = not job.is_active
    db.session.commit()
    state = "activated" if job.is_active else "deactivated"
    flash(f"Job '{job.title}' {state}.", "success")
    return redirect(url_for("recruiter.jobs"))


@recruiter_bp.route("/applicants")
@login_required
@role_required("recruiter")
def applicants():
    company = recruiter_company()
    job_ids = [j.id for j in company.jobs]
    if not job_ids:
        return render_template("recruiter/applicants.html", applications=[], jobs=company.jobs)

    query = Application.query.filter(Application.job_id.in_(job_ids))
    search = request.args.get("q", "").strip()
    job_filter = request.args.get("job", "").strip()
    status_filter = request.args.get("status", "").strip()

    if job_filter:
        try:
            query = query.filter_by(job_id=int(job_filter))
        except ValueError:
            pass
    if status_filter:
        query = query.filter_by(status=status_filter)
    if search:
        term = f"%{search.lower()}%"
        query = (query.join(Application.student)
                      .filter(db.or_(Student.name.ilike(term),
                                     Student.roll_number.ilike(term),
                                     Student.department.ilike(term))))

    applications = query.order_by(Application.applied_at.desc()).all()
    return render_template("recruiter/applicants.html",
                           applications=applications,
                           jobs=company.jobs,
                           search=search,
                           job_filter=job_filter,
                           status_filter=status_filter)


@recruiter_bp.route("/jobs/<int:job_id>/applicants")
@login_required
@role_required("recruiter")
def job_applicants(job_id):
    job = Job.query.get_or_404(job_id)
    if not can_manage_job(job):
        abort(403)
    applications = (Application.query
                    .filter_by(job_id=job.id)
                    .order_by(Application.applied_at.desc())
                    .all())
    return render_template("recruiter/job_detail.html",
                           job=job, applications=applications)


@recruiter_bp.route("/applicants/<int:application_id>")
@login_required
@role_required("recruiter")
def applicant_detail(application_id):
    application = Application.query.get_or_404(application_id)
    if not can_manage_job(application.job):
        abort(403)
    return render_template("recruiter/applicant_detail.html",
                           application=application, today=date.today())


@recruiter_bp.route("/students/<int:student_id>/resume/download")
@login_required
@role_required("recruiter")
def download_applicant_resume(student_id):
    from models import Student
    from utils.files import download_upload
    student = Student.query.get_or_404(student_id)
    if not student.resume_path:
        abort(404)
    return download_upload(student.resume_path)


@recruiter_bp.route("/applicants/<int:application_id>/status", methods=["POST"])
@login_required
@role_required("recruiter")
def applicant_status(application_id):
    application = Application.query.get_or_404(application_id)
    if not can_manage_job(application.job):
        abort(403)

    action = request.form.get("action", "")
    if action == "shortlist":
        application.status = "shortlisted"
        message = f"{application.student.name} shortlisted for {application.job.title}."
        flash("Applicant shortlisted.", "success")
    elif action == "reject":
        application.status = "rejected"
        message = f"Application for {application.job.title} has been rejected."
        flash("Applicant rejected.", "info")
    else:
        flash("Invalid action.", "danger")
        return redirect(request.referrer or url_for("recruiter.applicants"))

    from utils.notifications import notify
    notify(application.student.user_id, "Application status updated", message,
           url_for("student.applications"))
    db.session.commit()
    return redirect(request.referrer or url_for("recruiter.applicants"))


@recruiter_bp.route("/applicants/<int:application_id>/interview", methods=["POST"])
@login_required
@role_required("recruiter")
def schedule_interview(application_id):
    application = Application.query.get_or_404(application_id)
    if not can_manage_job(application.job):
        abort(403)

    form = request.form
    try:
        interview_date = datetime.strptime(form.get("interview_date", ""), "%Y-%m-%d").date()
    except ValueError:
        flash("Please choose a valid interview date.", "danger")
        return redirect(request.referrer or url_for("recruiter.applicants"))

    if interview_date < date.today():
        flash("Interview date cannot be in the past.", "danger")
        return redirect(request.referrer or url_for("recruiter.applicants"))

    interview = Interview(
        application_id=application.id,
        interview_date=interview_date,
        interview_time=form.get("interview_time", "").strip() or None,
        venue=form.get("venue", "").strip() or None,
        round=form.get("round", "Technical").strip() or "Technical",
        mode=form.get("mode", "Online").strip() or "Online",
        remarks=form.get("remarks", "").strip() or None,
        status="Scheduled",
    )
    application.status = "interview"
    db.session.add(interview)

    from utils.notifications import notify
    notify(application.student.user_id,
           f"Interview scheduled for {application.job.title}",
           f"Round: {interview.round} on {interview_date}.",
           url_for("student.interviews"))
    db.session.commit()
    flash(f"Interview scheduled for {application.student.name}.", "success")
    return redirect(request.referrer or url_for("recruiter.applicants"))


@recruiter_bp.route("/applicants/<int:application_id>/select", methods=["POST"])
@login_required
@role_required("recruiter")
def select_applicant(application_id):
    application = Application.query.get_or_404(application_id)
    if not can_manage_job(application.job):
        abort(403)

    application.status = "selected"
    application.student.placed = True

    from utils.notifications import notify
    notify(application.student.user_id,
           f"Congratulations! Selected for {application.job.title}",
           "You have been selected. The offer letter will be uploaded shortly.",
           url_for("student.offers"))
    db.session.commit()
    flash(f"{application.student.name} marked as selected.", "success")
    return redirect(request.referrer or url_for("recruiter.applicants"))


@recruiter_bp.route("/applicants/<int:application_id>/offer", methods=["POST"])
@login_required
@role_required("recruiter")
def upload_offer(application_id):
    application = Application.query.get_or_404(application_id)
    if not can_manage_job(application.job):
        abort(403)

    file = request.files.get("offer_letter")
    if not file or not file.filename:
        flash("Please choose an offer-letter PDF to upload.", "danger")
        return redirect(request.referrer or url_for("recruiter.applicants"))
    if not has_pdf_extension(file.filename):
        flash("Only PDF files are allowed for offer letters.", "danger")
        return redirect(request.referrer or url_for("recruiter.applicants"))

    try:
        package = float(request.form.get("package", 0) or 0)
        if package < 0:
            raise ValueError
    except ValueError:
        flash("Please enter a valid package.", "danger")
        return redirect(request.referrer or url_for("recruiter.applicants"))

    if application.offer:
        offer = application.offer
        if offer.offer_letter:
            delete_upload(offer.offer_letter)
    else:
        offer = Offer(application_id=application.id)
        db.session.add(offer)

    offer.offer_letter = save_offer(file)
    offer.package = package or None
    offer.offer_date = date.today()
    offer.status = "Pending"
    application.status = "offer"

    from utils.notifications import notify
    notify(application.student.user_id,
           f"Offer letter uploaded for {application.job.title}",
           "Your offer letter is available for download.",
           url_for("student.offers"))
    db.session.commit()
    flash("Offer letter uploaded.", "success")
    return redirect(request.referrer or url_for("recruiter.applicants"))


@recruiter_bp.route("/offers")
@login_required
@role_required("recruiter")
def offers():
    company = recruiter_company()
    job_ids = [j.id for j in company.jobs]
    items = []
    if job_ids:
        items = (Offer.query
                 .join(Application, Offer.application_id == Application.id)
                 .filter(Application.job_id.in_(job_ids))
                 .order_by(Offer.offer_date.desc())
                 .all())
    return render_template("recruiter/offers.html", offers=items)


@recruiter_bp.route("/interviews")
@login_required
@role_required("recruiter")
def interviews():
    company = recruiter_company()
    job_ids = [j.id for j in company.jobs]
    items = []
    if job_ids:
        items = (Interview.query
                 .join(Application, Interview.application_id == Application.id)
                 .filter(Application.job_id.in_(job_ids))
                 .order_by(Interview.interview_date.desc())
                 .all())
    return render_template("recruiter/interviews.html", interviews=items)


@recruiter_bp.route("/offers/<int:offer_id>/download")
@login_required
@role_required("recruiter")
def download_offer(offer_id):
    offer = Offer.query.get_or_404(offer_id)
    if not can_manage_job(offer.application.job):
        abort(403)
    if not offer.offer_letter:
        abort(404)
    return download_upload(offer.offer_letter)


def validate_job_form(form):
    """Validate a job form; return (errors, data_dict)."""
    from utils.validators import clean_skills
    errors = []
    title = form.get("title", "").strip()
    description = form.get("description", "").strip()
    if not title:
        errors.append("Job title is required.")
    if not description:
        errors.append("Job description is required.")

    try:
        min_cgpa = float(form.get("min_cgpa", 0))
        if not is_valid_cgpa(min_cgpa):
            errors.append("Minimum CGPA must be between 0 and 10.")
    except ValueError:
        errors.append("Invalid minimum CGPA.")

    try:
        max_backlogs = int(form.get("max_backlogs", 10))
        if max_backlogs < 0:
            errors.append("Maximum backlogs cannot be negative.")
    except ValueError:
        errors.append("Invalid backlogs value.")

    try:
        vacancies = int(form.get("vacancies", 1))
        if vacancies < 1:
            errors.append("Vacancies must be at least 1.")
    except ValueError:
        errors.append("Invalid vacancies value.")

    try:
        package = float(form.get("package", 0))
        if package < 0:
            errors.append("Package cannot be negative.")
    except ValueError:
        errors.append("Invalid package value.")

    deadline = None
    try:
        deadline = datetime.strptime(form.get("deadline", ""), "%Y-%m-%d").date()
        if deadline < date.today():
            errors.append("Deadline cannot be in the past.")
    except ValueError:
        errors.append("Please choose a valid deadline date.")

    employment_type = form.get("employment_type", "Full-time").strip()

    if errors:
        return errors, {}

    data = {
        "title": title,
        "description": description,
        "skills": clean_skills(form.get("skills", "")),
        "min_cgpa": min_cgpa,
        "max_backlogs": max_backlogs,
        "vacancies": vacancies,
        "package": package,
        "location": form.get("location", "").strip() or None,
        "employment_type": employment_type,
        "deadline": deadline,
    }
    return [], data
