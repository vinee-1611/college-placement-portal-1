"""
app.py

Application factory and entry point.

Run with:  python app.py
Then open: http://127.0.0.1:5000
"""

import os
from datetime import date, timedelta

import sqlalchemy as sa
from flask import Flask, render_template

from config import Config
from extensions import db, login_manager


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from datetime import datetime as _datetime

    from models import Setting as _Setting

    @app.context_processor
    def inject_globals():
        """Global template helpers available to every blueprint's templates."""

        def setting(key, default=""):
            record = _Setting.query.filter_by(key=key).first()
            return record.value if record and record.value else default

        return dict(now=_datetime.now, setting=setting)


    _register_blueprints(app)
    _register_error_handlers(app)
    _ensure_upload_folders()

    with app.app_context():
        db.create_all()
        _ensure_schema()
        _seed_defaults()
        _seed_demo_jobs()
        _sync_demo_data()

    return app


def _register_blueprints(app):
    from blueprints.admin import admin_bp
    from blueprints.auth import auth_bp
    from blueprints.main import main_bp
    from blueprints.recruiter import recruiter_bp
    from blueprints.student import student_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(student_bp, url_prefix="/student")
    app.register_blueprint(recruiter_bp, url_prefix="/recruiter")
    app.register_blueprint(admin_bp, url_prefix="/admin")


def _register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(403)
    def forbidden(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template("errors/500.html"), 500


def _ensure_upload_folders():
    for folder in (Config.RESUME_FOLDER, Config.OFFER_FOLDER, Config.IMAGE_FOLDER):
        os.makedirs(folder, exist_ok=True)


def _seed_defaults():
    """Create the default admin account and default system settings on first run."""
    from models import Admin, Setting, User

    if not User.query.filter_by(role="admin").first():
        user = User(email=Config.DEFAULT_ADMIN_EMAIL, role="admin")
        user.set_password(Config.DEFAULT_ADMIN_PASSWORD)
        db.session.add(user)
        db.session.flush()
        db.session.add(Admin(user_id=user.id, name="Placement Officer"))
        print(f"[SEED] Default admin created -> {Config.DEFAULT_ADMIN_EMAIL} / {Config.DEFAULT_ADMIN_PASSWORD}")

    defaults = {
        "site_name": "College Placement Portal",
        "college_name": "ABC College of Engineering",
        "contact_email": "placement@college.edu",
        "contact_phone": "+91 00000 00000",
        "placement_policy": ("Students must meet the job eligibility criteria "
                             "(CGPA and backlogs) and have no active backlogs at the "
                             "time of the interview to apply."),
    }
    for key, value in defaults.items():
        if not Setting.query.filter_by(key=key).first():
            db.session.add(Setting(key=key, value=value))

    db.session.commit()


def _ensure_schema():
    """Apply column additions to databases created by an earlier version.

    db.create_all() only creates missing tables, it never adds new columns to
    existing ones, so every column added to a shipped model is listed here.
    """
    added_columns = {
        "recruiters": {
            "experience": "VARCHAR(20)",
        },
    }

    inspector = sa.inspect(db.engine)
    for table, columns in added_columns.items():
        existing = {c["name"] for c in inspector.get_columns(table)}
        for column, ddl_type in columns.items():
            if column not in existing:
                with db.engine.begin() as conn:
                    conn.execute(sa.text(f"ALTER TABLE {table} ADD COLUMN {column} {ddl_type}"))
                print(f"[SEED] Added column {table}.{column}")


def _seed_demo_jobs():
    """Populate Browse Jobs with demo companies and open positions.

    Runs only while the jobs table is empty, so real postings are never
    overwritten and the seed never runs twice.
    """
    from models import Company, Job, Recruiter, User
    from utils.demo_data import DEMO_COMPANIES

    if Job.query.first():
        return

    for spec in DEMO_COMPANIES:
        company = Company(
            name=spec["name"],
            industry=spec["industry"],
            website=spec.get("website"),
            email=spec.get("email"),
            location=spec["location"],
            description=spec["description"],
            is_approved=True,
        )
        db.session.add(company)
        db.session.flush()

        user = User(email=spec["recruiter"]["email"], role="recruiter")
        user.set_password(Config.DEFAULT_RECRUITER_PASSWORD)
        db.session.add(user)
        db.session.flush()

        db.session.add(Recruiter(
            user_id=user.id,
            company_id=company.id,
            name=spec["recruiter"]["name"],
            designation=spec["recruiter"]["designation"],
            experience=spec["recruiter"]["experience"],
        ))

        for job in spec["jobs"]:
            db.session.add(Job(
                company_id=company.id,
                title=job["title"],
                description=job["description"],
                skills=job.get("skills"),
                min_cgpa=job.get("min_cgpa", 6.0),
                max_backlogs=job.get("max_backlogs", 2),
                vacancies=job.get("vacancies", 5),
                package=job.get("package", 0.0),
                location=company.location,
                employment_type=job.get("employment_type", "Full-time"),
                deadline=date.today() + timedelta(days=job.get("days_to_deadline", 30)),
                is_active=True,
            ))

    db.session.commit()
    print(f"[SEED] Demo companies/jobs created -> {len(DEMO_COMPANIES)} companies, "
          f"demo recruiter login: {DEMO_COMPANIES[0]['recruiter']['email']} / "
          f"{Config.DEFAULT_RECRUITER_PASSWORD}")


def _sync_demo_data():
    """Re-apply utils/demo_data.py to an already-seeded database.

    Editing the demo data has no effect on an existing database because
    _seed_demo_jobs() only runs while the jobs table is empty. This brings
    previously-seeded demo jobs back in step with the source data — including
    pushing their deadlines forward so the demo never goes stale. Jobs with
    applications are left alone, and is_active is never touched so any job the
    admin or recruiter deactivated stays that way.
    """
    from models import Company, Job
    from utils.demo_data import DEMO_COMPANIES

    synced = 0
    for spec in DEMO_COMPANIES:
        company = Company.query.filter(
            db.func.lower(Company.name) == spec["name"].lower()).first()
        if not company:
            continue
        for job_spec in spec["jobs"]:
            job = Job.query.filter_by(company_id=company.id,
                                      title=job_spec["title"]).first()
            if not job or job.applications:
                continue
            values = {
                "description": job_spec["description"],
                "skills": job_spec.get("skills"),
                "min_cgpa": job_spec.get("min_cgpa", 6.0),
                "max_backlogs": job_spec.get("max_backlogs", 2),
                "vacancies": job_spec.get("vacancies", 5),
                "package": job_spec.get("package", 0.0),
                "location": company.location,
                "employment_type": job_spec.get("employment_type", "Full-time"),
                "deadline": date.today() + timedelta(days=job_spec.get("days_to_deadline", 30)),
            }
            if all(getattr(job, key) == value for key, value in values.items()):
                continue
            for key, value in values.items():
                setattr(job, key, value)
            synced += 1

    if synced:
        db.session.commit()
        print(f"[SEED] Synced {synced} demo job(s) with utils/demo_data.py")


app = create_app()


if __name__ == "__main__":
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
