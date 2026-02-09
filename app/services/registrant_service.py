"""Registrant service."""
import secrets
from datetime import datetime
from app.models import db, Registrant
from app.services.activity_service import check_quota_and_close


def _generate_check_in_code():
    """Unique short code for QR attendance."""
    return secrets.token_urlsafe(12)


def get_registrants_for_activity(activity_id, status=None):
    q = Registrant.query.filter_by(activity_id=activity_id)
    if status:
        q = q.filter_by(status=status)
    return q.order_by(Registrant.created_at.desc()).all()


def create_registrant(activity_id, name, school, phone, email):
    code = _generate_check_in_code()
    while Registrant.query.filter_by(check_in_code=code).first():
        code = _generate_check_in_code()
    reg = Registrant(
        activity_id=activity_id,
        name=name,
        school=school,
        phone=phone or "",
        email=email,
        status="pending",
        check_in_code=code,
    )
    db.session.add(reg)
    db.session.commit()
    activity = reg.activity
    check_quota_and_close(activity)
    return reg


def set_registrant_status(registrant_id, status):
    reg = Registrant.query.get_or_404(registrant_id)
    reg.status = status
    db.session.commit()
    return reg


def verify_registrant(registrant_id):
    return set_registrant_status(registrant_id, "verified")


def get_registrant_by_check_in_code(code):
    return Registrant.query.filter_by(check_in_code=code).first()


def mark_attended(registrant_id):
    reg = Registrant.query.get_or_404(registrant_id)
    if reg.attended_at:
        return reg
    reg.attended_at = datetime.utcnow()
    db.session.commit()
    return reg


def mark_attended_by_code(code):
    reg = get_registrant_by_check_in_code(code)
    if not reg:
        return None
    if reg.attended_at:
        return reg
    reg.attended_at = datetime.utcnow()
    db.session.commit()
    return reg


def ensure_check_in_code(reg):
    """Backfill check_in_code for registrants created before Phase 3."""
    if reg.check_in_code:
        return reg.check_in_code
    code = _generate_check_in_code()
    while Registrant.query.filter_by(check_in_code=code).first():
        code = _generate_check_in_code()
    reg.check_in_code = code
    db.session.commit()
    return code
