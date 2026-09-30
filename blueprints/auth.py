"""
blueprints/auth.py

Authentication: login, student/recruiter registration, logout,
forgot & reset password, change password.
"""

import secrets
from datetime import date, datetime, timedelta

from flask import (Blueprint, flash, redirect, render_template, request,
                   url_for)
from flask_login import current_user, login_required, login_user, logout_user

from config import Config
from extensions import db
from models import Admin, Company, Job, Recruiter, Student, User
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

EXPERIENCE_LEVELS = Config.EXPERIENCE_LEVELS
MAX_ROLES = 6
QUICK_SIGNUP_DEADLINE_DAYS = 30


def parse_roles(raw):
    """Turn a comma-separated list of open roles into a clean, de-duplicated list."""
    roles = []
    for part in (raw or "").split(","):
        role = part.strip()
        if role and role.lower() not in [r.lower() for r in roles]:
            roles.append(role)
    return roles


def split_vacancies(total, count):
    """Spread `total` vacancies over `count` roles as evenly as possible."""
    base, remainder = divmod(total, count)
    return [base + (1 if index < remainder else 0) for index in range(count)]


def default_recruiter_name(email):
    """Fallback display name derived from the email local part."""
    local_part = email.split("@")[0].replace(".", " ").replace("_", " ").strip()
    return local_part.title() or "Recruiter"


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
    """Quick recruiter signup.

    A recruiter only has to state who they are, where their company is, how
    many vacancies they have and which roles are open. The company, the
    recruiter account and one job posting per role are all created here so the
    recruiter lands on a working dashboard instead of an empty form.
    """
    if current_user.is_authenticated:
        return redirect(dashboard_url_for(current_user))

    if request.method == "POST":
        form = request.form
        email = form.get("email", "").strip().lower()
        password = form.get("password", "")
        company_name = form.get("company_name", "").strip()
        location = form.get("location", "").strip()
        designation = form.get("designation", "").strip()
        experience = form.get("experience", "").strip()
        roles = parse_roles(form.get("roles", ""))

        errors = []
        if not company_name:
            errors.append("Company name is required.")
        if not location:
            errors.append("Company location is required.")
        if not designation:
            errors.append("Your designation is required.")
        if experience not in EXPERIENCE_LEVELS:
            errors.append("Please select your experience level.")
        try:
            vacancies = int(form.get("vacancies", 0))
            if vacancies < 1:
                errors.append("Vacancies must be at least 1.")
        except ValueError:
            vacancies = 0
            errors.append("Invalid vacancies value.")
        if not roles:
            errors.append("Enter at least one role you are hiring for.")
        elif len(roles) > MAX_ROLES:
            errors.append(f"You can list up to {MAX_ROLES} roles at a time.")
        if not is_valid_email(email):
            errors.append("Please enter a valid email address.")
        elif User.query.filter_by(email=email).first():
            errors.append("This email is already registered. Please log in instead.")
        if not is_strong_password(password):
            errors.append("Password must be at least 8 characters and include uppercase, lowercase, a number and a symbol.")
        if password != form.get("confirm_password", ""):
            errors.append("Passwords do not match.")

        if errors:
            for error in errors:
                flash(error, "danger")
        else:
            company = Company.query.filter(
                db.func.lower(Company.name) == company_name.lower()).first()
            created_company = company is None
            if created_company:
                company = Company(
                    name=company_name,
                    location=location,
                    description=f"{company_name} is hiring for {len(roles)} role(s) on the placement portal.",
                    is_approved=True,
                )
                db.session.add(company)
                db.session.flush()
            else:
                company.location = company.location or location

            user = User(email=email, role="recruiter")
            user.set_password(password)
            db.session.add(user)
            db.session.flush()

            recruiter_name = form.get("name", "").strip() or default_recruiter_name(email)
            db.session.add(Recruiter(
                user_id=user.id,
                company_id=company.id,
                name=recruiter_name,
                designation=designation,
                experience=experience,
            ))

            for role, role_vacancies in zip(roles, split_vacancies(vacancies, len(roles))):
                db.session.add(Job(
                    company_id=company.id,
                    title=role,
                    description=(
                        f"{role} opening at {company.name}, {location}. "
                        f"Applications are reviewed by the placement office for this "
                        f"academic cycle. Edit this posting to add the full job "
                        f"description, required skills and package."
                    ),
                    min_cgpa=6.0,
                    max_backlogs=2,
                    vacancies=role_vacancies,
                    package=0.0,
                    location=location,
                    employment_type="Full-time",
                    deadline=date.today() + timedelta(days=QUICK_SIGNUP_DEADLINE_DAYS),
                    is_active=True,
                ))

            db.session.commit()
            login_user(user)
            flash(
                f"Welcome aboard! {company.name} is live and "
                f"{'we created ' + str(len(roles)) + ' job posting(s) from your openings' if created_company else 'your openings are now advertised'}.",
                "success",
            )
            return redirect(url_for("recruiter.dashboard"))

    return render_template("auth/register_recruiter.html",
                           experience_levels=EXPERIENCE_LEVELS)



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
