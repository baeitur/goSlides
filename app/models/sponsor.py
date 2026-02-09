from . import db

class Sponsor(db.Model):
    __tablename__ = 'sponsors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    logo = db.Column(db.String(255), nullable=False)  # path to image file
    link = db.Column(db.String(255), nullable=True)
    year_id = db.Column(db.Integer, db.ForeignKey('years.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f"<Sponsor {self.name}>"
