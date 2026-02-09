"""Year management service."""
from app.models import db, Year


def get_active_year():
    return Year.query.filter_by(active=True).first()


def get_all_years():
    return Year.query.order_by(Year.created_at.desc()).all()


def set_active_year(year_id):
    """Set only the given year as active; deactivate others."""
    Year.query.update({"active": False})
    year = Year.query.get(year_id)
    if year:
        year.active = True
    db.session.commit()
    return year


def create_year(name):
    years = Year.query.all()
    active = len(years) == 0
    year = Year(name=name, active=active)
    db.session.add(year)
    db.session.commit()
    return year

def create_year(name, theme=None):
    years = Year.query.all()
    active = len(years) == 0
    year = Year(name=name, theme=theme, active=active)
    db.session.add(year)
    db.session.commit()
    return year


def update_year(year_id, name):
    year = Year.query.get_or_404(year_id)
    year.name = name
    db.session.commit()
    return year

def update_year(year_id, name, theme=None):
    year = Year.query.get_or_404(year_id)
    year.name = name
    year.theme = theme
    db.session.commit()
    return year


def delete_year(year_id):
    year = Year.query.get_or_404(year_id)
    db.session.delete(year)
    db.session.commit()
