import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret")
    database_url = os.getenv("DATABASE_URL", "sqlite:///agridoc_dev.db")
    if database_url == "sqlite:///agridoc_dev.db":
        database_url = f"sqlite:///{(BASE_DIR / 'instance' / 'agridoc_dev.db').as_posix()}"
    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", str(BASE_DIR / "uploads"))
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))
    ALLOWED_EXTENSIONS = {ext.strip().lower() for ext in os.getenv("ALLOWED_EXTENSIONS", "jpg,jpeg,png,webp").split(",") if ext.strip()}
    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
    MODEL_CONFIDENCE_THRESHOLD = float(os.getenv("MODEL_CONFIDENCE_THRESHOLD", "0.35"))
    DISEASE_MODEL_PATH = os.getenv("DISEASE_MODEL_PATH", str(BASE_DIR / "ml_models" / "disease_model" / "disease_model.keras"))
