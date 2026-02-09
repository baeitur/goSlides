"""Dashboard statistics for Chart.js and summary cards."""
from datetime import datetime, timedelta
from sqlalchemy import func
from app.models import Year, Activity, Registrant


def get_dashboard_stats(active_year=None):
    """Return stats for dashboard: counts and time-series for Chart.js."""
    if active_year:
        year_id = active_year.id
        activities = Activity.query.filter_by(year_id=year_id).all()
        activity_ids = [a.id for a in activities]
    else:
        activities = []
        activity_ids = []

    total_registrants = Registrant.query.filter(Registrant.activity_id.in_(activity_ids)).count() if activity_ids else 0
    verified = Registrant.query.filter(Registrant.activity_id.in_(activity_ids), Registrant.status == "verified").count() if activity_ids else 0
    attended = Registrant.query.filter(Registrant.activity_id.in_(activity_ids), Registrant.attended_at.isnot(None)).count() if activity_ids else 0

    # Per-activity counts for bar chart
    activity_labels = []
    activity_counts = []
    for a in activities:
        activity_labels.append(a.title[:20] + ("..." if len(a.title) > 20 else ""))
        activity_counts.append(a.registrants.count())

    # Registrations over last 14 days (for line chart)
    days_back = 14
    today = datetime.utcnow().date()
    start = today - timedelta(days=days_back)
    if activity_ids:
        rows = (
            Registrant.query.filter(
                Registrant.activity_id.in_(activity_ids),
                func.date(Registrant.created_at) >= start,
            )
            .with_entities(func.date(Registrant.created_at).label("day"), func.count(Registrant.id).label("count"))
            .group_by(func.date(Registrant.created_at))
            .order_by(func.date(Registrant.created_at))
            .all()
        )
        regs_by_day = {str(r.day): r.count for r in rows}
    else:
        regs_by_day = {}

    day_labels = [(start + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days_back + 1)]
    regs_per_day = [regs_by_day.get(d, 0) for d in day_labels]

    return {
        "total_activities": len(activities),
        "total_registrants": total_registrants,
        "verified_count": verified,
        "attended_count": attended,
        "activity_labels": activity_labels or [],
        "activity_counts": activity_counts or [],
        "day_labels": day_labels,
        "regs_per_day": regs_per_day,
    }
