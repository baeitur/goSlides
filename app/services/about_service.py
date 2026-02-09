"""About page content (singleton)."""
from app.models import db, About


def get_about():
    row = About.query.first()
    if row is None:
        row = About(title="About Go Slides", description="", goals="", location="")
        db.session.add(row)
        db.session.commit()
    return row


def update_about(title=None, description=None, goals=None, location=None):
    row = get_about()
    if title is not None:
        row.title = title
    if description is not None:
        row.description = description
    if goals is not None:
        row.goals = goals
    if location is not None:
        row.location = location
    db.session.commit()
    return row
