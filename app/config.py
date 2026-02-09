"""Application configuration."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")

    # ================= DATABASE =================

    DATABASE_URL = os.environ.get("DATABASE_URL")

    if DATABASE_URL:
        # Render provides postgres:// but SQLAlchemy needs postgresql://
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

        SQLALCHEMY_DATABASE_URI = DATABASE_URL

    else:
        # Local SQLite fallback
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{BASE_DIR / 'instance' / 'goslides.db'}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True
    }

    # ================= UPLOAD PATHS =================

    UPLOAD_FOLDER = BASE_DIR / "app" / "uploads" / "guidelines"
    SPONSOR_UPLOAD_FOLDER = BASE_DIR / "app" / "uploads" / "sponsor"
    GALLERY_UPLOAD_FOLDER = BASE_DIR / "app" / "uploads" / "gallery"

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

    ALLOWED_EXTENSIONS = {"pdf"}
    ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

    # ================= WHATSAPP =================

    WHATSAPP_NUMBER = os.environ.get("WHATSAPP_NUMBER", "6281317707705").replace(" ", "")

    WHATSAPP_ACCOUNT_SID = os.environ.get("WHATSAPP_ACCOUNT_SID", "")
    WHATSAPP_AUTH_TOKEN = os.environ.get("WHATSAPP_AUTH_TOKEN", "")
    WHATSAPP_FROM_NUMBER = os.environ.get("WHATSAPP_FROM_NUMBER", "").replace(" ", "")
