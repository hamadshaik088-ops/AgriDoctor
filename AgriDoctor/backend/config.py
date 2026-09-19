import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / "instance"
INSTANCE_DIR.mkdir(parents=True, exist_ok=True)
load_dotenv(BASE_DIR / ".env")


def _resolve_database_url():
    database_url = os.getenv("DATABASE_URL", "").strip()
    if not database_url:
        database_url = f"sqlite:///{INSTANCE_DIR / 'agridoctor.db'}"

    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    return database_url.strip()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "local-development-secret-change-me")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "local-development-jwt-secret-change-me-32")
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", "86400"))
    SQLALCHEMY_DATABASE_URI = _resolve_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    upload_folder = os.getenv("UPLOAD_FOLDER", "uploads").strip()
    UPLOAD_FOLDER = str(Path(upload_folder) if Path(upload_folder).is_absolute() else BASE_DIR / upload_folder)
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))
    ALLOWED_EXTENSIONS = {ext.strip().lower() for ext in os.getenv("ALLOWED_EXTENSIONS", "jpg,jpeg,png,webp").split(",") if ext.strip()}
    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
    PLANT_ID_API_KEY = os.getenv("PLANT_ID_API_KEY", "")
    MODEL_CONFIDENCE_THRESHOLD = float(os.getenv("MODEL_CONFIDENCE_THRESHOLD", "0.35"))


Path(Config.UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)
