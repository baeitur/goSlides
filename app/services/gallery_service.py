"""Gallery images per activity/year."""
import os
import uuid
from flask import current_app
from app.models import db, Gallery


def get_gallery_for_activity(activity_id):
    return Gallery.query.filter_by(activity_id=activity_id).order_by(Gallery.created_at.desc()).all()


def get_featured_photos(limit=8):
    return Gallery.query.filter_by(is_featured=True).order_by(Gallery.created_at.desc()).limit(limit).all()


def get_recent_gallery_photos(limit=8):
    """Latest gallery images from any activity (for homepage when no featured)."""
    return Gallery.query.order_by(Gallery.created_at.desc()).limit(limit).all()


def save_gallery_image(file_storage):
    """Save uploaded image; return stored filename or None."""
    if not file_storage or not file_storage.filename:
        return None
    ext = file_storage.filename.rsplit(".", 1)[-1].lower()
    if ext not in current_app.config.get("ALLOWED_IMAGE_EXTENSIONS", {"png", "jpg", "jpeg", "gif", "webp"}):
        return None
    filename = f"{uuid.uuid4().hex}.{ext}"
    folder = current_app.config["GALLERY_UPLOAD_FOLDER"]
    path = os.path.join(str(folder), filename)
    file_storage.save(path)
    return filename


def add_gallery_item(year_id, activity_id, file_filename, caption=None, is_featured=False):
    item = Gallery(
        year_id=year_id,
        activity_id=activity_id,
        file=file_filename,
        caption=caption or "",
        is_featured=bool(is_featured),
    )
    db.session.add(item)
    db.session.commit()
    return item


def delete_gallery_item(item_id):
    item = Gallery.query.get_or_404(item_id)
    folder = current_app.config["GALLERY_UPLOAD_FOLDER"]
    path = os.path.join(str(folder), item.file)
    if os.path.isfile(path):
        os.remove(path)
    db.session.delete(item)
    db.session.commit()


def set_featured(item_id, is_featured):
    item = Gallery.query.get_or_404(item_id)
    item.is_featured = bool(is_featured)
    db.session.commit()
    return item
