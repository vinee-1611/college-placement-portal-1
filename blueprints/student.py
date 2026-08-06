"""
blueprints/student.py

Student features: dashboard, profile, resume management, jobs,
applications, interviews, offers, notifications, change password.
"""

from flask import (Blueprint, abort, flash, redirect, render_template,
                   request, url_for)
from flask_login import current_user, login_required

from extensions import db
from models import Application, Interview, Job, Offer, Student
from utils.decorators import role_required
from utils.files import delete_upload, download_upload, save_resume
from utils.queries import already_applied, eligible_jobs_query, is_eligible, student_stats
from utils.validators import (clean_skills, has_pdf_extension, is_valid_cgpa,
                              is_valid_phone)

student_bp = Blueprint("student", __name__)


def current_student():
    """The Student profile belonging to the logged-in user."""
    return current_user.student


@student_bp.route("/dashboard")
@login_required
@role_required("student")
def dashboard():
    student = current_student()
    stats = student_stats(student)
    eligible = eligible_jobs_query(student)[:5]
    upcoming_interviews = (Interview.query
                           .join(Application)
                           .filter(Application.student_id == student.id,
                                   Interview.status == "Scheduled")
                           .order_by(Interview.interview_date.asc())
                           .all())
    notifications = current_user.recent_notifications(5)
    return render_template(
        "dashboard/student_dashboard.html",
        student=student,
        stats=stats,
        eligible=eligible,
        upcoming_interviews=upcoming_interviews,
        notifications=notifications,
    )


@student_bp.route("/profile")
@login_required
@role_required("student")
def profile():
    return render_template("student/profile.html", student=current_student())


@student_bp.route("/profile/update", methods=["POST"])
@login_required
@role_required("student")
def update_profile():
    student = current_student()
    form = request.form

    errors = []
    if form.get("name", "").strip() and not form.get("name").strip():
        errors.append("Name cannot be empty.")
    if form.get("phone", "").strip() and not is_valid_phone(form.get("phone")):
        errors.append("Please enter a valid phone number.")
    try:
        cgpa = float(form.get("cgpa", student.cgpa))
        if not is_valid_cgpa(cgpa):
            errors.append("CGPA must be between 0 and 10.")
    except ValueError:
        errors.append("Invalid CGPA.")
    try:
        backlogs = int(form.get("backlogs", student.backlogs))
        if backlogs < 0:
            errors.append("Backlogs cannot be negative.")
    except ValueError:
        errors.append("Invalid backlogs value.")

    if errors:
        for error in errors:
            flash(error, "danger")
    else:
        student.name = form.get("name", student.name).strip()
        student.phone = form.get("phone", "").strip() or None
        student.year = int(form.get("year", student.year))
        student.cgpa = cgpa
        student.backlogs = backlogs
        student.skills = clean_skills(form.get("skills", ""))
        db.session.commit()
        flash("Profile updated successfully.", "success")

    return redirect(url_for("student.profile"))


@student_bp.route("/profile/picture", methods=["POST"])
@login_required
@role_required("student")
def upload_picture():
    from flask import current_app
    from utils.files import save_image
    student = current_student()
    file = request.files.get("picture")

    if not file or not file.filename:
        flash("Please choose an image to upload.", "danger")
        return redirect(url_for("student.profile"))
    if "." not in file.filename or file.filename.rsplit(".", 1)[1].lower() not in current_app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        flash("Only PNG, JPG, JPEG or GIF images are allowed.", "danger")
        return redirect(url_for("student.profile"))

    if student.profile_pic:
        delete_upload(student.profile_pic)
    student.profile_pic = save_image(file)
    db.session.commit()
    flash("Profile picture updated.", "success")
    return redirect(url_for("student.profile"))


@student_bp.route("/jobs")
@login_required
@role_required("student")
def jobs():
    student = current_student()
    search = request.args.get("q", "").strip()
    department = request.args.get("department", "").strip()
    location = request.args.get("location", "").strip()
    min_package = request.args.get("min_package", "").strip()

    eligible = eligible_jobs_query(student)
    if search:
        term = search.lower()
        eligible = [j for j in eligible if (term in j.title.lower()
                    or term in j.company.name.lower()
                    or term in " ".join(j.skills_list()).lower())]
    if department:
        eligible = [j for j in eligible if j.company.industry.lower() == department.lower()]
    if location:
        eligible = [j for j in eligible if location.lower() in (j.location or "").lower()]
    if min_package:
        try:
            threshold = float(min_package)
            eligible = [j for j in eligible if j.package >= threshold]
        except ValueError:
            pass

    applied_ids = {a.job_id for a in student.applications}
    return render_template(
        "student/jobs.html",
        jobs=eligible,
        applied_ids=applied_ids,
        search=search,
        department=department,
        location=location,
        min_package=min_package,
    )


@student_bp.route("/jobs/<int:job_id>")
@login_required
@role_required("student")
def job_detail(job_id):
    job = Job.query.get_or_404(job_id)
    if not job.company.is_approved:
        abort(404)
    student = current_student()
    application = Application.query.filter_by(student_id=student.id,
                                              job_id=job.id).first()
    return render_template(
        "student/job_detail.html",
        job=job,
        eligible=is_eligible(student, job),
        application=application,
    )


@student_bp.route("/jobs/<int:job_id>/apply", methods=["POST"])
@login_required
@role_required("student")
def apply(job_id):
    job = Job.query.get_or_404(job_id)
    student = current_student()

    if not job.is_open or not job.company.is_approved:
        flash("This job is no longer accepting applications.", "warning")
        return redirect(url_for("student.job_detail", job_id=job.id))
    if not is_eligible(student, job):
        flash("You do not meet the eligibility criteria for this job.", "danger")
        return redirect(url_for("student.job_detail", job_id=job.id))
    if already_applied(student, job):
        flash("You have already applied to this job.", "warning")
        return redirect(url_for("student.job_detail", job_id=job.id))
    if not student.resume_path:
        flash("Please upload your resume before applying.", "warning")
        return redirect(url_for("student.profile"))

    application = Application(student_id=student.id, job_id=job.id)
    db.session.add(application)
    db.session.flush()

    from utils.notifications import notify_many
    recruiter_ids = [r.user_id for r in job.company.recruiters]
    if recruiter_ids:
        notify_many(recruiter_ids,
                    f"New application for {job.title}",
                    f"{student.name} ({student.roll_number}) applied.",
                    url_for("recruiter.job_applicants", job_id=job.id))

    db.session.commit()
    flash(f"Application submitted for {job.title}. Good luck!", "success")
    return redirect(url_for("student.applications"))


@student_bp.route("/applications")
@login_required
@role_required("student")
def applications():
    student = current_student()
    items = (Application.query
             .filter_by(student_id=student.id)
             .order_by(Application.applied_at.desc())
             .all())
    return render_template("student/applications.html", applications=items)


@student_bp.route("/applications/<int:application_id>/withdraw", methods=["POST"])
@login_required
@role_required("student")
def withdraw_application(application_id):
    application = Application.query.get_or_404(application_id)
    if application.student_id != current_student().id:
        abort(403)
    if application.status != "applied":
        flash("You can only withdraw applications that are still under review.", "warning")
        return redirect(url_for("student.applications"))
    db.session.delete(application)
    db.session.commit()
    flash("Application withdrawn.", "info")
    return redirect(url_for("student.applications"))


@student_bp.route("/interviews")
@login_required
@role_required("student")
def interviews():
    student = current_student()
    items = (Interview.query
             .join(Application)
             .filter(Application.student_id == student.id)
             .order_by(Interview.interview_date.desc())
             .all())
    return render_template("student/interviews.html", interviews=items)


@student_bp.route("/offers")
@login_required
@role_required("student")
def offers():
    student = current_student()
    items = (Offer.query
             .join(Application)
             .filter(Application.student_id == student.id)
             .order_by(Offer.offer_date.desc())
             .all())
    return render_template("student/offers.html", offers=items)


@student_bp.route("/offers/<int:offer_id>/download")
@login_required
@role_required("student")
def download_offer(offer_id):
    offer = Offer.query.get_or_404(offer_id)
    if offer.application.student_id != current_student().id:
        abort(403)
    if not offer.offer_letter:
        abort(404)
    return download_upload(offer.offer_letter)


@student_bp.route("/resume/upload", methods=["POST"])
@login_required
@role_required("student")
def upload_resume():
    student = current_student()
    file = request.files.get("resume")

    if not file or not file.filename:
        flash("Please choose a PDF file to upload.", "danger")
        return redirect(url_for("student.profile"))
    if not has_pdf_extension(file.filename):
        flash("Only PDF files are allowed.", "danger")
        return redirect(url_for("student.profile"))
    max_size = request.max_content_length or 3 * 1024 * 1024
    file.stream.seek(0, 2)
    size = file.stream.tell()
    file.stream.seek(0)
    if size > max_size or size > 3 * 1024 * 1024:
        flash("Resume must be smaller than 3 MB.", "danger")
        return redirect(url_for("student.profile"))

    if student.resume_path:
        delete_upload(student.resume_path)
    student.resume_path = save_resume(file)
    db.session.commit()
    flash("Resume uploaded successfully.", "success")
    return redirect(url_for("student.profile"))


@student_bp.route("/resume/download")
@login_required
@role_required("student")
def download_resume():
    student = current_student()
    if not student.resume_path:
        flash("No resume uploaded yet.", "warning")
        return redirect(url_for("student.profile"))
    return download_upload(student.resume_path)


@student_bp.route("/resume/delete", methods=["POST"])
@login_required
@role_required("student")
def delete_resume():
    student = current_student()
    if student.resume_path:
        delete_upload(student.resume_path)
        student.resume_path = None
        db.session.commit()
        flash("Resume removed.", "info")
    return redirect(url_for("student.profile"))
