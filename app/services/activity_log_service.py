"""Activity logging for admin actions."""
from flask_login import current_user
from app.models import db, ActivityLog


def log_action(action, entity_type=None, entity_id=None, details=None):
    """Record an action in the activity log."""
    user_id = current_user.id if current_user.is_authenticated else None
    entry = ActivityLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id) if entity_id is not None else None,
        details=details,
    )
    db.session.add(entry)
    db.session.commit()
    return entry


def get_recent_logs(limit=50):
    """Get most recent activity log entries."""
    return ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(limit).all()
