from app.models.sponsor import Sponsor
from app.models import db

class SponsorService:
    @staticmethod
    def get_all(year_id=None):
        q = Sponsor.query
        if year_id:
            q = q.filter_by(year_id=year_id)
        return q.order_by(Sponsor.created_at.desc()).all()

    @staticmethod
    def add(name, logo, year_id, link=None):
        sponsor = Sponsor(name=name, logo=logo, link=link, year_id=year_id)
        db.session.add(sponsor)
        db.session.commit()
        return sponsor

    @staticmethod
    def update(sponsor_id, name, logo=None, link=None, year_id=None):
        sponsor = Sponsor.query.get_or_404(sponsor_id)
        sponsor.name = name
        if logo:
            sponsor.logo = logo
        sponsor.link = link
        if year_id:
            sponsor.year_id = year_id
        db.session.commit()
        return sponsor

    @staticmethod
    def delete(sponsor_id):
        sponsor = Sponsor.query.get_or_404(sponsor_id)
        db.session.delete(sponsor)
        db.session.commit()
