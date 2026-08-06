"""
blueprints/main.py

Public pages: landing page, about, announcements, and shared notifications.
"""

from flask import Blueprint, redirect, render_template, request
from flask_login import current_user, login_required

from extensions import db
from models import Announcement, Company, Job, Setting

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    announcements = Announcement.query.order_by(
        Announcement.created_at.desc()).limit(5).all()
    job_count = Job.query.filter_by(is_active=True).count()
    company_count = Company.query.filter_by(is_approved=True).count()
    return render_template(
        "main/index.html",
        announcements=announcements,
        job_count=job_count,
        company_count=company_count,
    )


@main_bp.route("/about")
def about():
    return render_template("main/about.html")


@main_bp.route("/announcements")
def announcements():
    page = 1
    items = (Announcement.query
             .order_by(Announcement.created_at.desc())
             .paginate(page=page, per_page=9, error_out=False))
    return render_template("main/announcements.html", items=items)


@main_bp.route("/notifications")
@login_required
def notifications():
    return render_template("student/notifications.html",
                           notifications=current_user.all_notifications())


@main_bp.route("/notifications/mark-read", methods=["POST"])
@login_required
def mark_notifications_read():
    current_user.notifications.filter_by(is_read=False).update({"is_read": True})
    db.session.commit()
    return redirect(request.referrer or url_for("main.index"))


@main_bp.route("/uploads/<path:filename>")
def uploaded_file(filename):
    """Serve files stored under the uploads/ folder."""
    from flask import current_app, send_from_directory
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)
