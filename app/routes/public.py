
import os
from datetime import date
from flask import Blueprint, render_template, redirect, url_for, flash, send_from_directory, current_app
from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email

from app.models import Activity
from app.services.year_service import get_active_year
from app.services.activity_service import get_activities_for_year, get_activity_or_404
from app.services.registrant_service import create_registrant
from app.services.about_service import get_about
from app.services.contact_service import create_message


"""Public routes: landing, events, competition detail, guidelines, registration, about, contact, gallery."""
public_bp = Blueprint("public", __name__)

@public_bp.route("/uploads/sponsor/<path:filename>")
def serve_sponsor_logo(filename):
    folder = os.path.join(current_app.root_path, "uploads", "sponsor")
    return send_from_directory(folder, filename)

from app.services.gallery_service import get_gallery_for_activity, get_featured_photos, get_recent_gallery_photos
from app.services.registrant_service import mark_attended_by_code, get_registrant_by_check_in_code
from app.services.whatsapp_service import notify_registration_confirmation
from app.services.sponsor_service import SponsorService


class RegistrationForm(FlaskForm):
    name = StringField("Full Name", validators=[DataRequired()])
    school = StringField("School / Institution", validators=[DataRequired()])
    phone = StringField("Phone (optional)")
    email = EmailField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Register")


class ContactForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    message = TextAreaField("Message", validators=[DataRequired()])
    submit = SubmitField("Send message")


def _next_countdown_date(activities):
    """Next activity date (open or upcoming) for countdown."""
    today = date.today()
    for act in sorted(activities, key=lambda a: (a.date or date.max)):
        if act.date and act.date >= today and act.status in ("open", "upcoming"):
            return act.date
    return None


@public_bp.route("/")
def index():
    active_year = get_active_year()
    activities = get_activities_for_year(year_active=True) if active_year else []
    countdown_date = _next_countdown_date(activities) if activities else None
    featured = get_featured_photos(limit=8)
    gallery_photos = featured if featured else get_recent_gallery_photos(limit=8)
    sponsors = SponsorService.get_all(year_id=active_year.id) if active_year else []
    return render_template(
        "public/index.html",
        active_year=active_year,
        activities=activities,
        countdown_date=countdown_date,
        featured_photos=featured,
        gallery_photos=gallery_photos,
        sponsors=sponsors,
    )


@public_bp.route("/events")
def events():
    active_year = get_active_year()
    activities = get_activities_for_year(year_active=True) if active_year else []
    return render_template("public/events.html", active_year=active_year, activities=activities)


@public_bp.route("/about")
def about():
    about_content = get_about()
    return render_template("public/about.html", about_content=about_content)


@public_bp.route("/contact", methods=["GET", "POST"])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        create_message(form.name.data, form.email.data, form.message.data)
        flash("Pesan Anda telah terkirim. Kami akan segera membalas.", "success")
        return redirect(url_for("public.contact"))
    whatsapp = current_app.config.get("WHATSAPP_NUMBER", "")
    return render_template("public/contact.html", form=form, whatsapp_number=whatsapp)


@public_bp.route("/competition/<int:activity_id>")
def competition_detail(activity_id):
    activity = get_activity_or_404(activity_id)
    gallery = get_gallery_for_activity(activity_id)
    countdown_date = activity.date if activity.date and activity.status in ("open", "upcoming") else None
    return render_template(
        "public/competition_detail.html",
        activity=activity,
        gallery=gallery,
        countdown_date=countdown_date,
    )


@public_bp.route("/competition/<int:activity_id>/guideline")
def download_guideline(activity_id):
    activity = get_activity_or_404(activity_id)
    if not activity.guideline_file:
        flash("Berkas panduan untuk lomba ini tidak tersedia.", "warning")
        return redirect(url_for("public.competition_detail", activity_id=activity_id))
    folder = current_app.config["UPLOAD_FOLDER"]
    path = os.path.join(str(folder), activity.guideline_file)
    if not os.path.isfile(path):
        flash("Berkas panduan tidak ditemukan.", "error")
        return redirect(url_for("public.competition_detail", activity_id=activity_id))
    return send_from_directory(
        str(folder),
        activity.guideline_file,
        as_attachment=True,
        download_name=f"guideline-{activity.title[:30].replace(' ', '-')}.pdf",
    )


@public_bp.route("/competition/<int:activity_id>/register", methods=["GET", "POST"])
def register(activity_id):
    activity = get_activity_or_404(activity_id)
    if not activity.can_register:
        flash("Pendaftaran belum dibuka atau kuota sudah penuh.", "warning")
        return redirect(url_for("public.competition_detail", activity_id=activity_id))

    form = RegistrationForm()
    if form.validate_on_submit():
        reg = create_registrant(
            activity_id=activity.id,
            name=form.name.data,
            school=form.school.data,
            phone=form.phone.data,
            email=form.email.data,
        )
        notify_registration_confirmation(reg, activity)
        flash("Pendaftaran berhasil dikirim. Kami akan memverifikasi pendaftaran Anda segera.", "success")
        return redirect(url_for("public.competition_detail", activity_id=activity_id))

    return render_template("public/register.html", activity=activity, form=form)


@public_bp.route("/competition/<int:activity_id>/gallery")
def activity_gallery(activity_id):
    activity = get_activity_or_404(activity_id)
    gallery = get_gallery_for_activity(activity_id)
    return render_template("public/gallery.html", activity=activity, gallery=gallery)


@public_bp.route("/uploads/gallery/<path:filename>")
def serve_gallery_image(filename):
    folder = current_app.config["GALLERY_UPLOAD_FOLDER"]
    return send_from_directory(str(folder), filename)


@public_bp.route("/checkin/<code>")
def checkin(code):
    """QR code attendance: scan opens this URL and marks the registrant as attended."""
    reg = get_registrant_by_check_in_code(code)
    if not reg:
        return render_template("public/checkin_result.html", success=False, registrant=None)
    already = reg.attended_at
    if not already:
        mark_attended_by_code(code)
    return render_template("public/checkin_result.html", success=True, registrant=reg, already_attended=already)

@public_bp.route("/health")
def health():
    return "OK", 200
