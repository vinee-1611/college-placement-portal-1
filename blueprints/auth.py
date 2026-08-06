"""
blueprints/auth.py

Authentication: login, student/recruiter registration, logout,
forgot & reset password, change password.
"""

import secrets
from datetime import datetime, timedelta

from flask import (Blueprint, flash, redirect, render_template, request,
                   url_for)
from flask_login import current_user, login_required, login_user, logout_user

from extensions import db
from models import Admin, Company, Recruiter, Student, User
from utils.validators import (clean_skills, is_strong_password, is_valid_cgpa,
                              is_valid_email, is_valid_phone, is_valid_roll_number)

auth_bp = Blueprint("auth", __name__)

DEPARTMENTS = [
    "Computer Science Engineering",
    "Information Technology",
    "Electronics & Communication Engineering",
    "Electrical & Electronics Engineering",
    "Mechanical Engineering",
    "Civil Engineering",
]


def dashboard_url_for(user):
    """Return the dashboard URL for a user's role."""
    if user.role == "student":
        return url_for("student.dashboard")
    if user.role == "recruiter":
        return url_for("recruiter.dashboard")
    return url_for("admin.dashboard")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(dashboard_url_for(current_user))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email.lower()).first()

        if user and user.check_password(password):
            if not user.is_active:
                flash("Your account has been deactivated. Contact the placement office.", "danger")
                return render_template("auth/login.html")
            login_user(user)
            flash(f"Welcome back, {user.email}!", "success")
            return redirect(request.args.get("next") or dashboard_url_for(user))

        flash("Invalid email or password.", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(dashboard_url_for(current_user))

    if request.method == "POST":
        form = request.form
        email = form.get("email", "").strip().lower()
        password = form.get("password", "")
        confirm = form.get("confirm_password", "")

        errors = []
        if not is_valid_email(email):
            errors.append("Please enter a valid email address.")
        if User.query.filter_by(email=email).first():
            errors.append("This email is already registered.")
        if not is_strong_password(password):
            errors.append("Password must be at least 8 characters and include uppercase, lowercase, a number and a symbol.")
        if password != confirm:
            errors.append("Passwords do not match.")
        if not form.get("name", "").strip():
            errors.append("Full name is required.")
        if not is_valid_roll_number(form.get("roll_number", "")):
            errors.append("Roll number must be 5-20 characters (letters, digits, / or -).")
        if Student.query.filter_by(roll_number=form.get("roll_number", "").strip()).first():
            errors.append("This roll number is already registered.")
        if form.get("department", "").strip() not in DEPARTMENTS:
            errors.append("Please select a valid department.")
        if form.get("batch", "").strip() not in ("2021-2025", "2022-2026", "2023-2027", "2024-2028"):
            errors.append("Please select a valid batch.")
        try:
            year = int(form.get("year", 0))
            if year not in (1, 2, 3, 4):
                errors.append("Year must be between 1 and 4.")
        except ValueError:
            errors.append("Invalid year.")
        try:
            cgpa = float(form.get("cgpa", 0))
            if not is_valid_cgpa(cgpa):
                errors.append("CGPA must be between 0 and 10.")
        except ValueError:
            errors.append("Invalid CGPA.")
        try:
            backlogs = int(form.get("backlogs", 0))
            if backlogs < 0:
                errors.append("Backlogs cannot be negative.")
        except ValueError:
            errors.append("Invalid backlogs value.")
        if form.get("phone", "").strip() and not is_valid_phone(form.get("phone")):
            errors.append("Please enter a valid phone number.")

        if errors:
            for error in errors:
                flash(error, "danger")
        else:
            user = User(email=email, role="student")
            user.set_password(password)
            db.session.add(user)
            db.session.flush()

            student = Student(
                user_id=user.id,
                name=form.get("name").strip(),
                roll_number=form.get("roll_number").strip(),
                department=form.get("department").strip(),
                batch=form.get("batch").strip(),
                year=year,
                cgpa=cgpa,
                backlogs=backlogs,
                phone=form.get("phone", "").strip() or None,
                skills=clean_skills(form.get("skills", "")),
            )
            db.session.add(student)
            db.session.commit()
            flash("Registration successful! Please log in to continue.", "success")
            return redirect(url_for("auth.login"))

    return render_template("auth/register.html", departments=DEPARTMENTS)


@auth_bp.route("/register/recruiter", methods=["GET", "POST"])
def register_recruiter():
    if current_user.is_authenticated:
        return redirect(dashboard_url_for(current_user))

    if request.method == "POST":
        form = request.form
        email = form.get("email", "").strip().lower()
        password = form.get("password", "")

        errors = []
        if not is_valid_email(email):
            errors.append("Please enter a valid email address.")
        if User.query.filter_by(email=email).first():
            errors.append("This email is already registered.")
        if not is_strong_password(password):
            errors.append("Password must be at least 8 characters and include uppercase, lowercase, a number and a symbol.")
        if password != form.get("confirm_password", ""):
            errors.append("Passwords do not match.")
        if not form.get("name", "").strip():
            errors.append("Recruiter name is required.")
        if not form.get("designation", "").strip():
            errors.append("Designation is required.")
        if not form.get("company_name", "").strip():
            errors.append("Company name is required.")
        if Company.query.filter_by(name=form.get("company_name", "").strip()).first():
            errors.append("This company is already registered. Contact the placement office.")
        if form.get("phone", "").strip() and not is_valid_phone(form.get("phone")):
            errors.append("Please enter a valid phone number.")

        if errors:
            for error in errors:
                flash(error, "danger")
        else:
            company = Company(
                name=form.get("company_name").strip(),
                industry=form.get("industry", "").strip() or None,
                website=form.get("website", "").strip() or None,
                email=form.get("company_email", "").strip() or None,
                phone=form.get("company_phone", "").strip() or None,
                location=form.get("location", "").strip() or None,
                description=form.get("description", "").strip() or None,
                is_approved=False,
            )
            db.session.add(company)
            db.session.flush()

            user = User(email=email, role="recruiter")
            user.set_password(password)
            db.session.add(user)
            db.session.flush()

            recruiter = Recruiter(
                user_id=user.id,
                company_id=company.id,
                name=form.get("name").strip(),
                designation=form.get("designation").strip(),
                phone=form.get("phone", "").strip() or None,
            )
            db.session.add(recruiter)
            db.session.commit()
            flash("Company registered! Your account will be activated once the placement office approves your company.", "success")
            return redirect(url_for("auth.login"))

    return render_template("auth/register_recruiter.html")


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    reset_link = None
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        user = User.query.filter_by(email=email).first()
        if user:
            user.reset_token = secrets.token_urlsafe(32)
            user.reset_token_expiry = datetime.now() + timedelta(minutes=30)
            db.session.commit()
            reset_link = url_for("auth.reset_password", token=user.reset_token, _external=True)
        else:
            flash("No account found with that email.", "danger")

    return render_template("auth/forgot_password.html", reset_link=reset_link)


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    user = User.query.filter_by(reset_token=token).first()
    expired = (not user or not user.reset_token_expiry
               or user.reset_token_expiry < datetime.now())
    if expired:
        flash("This password reset link is invalid or has expired.", "danger")
        return redirect(url_for("auth.forgot_password"))

    if request.method == "POST":
        password = request.form.get("password", "")
        if not is_strong_password(password):
            flash("Password must be at least 8 characters and include uppercase, lowercase, a number and a symbol.", "danger")
        elif password != request.form.get("confirm_password", ""):
            flash("Passwords do not match.", "danger")
        else:
            user.set_password(password)
            user.reset_token = None
            user.reset_token_expiry = None
            db.session.commit()
            flash("Password reset successful! Please log in.", "success")
            return redirect(url_for("auth.login"))

    return render_template("auth/reset_password.html")


@auth_bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        current = request.form.get("current_password", "")
        new_password = request.form.get("new_password", "")

        if not current_user.check_password(current):
            flash("Your current password is incorrect.", "danger")
        elif not is_strong_password(new_password):
            flash("New password must be at least 8 characters and include uppercase, lowercase, a number and a symbol.", "danger")
        elif new_password != request.form.get("confirm_password", ""):
            flash("New passwords do not match.", "danger")
        else:
            current_user.set_password(new_password)
            db.session.commit()
            flash("Password changed successfully.", "success")
            return redirect(dashboard_url_for(current_user))

    return render_template("auth/change_password.html")
