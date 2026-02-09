"""Role-based access decorators."""
from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

from app.models import ROLE_SUPER_ADMIN, ROLE_OPERATOR


def role_required(*allowed_roles):
    """Require user to have one of the given roles. Use after @login_required."""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("admin.login"))
            if current_user.role not in allowed_roles:
                flash("Anda tidak memiliki izin untuk mengakses halaman ini.", "error")
                return redirect(url_for("admin.dashboard"))
            return f(*args, **kwargs)
        return wrapped
    return decorator


def super_admin_required(f):
    """Require Super Admin role."""
    return role_required(ROLE_SUPER_ADMIN)(f)


def operator_or_above(f):
    """Allow both Operator and Super Admin (default for most admin routes)."""
    return role_required(ROLE_SUPER_ADMIN, ROLE_OPERATOR)(f)
