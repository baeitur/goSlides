"""Authentication service."""
import hashlib
from passlib.context import CryptContext
from passlib.exc import UnknownHashError
from app.models import db, User, ROLE_SUPER_ADMIN

pwd_context = CryptContext(schemes=["pbkdf2_sha256", "scrypt"], default="pbkdf2_sha256")


def _verify_legacy_scrypt(password, hash_value):
    try:
        method, salt, digest_hex = hash_value.split("$")
        _, n, r, p = method.split(":")
        n, r, p = int(n), int(r), int(p)
    except ValueError:
        return False

    password_bytes = password.encode("utf-8")
    salt_bytes = salt.encode("utf-8")
    dklen = len(digest_hex) // 2
    maxmem = 132 * n * r * p

    try:
        digest = hashlib.scrypt(
            password_bytes,
            salt=salt_bytes,
            n=n,
            r=r,
            p=p,
            dklen=dklen,
            maxmem=maxmem,
        )
    except ValueError:
        return False

    return digest.hex() == digest_hex


def _verify_legacy_pbkdf2(password, hash_value):
    try:
        method, salt, digest_hex = hash_value.split("$")
        _, hash_name, iterations = method.split(":")
        iterations = int(iterations)
    except ValueError:
        return False

    password_bytes = password.encode("utf-8")
    salt_bytes = salt.encode("utf-8")
    digest = hashlib.pbkdf2_hmac(hash_name, password_bytes, salt_bytes, iterations)
    return digest.hex() == digest_hex


def ensure_admin_exists():
    """Create default Super Admin if no users exist."""
    if User.query.first() is not None:
        return
    admin = User(
        name="Admin",
        email="admin@goslides.com",
        password=pwd_context.hash("admin123"),
        role=ROLE_SUPER_ADMIN,
    )
    db.session.add(admin)
    db.session.commit()


def get_user_by_email(email):
    return User.query.filter_by(email=email).first()


def verify_password(user, password):
    try:
        return pwd_context.verify(password, user.password)
    except UnknownHashError:
        if user.password.startswith("scrypt:"):
            return _verify_legacy_scrypt(password, user.password)
        if user.password.startswith("pbkdf2:"):
            return _verify_legacy_pbkdf2(password, user.password)
        return False
