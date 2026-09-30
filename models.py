"""
models.py

SQLAlchemy models for the College Placement Portal (11 tables + settings).

Tables: users, students, recruiters, admins, companies, jobs,
        applications, interviews, offers, announcements, notifications, settings.

See docs/DATABASE_DESIGN.md for the full schema and ER diagram.
"""

from datetime import date, datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db


class User(UserMixin, db.Model):
    """Single sign-on account; role decides which profile applies."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # student | recruiter | admin
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    reset_token = db.Column(db.String(64), nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    student = db.relationship("Student", backref="user", uselist=False,
                              cascade="all, delete-orphan")
    recruiter = db.relationship("Recruiter", backref="user", uselist=False,
                                cascade="all, delete-orphan")
    admin = db.relationship("Admin", backref="user", uselist=False,
                            cascade="all, delete-orphan")
    notifications = db.relationship("Notification", backref="user",
                                    lazy="dynamic", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def unread_notifications(self):
        return self.notifications.filter_by(is_read=False).count()

    def recent_notifications(self, limit=5):
        return (self.notifications
                .order_by(Notification.created_at.desc())
                .limit(limit).all())

    def all_notifications(self):
        return (self.notifications
                .order_by(Notification.created_at.desc())
                .all())

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"


class Student(db.Model):
    """Academic profile for a student account."""

    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"),
                        nullable=False, unique=True)
    name = db.Column(db.String(120), nullable=False)
    roll_number = db.Column(db.String(20), nullable=False, unique=True, index=True)
    department = db.Column(db.String(100), nullable=False)
    batch = db.Column(db.String(10), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    cgpa = db.Column(db.Float, nullable=False, default=0.0)
    backlogs = db.Column(db.Integer, nullable=False, default=0)
    phone = db.Column(db.String(15), nullable=True)
    skills = db.Column(db.Text, nullable=True)
    profile_pic = db.Column(db.String(256), nullable=True)
    resume_path = db.Column(db.String(256), nullable=True)
    placed = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    applications = db.relationship("Application", backref="student",
                                   lazy=True, cascade="all, delete-orphan")

    def skills_list(self):
        return [s.strip() for s in (self.skills or "").split(",") if s.strip()]

    def __repr__(self):
        return f"<Student {self.name}>"


class Admin(db.Model):
    """Placement officer (admin) profile."""

    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"),
                        nullable=False, unique=True)
    name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(15), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    announcements = db.relationship("Announcement", backref="admin",
                                    lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Admin {self.name}>"


class Company(db.Model):
    """Company that recruiters belong to. Approved by the admin."""

    __tablename__ = "companies"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    industry = db.Column(db.String(100), nullable=True)
    website = db.Column(db.String(120), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(15), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    logo = db.Column(db.String(256), nullable=True)
    is_approved = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    recruiters = db.relationship("Recruiter", backref="company",
                                 lazy=True, cascade="all, delete-orphan")
    jobs = db.relationship("Job", backref="company",
                           lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Company {self.name}>"


class Recruiter(db.Model):
    """Recruiter profile linked to a company."""

    __tablename__ = "recruiters"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"),
                        nullable=False, unique=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    designation = db.Column(db.String(100), nullable=False)
    experience = db.Column(db.String(20), nullable=True)
    phone = db.Column(db.String(15), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def __repr__(self):
        return f"<Recruiter {self.name}>"


class Job(db.Model):
    """A job posting with eligibility criteria."""

    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    skills = db.Column(db.Text, nullable=True)
    min_cgpa = db.Column(db.Float, nullable=False, default=0.0)
    max_backlogs = db.Column(db.Integer, nullable=False, default=10)
    vacancies = db.Column(db.Integer, nullable=False, default=1)
    package = db.Column(db.Float, nullable=False, default=0.0)
    location = db.Column(db.String(100), nullable=True)
    employment_type = db.Column(db.String(20), nullable=False, default="Full-time")
    deadline = db.Column(db.Date, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    applications = db.relationship("Application", backref="job",
                                   lazy=True, cascade="all, delete-orphan")

    @property
    def is_open(self):
        return self.is_active and self.deadline >= date.today()

    def skills_list(self):
        return [s.strip() for s in (self.skills or "").split(",") if s.strip()]

    def __repr__(self):
        return f"<Job {self.title}>"


class Application(db.Model):
    """A student's application to a job, with status tracking."""

    __tablename__ = "applications"
    __table_args__ = (
        db.UniqueConstraint("student_id", "job_id", name="uq_application_student_job"),
    )

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="applied")
    applied_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    interviews = db.relationship("Interview", backref="application",
                                 lazy=True, cascade="all, delete-orphan")
    offer = db.relationship("Offer", backref="application", uselist=False,
                            lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Application student={self.student_id} job={self.job_id} {self.status}>"


class Interview(db.Model):
    """An interview round scheduled for an application."""

    __tablename__ = "interviews"

    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey("applications.id"),
                               nullable=False)
    interview_date = db.Column(db.Date, nullable=False)
    interview_time = db.Column(db.String(10), nullable=True)
    venue = db.Column(db.String(150), nullable=True)
    round = db.Column(db.String(50), nullable=False, default="Technical")
    mode = db.Column(db.String(20), nullable=False, default="Online")
    remarks = db.Column(db.String(256), nullable=True)
    status = db.Column(db.String(20), nullable=False, default="Scheduled")

    def __repr__(self):
        return f"<Interview app={self.application_id} {self.interview_date}>"


class Offer(db.Model):
    """Offer letter uploaded for a selected application."""

    __tablename__ = "offers"

    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey("applications.id"),
                               nullable=False)
    offer_letter = db.Column(db.String(256), nullable=True)
    package = db.Column(db.Float, nullable=True)
    offer_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), nullable=False, default="Pending")

    def __repr__(self):
        return f"<Offer app={self.application_id} {self.status}>"


class Announcement(db.Model):
    """Campus announcement published by the admin."""

    __tablename__ = "announcements"

    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey("admins.id"), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(30), nullable=False, default="news")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def __repr__(self):
        return f"<Announcement {self.title}>"


class Notification(db.Model):
    """In-app notification delivered to a user."""

    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.String(300), nullable=True)
    link = db.Column(db.String(256), nullable=True)
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def __repr__(self):
        return f"<Notification {self.title}>"


class Setting(db.Model):
    """Key-value store for system settings editable by the admin."""

    __tablename__ = "settings"

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), nullable=False, unique=True)
    value = db.Column(db.String(300), nullable=True)

    def __repr__(self):
        return f"<Setting {self.key}>"
