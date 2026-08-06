"""
files.py

Helpers for secure file saving, deletion and download responses.
"""

import os
from datetime import datetime

from flask import current_app, send_from_directory
from werkzeug.utils import secure_filename


def _unique_filename(prefix, original_filename):
    ext = original_filename.rsplit(".", 1)[1].lower()
    stamp = datetime.now().strftime("%Y%m%d%H%M%S")
    safe = secure_filename(original_filename.rsplit(".", 1)[0]) or "file"
    return f"{prefix}_{stamp}_{safe[:40]}.{ext}"


def save_resume(file_storage):
    """Save an uploaded resume PDF and return its relative path."""
    filename = _unique_filename("resume", file_storage.filename)
    folder = current_app.config["RESUME_FOLDER"]
    os.makedirs(folder, exist_ok=True)
    file_storage.save(os.path.join(folder, filename))
    return f"resumes/{filename}"


def save_offer(file_storage):
    """Save an uploaded offer-letter PDF and return its relative path."""
    filename = _unique_filename("offer", file_storage.filename)
    folder = current_app.config["OFFER_FOLDER"]
    os.makedirs(folder, exist_ok=True)
    file_storage.save(os.path.join(folder, filename))
    return f"offers/{filename}"


def save_image(file_storage):
    """Save an uploaded image (logo / profile picture) and return its relative path."""
    filename = _unique_filename("img", file_storage.filename)
    folder = current_app.config["IMAGE_FOLDER"]
    os.makedirs(folder, exist_ok=True)
    file_storage.save(os.path.join(folder, filename))
    return f"images/{filename}"


def delete_upload(relative_path):
    """Delete an uploaded file by its relative path (e.g. resumes/foo.pdf)."""
    if not relative_path:
        return
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    full_path = os.path.join(upload_folder, relative_path)
    if os.path.isfile(full_path):
        os.remove(full_path)


def download_upload(relative_path):
    """Return a send_from_directory response for a stored upload."""
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    directory = os.path.dirname(os.path.join(upload_folder, relative_path))
    filename = os.path.basename(relative_path)
    return send_from_directory(directory, filename, as_attachment=True)
