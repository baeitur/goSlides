"""Admin routes: login, years, activities, registrants, about, contact, gallery, backup, activity log, PDF export, QR."""
import os
import io
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file, current_app
from flask_login import login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, EmailField, PasswordField, SubmitField, TextAreaField, SelectField, IntegerField, DateField, BooleanField
from wtforms.validators import DataRequired, Email, Optional
import qrcode

from app.models import db, User, Year, Activity, Registrant, Gallery
from app.utils.decorators import operator_or_above, super_admin_required
from app.services.auth_service import get_user_by_email, verify_password
from app.services.year_service import get_all_years, set_active_year, create_year, update_year, delete_year
from app.services.activity_service import (
    get_activities_for_year,
    get_activity_or_404,
    create_activity,
    update_activity,
    delete_activity,
    save_guideline_file,
)
from app.services.registrant_service import (
    get_registrants_for_activity,
    verify_registrant,
    set_registrant_status,
    mark_attended,
    ensure_check_in_code,
)
from app.services.about_service import get_about, update_about
from app.services.contact_service import get_all_messages
from app.services.gallery_service import (
    get_gallery_for_activity,
    save_gallery_image,
    add_gallery_item,
    delete_gallery_item,
    set_featured,
)
from app.services.activity_log_service import log_action, get_recent_logs
from app.services.dashboard_service import get_dashboard_stats
from app.services.pdf_export_service import export_registrants_pdf
from app.services.sponsor_service import SponsorService

admin_bp = Blueprint("admin", __name__)


# ---- Auth forms ----
class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log In")


# ---- Year forms ----
class YearForm(FlaskForm):
    name = StringField("Year Name", validators=[DataRequired()])
    theme = StringField("Tema Acara")
    submit = SubmitField("Save")


# ---- Activity forms ----
class ActivityForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    description = TextAreaField("Description")
    date = DateField("Date", format="%Y-%m-%d", validators=[Optional()])
    type = SelectField("Type", choices=[("competition", "Competition"), ("non-competition", "Non-Competition")])
    status = SelectField("Status", choices=[("open", "Open"), ("upcoming", "Upcoming"), ("closed", "Closed")])
    quota = IntegerField("Quota (leave empty for no limit)", validators=[Optional()])
    guideline = FileField("Guideline PDF", validators=[FileAllowed(["pdf"], "PDF only")])
    submit = SubmitField("Save")


# ---- About form ----
class AboutForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    description = TextAreaField("Description")
    goals = TextAreaField("Goals")
    location = StringField("Location")
    submit = SubmitField("Save")


# ---- Gallery upload form ----
class GalleryUploadForm(FlaskForm):
    image = FileField("Image", validators=[FileAllowed(["png", "jpg", "jpeg", "gif", "webp"], "Images only")])
    caption = StringField("Caption")
    is_featured = BooleanField("Feature on homepage", default=False)
    submit = SubmitField("Upload")


# ---- Sponsor form ----
class SponsorForm(FlaskForm):
    name = StringField("Nama Sponsor", validators=[DataRequired()])
    logo = FileField("Logo", validators=[FileAllowed(["jpg", "jpeg", "png", "gif", "webp"], "Image only!")])
    link = StringField("Link (opsional)")
    submit = SubmitField("Simpan")


# ---- Routes ----
@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("admin.dashboard"))
    form = LoginForm()
    if form.validate_on_submit():
        user = get_user_by_email(form.email.data)
        if user and verify_password(user, form.password.data):
            login_user(user)
            log_action("login", details=user.email)
            flash("Berhasil masuk.", "success")
            next_url = request.args.get("next") or url_for("admin.dashboard")
            return redirect(next_url)
        flash("Email atau kata sandi salah.", "error")
    return render_template("admin/login.html", form=form)


@admin_bp.route("/logout")
@login_required
def logout():
    log_action("logout")
    logout_user()
    flash("Anda telah keluar.", "info")
    return redirect(url_for("public.index"))


@admin_bp.route("/")
@login_required
@operator_or_above
def dashboard():
    years = get_all_years()
    active_year = next((y for y in years if y.active), None)
    activities = get_activities_for_year(active_year.id) if active_year else []
    stats = get_dashboard_stats(active_year) if active_year else {}
    return render_template(
        "admin/dashboard.html",
        years=years,
        active_year=active_year,
        activities=activities,
        stats=stats,
    )


# ---- Years ----
@admin_bp.route("/years", methods=["GET", "POST"])
@login_required
@operator_or_above
def years_list():
    years = get_all_years()
    form = YearForm()
    if form.validate_on_submit():
        create_year(form.name.data, form.theme.data)
        log_action("create", entity_type="year", details=f"{form.name.data} | {form.theme.data}")
        flash("Tahun berhasil ditambahkan.", "success")
        return redirect(url_for("admin.years_list"))
    return render_template("admin/years.html", years=years, form=form)


@admin_bp.route("/years/<int:year_id>/activate", methods=["POST"])
@login_required
@operator_or_above
def year_activate(year_id):
    set_active_year(year_id)
    log_action("update", entity_type="year", entity_id=year_id, details="set active")
    flash("Tahun aktif diperbarui.", "success")
    return redirect(url_for("admin.years_list"))


@admin_bp.route("/years/<int:year_id>/edit", methods=["GET", "POST"])
@login_required
@operator_or_above
def year_edit(year_id):
    year = Year.query.get_or_404(year_id)
    form = YearForm(obj=year)
    if form.validate_on_submit():
        update_year(year_id, form.name.data, form.theme.data)
        log_action("update", entity_type="year", entity_id=year_id, details=f"{form.name.data} | {form.theme.data}")
        flash("Tahun diperbarui.", "success")
        return redirect(url_for("admin.years_list"))
    return render_template("admin/year_edit.html", year=year, form=form)


@admin_bp.route("/years/<int:year_id>/delete", methods=["POST"])
@login_required
@super_admin_required
def year_delete(year_id):
    delete_year(year_id)
    log_action("delete", entity_type="year", entity_id=year_id)
    flash("Tahun dihapus.", "success")
    return redirect(url_for("admin.years_list"))


# ---- Activities ----
@admin_bp.route("/years/<int:year_id>/activities", methods=["GET"])
@login_required
@operator_or_above
def activities_list(year_id):
    year = Year.query.get_or_404(year_id)
    activities = get_activities_for_year(year_id=year_id)
    return render_template("admin/activities.html", year=year, activities=activities)


@admin_bp.route("/years/<int:year_id>/activities/new", methods=["GET", "POST"])
@login_required
@operator_or_above
def activity_new(year_id):
    year = Year.query.get_or_404(year_id)
    form = ActivityForm()
    if form.validate_on_submit():
        guideline_file = save_guideline_file(form.guideline.data) if form.guideline.data else None
        act = create_activity(
            year_id=year_id,
            title=form.title.data,
            description=form.description.data,
            date=form.date.data,
            type_=form.type.data,
            status=form.status.data,
            quota=form.quota.data,
            guideline_file=guideline_file,
        )
        log_action("create", entity_type="activity", entity_id=act.id, details=act.title)
        flash("Acara berhasil ditambahkan.", "success")
        return redirect(url_for("admin.activities_list", year_id=year_id))
    return render_template("admin/activity_form.html", year=year, activity=None, form=form)


@admin_bp.route("/activities/<int:activity_id>/edit", methods=["GET", "POST"])
@login_required
@operator_or_above
def activity_edit(activity_id):
    activity = get_activity_or_404(activity_id)
    form = ActivityForm(obj=activity)
    if form.validate_on_submit():
        guideline_file = activity.guideline_file
        if form.guideline.data:
            new_file = save_guideline_file(form.guideline.data)
            if new_file:
                guideline_file = new_file
        update_activity(
            activity_id,
            title=form.title.data,
            description=form.description.data,
            date=form.date.data,
            type=form.type.data,
            status=form.status.data,
            quota=form.quota.data,
            guideline_file=guideline_file,
        )
        log_action("update", entity_type="activity", entity_id=activity_id, details=form.title.data)
        flash("Acara diperbarui.", "success")
        return redirect(url_for("admin.activities_list", year_id=activity.year_id))
    return render_template("admin/activity_form.html", year=activity.year, activity=activity, form=form)


@admin_bp.route("/activities/<int:activity_id>/delete", methods=["POST"])
@login_required
@super_admin_required
def activity_delete(activity_id):
    activity = get_activity_or_404(activity_id)
    year_id = activity.year_id
    title = activity.title
    delete_activity(activity_id)
    log_action("delete", entity_type="activity", entity_id=activity_id, details=title)
    flash("Acara dihapus.", "success")
    return redirect(url_for("admin.activities_list", year_id=year_id))


# ---- Registrants ----
@admin_bp.route("/activities/<int:activity_id>/registrants", methods=["GET"])
@login_required
@operator_or_above
def registrants_list(activity_id):
    activity = get_activity_or_404(activity_id)
    registrants = get_registrants_for_activity(activity_id)
    base_url = request.url_root.rstrip("/")
    for r in registrants:
        ensure_check_in_code(r)
    return render_template(
        "admin/registrants.html",
        activity=activity,
        registrants=registrants,
        checkin_base_url=base_url,
    )


@admin_bp.route("/activities/<int:activity_id>/registrants/export-pdf", methods=["GET"])
@login_required
@operator_or_above
def registrants_export_pdf(activity_id):
    activity = get_activity_or_404(activity_id)
    registrants = get_registrants_for_activity(activity_id)
    buffer = export_registrants_pdf(activity, registrants)
    filename = f"participants-{activity.title[:30].replace(' ', '-')}.pdf"
    return send_file(buffer, mimetype="application/pdf", as_attachment=True, download_name=filename)


@admin_bp.route("/registrants/<int:registrant_id>/qr", methods=["GET"])
@login_required
@operator_or_above
def registrant_qr(registrant_id):
    reg = Registrant.query.get_or_404(registrant_id)
    ensure_check_in_code(reg)
    checkin_url = request.url_root.rstrip("/") + url_for("public.checkin", code=reg.check_in_code, _external=False)
    img = qrcode.make(checkin_url)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return send_file(buffer, mimetype="image/png")


@admin_bp.route("/registrants/<int:registrant_id>/verify", methods=["POST"])
@login_required
@operator_or_above
def registrant_verify(registrant_id):
    verify_registrant(registrant_id)
    log_action("verify", entity_type="registrant", entity_id=registrant_id)
    flash("Pendaftar telah diverifikasi.", "success")
    reg = Registrant.query.get_or_404(registrant_id)
    return redirect(url_for("admin.registrants_list", activity_id=reg.activity_id))


@admin_bp.route("/registrants/<int:registrant_id>/attend", methods=["POST"])
@login_required
@operator_or_above
def registrant_mark_attended(registrant_id):
    mark_attended(registrant_id)
    log_action("attend", entity_type="registrant", entity_id=registrant_id)
    flash("Ditandai hadir.", "success")
    reg = Registrant.query.get_or_404(registrant_id)
    return redirect(url_for("admin.registrants_list", activity_id=reg.activity_id))


@admin_bp.route("/registrants/<int:registrant_id>/status", methods=["POST"])
@login_required
@operator_or_above
def registrant_status(registrant_id):
    status = request.form.get("status", "pending")
    if status not in ("pending", "verified"):
        status = "pending"
    set_registrant_status(registrant_id, status)
    flash("Status diperbarui.", "success")
    reg = Registrant.query.get_or_404(registrant_id)
    return redirect(url_for("admin.registrants_list", activity_id=reg.activity_id))


# ---- About ----
@admin_bp.route("/about", methods=["GET", "POST"])
@login_required
@operator_or_above
def about_edit():
    about_content = get_about()
    form = AboutForm(obj=about_content)
    if form.validate_on_submit():
        update_about(
            title=form.title.data,
            description=form.description.data,
            goals=form.goals.data,
            location=form.location.data,
        )
        log_action("update", entity_type="about")
        flash("Halaman tentang diperbarui.", "success")
        return redirect(url_for("admin.about_edit"))
    return render_template("admin/about.html", form=form, about_content=about_content)


# ---- Contact messages ----
@admin_bp.route("/contact-messages", methods=["GET"])
@login_required
@operator_or_above
def contact_messages():
    messages = get_all_messages()
    return render_template("admin/contact_messages.html", messages=messages)


# ---- Gallery ----
@admin_bp.route("/activities/<int:activity_id>/gallery", methods=["GET", "POST"])
@login_required
@operator_or_above
def activity_gallery(activity_id):
    activity = get_activity_or_404(activity_id)
    gallery = get_gallery_for_activity(activity_id)
    form = GalleryUploadForm()
    if form.validate_on_submit() and form.image.data:
        filename = save_gallery_image(form.image.data)
        if filename:
            add_gallery_item(
                year_id=activity.year_id,
                activity_id=activity_id,
                file_filename=filename,
                caption=form.caption.data,
                is_featured=form.is_featured.data,
            )
            flash("Gambar berhasil diunggah.", "success")
        else:
            flash("Jenis berkas gambar tidak valid.", "error")
        return redirect(url_for("admin.activity_gallery", activity_id=activity_id))
    return render_template("admin/gallery.html", activity=activity, gallery=gallery, form=form)


@admin_bp.route("/gallery/<int:item_id>/delete", methods=["POST"])
@login_required
@operator_or_above
def gallery_item_delete(item_id):
    item = Gallery.query.get_or_404(item_id)
    activity_id = item.activity_id
    delete_gallery_item(item_id)
    flash("Gambar dihapus.", "success")
    if activity_id:
        return redirect(url_for("admin.activity_gallery", activity_id=activity_id))
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/gallery/<int:item_id>/featured", methods=["POST"])
@login_required
@operator_or_above
def gallery_item_featured(item_id):
    item = Gallery.query.get_or_404(item_id)
    is_featured = request.form.get("featured") == "1"
    set_featured(item_id, is_featured)
    flash("Status unggulan diperbarui.", "success")
    if item.activity_id:
        return redirect(url_for("admin.activity_gallery", activity_id=item.activity_id))
    return redirect(url_for("admin.dashboard"))


# ---- Activity log (Super Admin only) ----
@admin_bp.route("/activity-log", methods=["GET"])
@login_required
@super_admin_required
def activity_log():
    logs = get_recent_logs(limit=100)
    return render_template("admin/activity_log.html", logs=logs)


# ---- Backup (Super Admin only) ----
@admin_bp.route("/backup", methods=["GET"])
@login_required
@super_admin_required
def backup():
    db_uri = current_app.config["SQLALCHEMY_DATABASE_URI"]
    if not db_uri.startswith("sqlite:///"):
        flash("Cadangan hanya didukung untuk basis data SQLite.", "warning")
        return redirect(url_for("admin.dashboard"))
    path = db_uri.replace("sqlite:///", "")
    if not os.path.isfile(path):
        flash("Berkas basis data tidak ditemukan.", "error")
        return redirect(url_for("admin.dashboard"))
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    download_name = f"goslides-backup-{timestamp}.db"
    return send_file(path, as_attachment=True, download_name=download_name)


# ---- Sponsor ----
@admin_bp.route("/sponsor", methods=["GET", "POST"])
@login_required
@super_admin_required
def sponsor_list():
    years = get_all_years()
    active_year = next((y for y in years if y.active), None)
    sponsors = SponsorService.get_all(year_id=active_year.id) if active_year else []
    form = SponsorForm()
    if form.validate_on_submit():
        logo_file = form.logo.data
        logo_filename = None
        if logo_file:
            logo_filename = f"sponsor_{datetime.utcnow().timestamp()}_{logo_file.filename}"
            sponsor_upload_folder = current_app.config.get("SPONSOR_UPLOAD_FOLDER")
            os.makedirs(sponsor_upload_folder, exist_ok=True)
            logo_path = os.path.join(sponsor_upload_folder, logo_filename)
            logo_file.save(logo_path)
        SponsorService.add(form.name.data, logo_filename, active_year.id if active_year else None, form.link.data)
        flash("Sponsor berhasil ditambah.", "success")
        return redirect(url_for("admin.sponsor_list"))
    return render_template("admin/sponsor_list.html", sponsors=sponsors, form=form, active_year=active_year)


@admin_bp.route('/sponsor/<int:sponsor_id>/edit', methods=['GET', 'POST'])
@login_required
@super_admin_required
def sponsor_edit(sponsor_id):
    from app.services.year_service import get_active_year
    sponsor = SponsorService.get_all()[0].__class__.query.get_or_404(sponsor_id)
    form = SponsorForm(obj=sponsor)
    active_year = get_active_year()
    if form.validate_on_submit():
        logo_file = form.logo.data
        logo_filename = sponsor.logo
        if logo_file:
            logo_filename = f"sponsor_{datetime.utcnow().timestamp()}_{logo_file.filename}"
            logo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], logo_filename)
            logo_file.save(logo_path)
        SponsorService.update(sponsor_id, form.name.data, logo_filename, form.link.data, active_year.id if active_year else None)
        flash('Sponsor berhasil diupdate.', 'success')
        return redirect(url_for('admin.sponsor_list'))
    return render_template('admin/sponsor_edit.html', form=form, sponsor=sponsor)


@admin_bp.route('/sponsor/<int:sponsor_id>/delete', methods=['POST'])
@login_required
@super_admin_required
def sponsor_delete(sponsor_id):
    SponsorService.delete(sponsor_id)
    flash('Sponsor dihapus.', 'success')
    return redirect(url_for('admin.sponsor_list'))
