"""
config.py

Central configuration for the College Placement Portal.
"""

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Flask
    SECRET_KEY = os.environ.get("SECRET_KEY", "placement-portal-secret-key-change-in-production")

    # Database (SQLite, auto-created in project root)
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "database.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Upload folders
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    RESUME_FOLDER = os.path.join(UPLOAD_FOLDER, "resumes")
    OFFER_FOLDER = os.path.join(UPLOAD_FOLDER, "offers")
    IMAGE_FOLDER = os.path.join(UPLOAD_FOLDER, "images")

    # Upload limits
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB
    MAX_RESUME_SIZE = 3 * 1024 * 1024     # 3 MB
    MAX_IMAGE_SIZE = 1 * 1024 * 1024      # 1 MB
    ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

    # Server
    HOST = "127.0.0.1"
    PORT = 5000
    DEBUG = True

    # Default admin account created on first run
    DEFAULT_ADMIN_EMAIL = "admin@placement.edu"
    DEFAULT_ADMIN_PASSWORD = "Admin@123"
