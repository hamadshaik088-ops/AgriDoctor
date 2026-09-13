import os
from uuid import uuid4
from flask import current_app
from werkzeug.utils import secure_filename


def allowed_file(filename):
    if not filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower() if "." in filename else ""
    return ext in current_app.config.get("ALLOWED_EXTENSIONS", {"jpg", "jpeg", "png", "webp"})


def save_uploaded_image(file_storage):
    if not file_storage or not allowed_file(file_storage.filename):
        raise ValueError("Invalid image file. Only JPG, JPEG, PNG, and WEBP are allowed.")
    filename = secure_filename(file_storage.filename)
    upload_dir = current_app.config.get("UPLOAD_FOLDER", "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    filename = f"{uuid4().hex}_{filename}"
    full_path = os.path.join(upload_dir, filename)
    file_storage.save(full_path)
    return full_path
