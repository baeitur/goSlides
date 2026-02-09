"""Go Slides - School Event & Competition Platform."""
import os
from flask import Flask
from flask_login import LoginManager

from app.config import Config
from app.models import db, User


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure instance and upload folders exist
    db_path = app.config["SQLALCHEMY_DATABASE_URI"].replace("sqlite:///", "")
    if db_path.startswith("/"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["GALLERY_UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "admin.login"
    login_manager.login_message = "Silakan masuk untuk mengakses area admin."

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        # Pastikan folder instance selalu ada (untuk SQLite)
        instance_dir = os.path.join(app.root_path, "instance")
        os.makedirs(instance_dir, exist_ok=True)
        db.create_all()
        # Create default admin if none exists
        from app.services.auth_service import ensure_admin_exists
        ensure_admin_exists()

    # Register blueprints
    from app.routes.public import public_bp
    from app.routes.admin import admin_bp
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")

    from app.services.year_service import get_active_year
    @app.context_processor
    def inject_event_theme():
        year = get_active_year()
        return {'event_theme': year.theme if year and year.theme else 'Dari Acara ke Prestasi'}

    return app
