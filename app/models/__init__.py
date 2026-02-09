"""Database models."""
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


# Role constants for role-based access
ROLE_SUPER_ADMIN = "super_admin"
ROLE_OPERATOR = "operator"


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(32), nullable=False, default=ROLE_OPERATOR)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    @property
    def is_super_admin(self):
        return self.role == ROLE_SUPER_ADMIN

    def __repr__(self):
        return f"<User {self.email}>"


class Year(db.Model):
    __tablename__ = "years"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    theme = db.Column(db.String(255), nullable=True)
    active = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    activities = db.relationship("Activity", backref="year", lazy="dynamic", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Year {self.name}>"


class Activity(db.Model):
    __tablename__ = "activities"
    id = db.Column(db.Integer, primary_key=True)
    year_id = db.Column(db.Integer, db.ForeignKey("years.id", ondelete="CASCADE"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.Date)
    type = db.Column(db.String(32), nullable=False, default="competition")
    status = db.Column(db.String(32), nullable=False, default="upcoming")
    quota = db.Column(db.Integer)
    guideline_file = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    registrants = db.relationship("Registrant", backref="activity", lazy="dynamic", cascade="all, delete-orphan")

    @property
    def is_full(self):
        if self.quota is None:
            return False
        return self.registrants.count() >= self.quota

    @property
    def can_register(self):
        return self.status == "open" and not self.is_full

    def __repr__(self):
        return f"<Activity {self.title}>"


class Registrant(db.Model):
    __tablename__ = "registrants"
    id = db.Column(db.Integer, primary_key=True)
    activity_id = db.Column(db.Integer, db.ForeignKey("activities.id", ondelete="CASCADE"), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    school = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(64))
    email = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(32), nullable=False, default="pending")
    check_in_code = db.Column(db.String(64), unique=True, nullable=True)  # for QR attendance
    attended_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f"<Registrant {self.name}>"


class Gallery(db.Model):
    __tablename__ = "gallery"
    id = db.Column(db.Integer, primary_key=True)
    year_id = db.Column(db.Integer, db.ForeignKey("years.id", ondelete="CASCADE"), nullable=False)
    activity_id = db.Column(db.Integer, db.ForeignKey("activities.id", ondelete="CASCADE"), nullable=True)
    file = db.Column(db.String(255), nullable=False)
    caption = db.Column(db.String(512))
    is_featured = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    year = db.relationship("Year", backref=db.backref("gallery_items", lazy="dynamic"))
    activity = db.relationship("Activity", backref=db.backref("gallery_items", lazy="dynamic"))


class About(db.Model):
    __tablename__ = "about"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False, default="About Go Slides")
    description = db.Column(db.Text)
    goals = db.Column(db.Text)
    location = db.Column(db.String(512))


class ContactMessage(db.Model):
    __tablename__ = "contact_messages"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())


class ActivityLog(db.Model):
    __tablename__ = "activity_log"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = db.Column(db.String(64), nullable=False)  # create, update, delete, login, etc.
    entity_type = db.Column(db.String(64), nullable=True)  # year, activity, registrant, about, etc.
    entity_id = db.Column(db.String(64), nullable=True)
    details = db.Column(db.Text, nullable=True)  # JSON or short description
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    user = db.relationship("User", backref="activity_logs")


from .sponsor import Sponsor
