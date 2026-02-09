"""Authentication service."""
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db, User, ROLE_SUPER_ADMIN


def ensure_admin_exists():
    """Create default Super Admin if no users exist."""
    if User.query.first() is not None:
        return
    admin = User(
        name="Admin",
        email="admin@goslides.com",
        password=generate_password_hash("admin123", method="scrypt"),
        role=ROLE_SUPER_ADMIN,
    )
    db.session.add(admin)
    db.session.commit()


def get_user_by_email(email):
    return User.query.filter_by(email=email).first()


def verify_password(user, password):
    return check_password_hash(user.password, password)
