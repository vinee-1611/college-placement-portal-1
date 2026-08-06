"""
app.py

Application factory and entry point.

Run with:  python app.py
Then open: http://127.0.0.1:5000
"""

import os

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
        _seed_defaults()

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


app = create_app()


if __name__ == "__main__":
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
