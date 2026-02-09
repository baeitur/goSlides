"""Application configuration."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "go-slides-dev-secret-key-change-in-production"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or f"sqlite:///{BASE_DIR / 'instance' / 'goslides.db'}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = BASE_DIR / "app" / "uploads" / "guidelines"
    SPONSOR_UPLOAD_FOLDER = BASE_DIR / "app" / "uploads" / "sponsor"
    GALLERY_UPLOAD_FOLDER = BASE_DIR / "app" / "uploads" / "gallery"
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB for PDFs and images
    ALLOWED_EXTENSIONS = {"pdf"}
    ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
    WHATSAPP_NUMBER = os.environ.get("WHATSAPP_NUMBER", "6281317707705").replace(" ", "")  # e.g. 6281234567890
    
    # WhatsApp Business API (e.g. Twilio): set to send notifications
    WHATSAPP_ACCOUNT_SID = os.environ.get("WHATSAPP_ACCOUNT_SID", "")
    WHATSAPP_AUTH_TOKEN = os.environ.get("WHATSAPP_AUTH_TOKEN", "")
    WHATSAPP_FROM_NUMBER = os.environ.get("WHATSAPP_FROM_NUMBER", "").replace(" ", "")  # Twilio WhatsApp sandbox number
