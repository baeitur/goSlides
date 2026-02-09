"""Activity (competition/event) service."""
import os
import uuid
from flask import current_app
from app.models import db, Activity


def get_activities_for_year(year_id=None, year_active=False):
    q = Activity.query
    if year_id is not None:
        q = q.filter_by(year_id=year_id)
    if year_active:
        q = q.join(Activity.year).filter_by(active=True)
    return q.order_by(Activity.date.asc().nulls_last(), Activity.created_at.desc()).all()


def get_activity_or_404(activity_id):
    return Activity.query.get_or_404(activity_id)


def create_activity(year_id, title, description, date, type_, status, quota, guideline_file=None):
    act = Activity(
        year_id=year_id,
        title=title,
        description=description or "",
        date=date,
        type=type_,
        status=status or "upcoming",
        quota=quota,
        guideline_file=guideline_file,
    )
    db.session.add(act)
    db.session.commit()
    return act


def update_activity(activity_id, **kwargs):
    act = Activity.query.get_or_404(activity_id)
    for key, value in kwargs.items():
        if hasattr(act, key):
            setattr(act, key, value)
    db.session.commit()
    return act


def delete_activity(activity_id):
    act = Activity.query.get_or_404(activity_id)
    if act.guideline_file:
        path = os.path.join(current_app.config["UPLOAD_FOLDER"], act.guideline_file)
        if os.path.isfile(path):
            os.remove(path)
    db.session.delete(act)
    db.session.commit()


def save_guideline_file(file_storage):
    """Save uploaded PDF; return stored filename."""
    if not file_storage or not file_storage.filename:
        return None
    ext = file_storage.filename.rsplit(".", 1)[-1].lower()
    if ext != "pdf":
        return None
    filename = f"{uuid.uuid4().hex}.pdf"
    path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    file_storage.save(path)
    return filename


def check_quota_and_close(activity):
    """If activity has quota and registrants >= quota, set status to closed."""
    if activity.quota is None:
        return
    if activity.registrants.count() >= activity.quota:
        activity.status = "closed"
        db.session.commit()
