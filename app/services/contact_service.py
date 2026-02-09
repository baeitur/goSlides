"""Contact form messages."""
from app.models import db, ContactMessage


def create_message(name, email, message):
    msg = ContactMessage(name=name, email=email, message=message)
    db.session.add(msg)
    db.session.commit()
    return msg


def get_all_messages():
    return ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
