# Phase 3 – Professional: Step-by-Step Implementation Guide

This guide documents the implementation of **role-based access**, **dashboard statistics (Chart.js)**, **QR code attendance**, **PDF export**, **activity log**, and **WhatsApp notifications** in Go Slides.

---

## 1. Role-based access (Super Admin / Operator)

### 1.1 Roles

- **super_admin**: Full access including backup, activity log, and delete year/activity.
- **operator**: Dashboard, years (add/edit, set active), activities (CRUD except delete), registrants (view/verify/attend), gallery, about, contact messages. Cannot: backup DB, view activity log, delete year/activity.

### 1.2 Model and constants

**File: `app/models/__init__.py`**

```python
ROLE_SUPER_ADMIN = "super_admin"
ROLE_OPERATOR = "operator"

class User(UserMixin, db.Model):
    # ...
    role = db.Column(db.String(32), nullable=False, default=ROLE_OPERATOR)

    @property
    def is_super_admin(self):
        return self.role == ROLE_SUPER_ADMIN
```

Default admin created in `ensure_admin_exists()` is given `role=ROLE_SUPER_ADMIN`.

### 1.3 Permission decorators

**File: `app/utils/decorators.py`**

```python
from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("admin.login"))
            if current_user.role not in allowed_roles:
                flash("You do not have permission to access this page.", "error")
                return redirect(url_for("admin.dashboard"))
            return f(*args, **kwargs)
        return wrapped
    return decorator

def super_admin_required(f):
    return role_required(ROLE_SUPER_ADMIN)(f)

def operator_or_above(f):
    return role_required(ROLE_SUPER_ADMIN, ROLE_OPERATOR)(f)
```

### 1.4 Usage on routes

- Use `@operator_or_above` for all admin routes that both roles may access.
- Use `@super_admin_required` for backup, activity log, and delete year/activity.

```python
@admin_bp.route("/backup", methods=["GET"])
@login_required
@super_admin_required
def backup():
    # ...
```

In templates, show Super-Admin-only links with:

```jinja2
{% if current_user.is_super_admin %}
  <a href="{{ url_for('admin.activity_log') }}">Activity log</a>
  <a href="{{ url_for('admin.backup') }}">Backup database</a>
{% endif %}
```

---

## 2. Dashboard statistics with Chart.js

### 2.1 Stats service

**File: `app/services/dashboard_service.py`**

- Counts: total activities, total registrants, verified, attended (for active year).
- Per-activity registrant counts (bar chart).
- Registrations per day for last 14 days (line chart).

Example structure:

```python
def get_dashboard_stats(active_year=None):
    # ... compute activity_ids, total_registrants, verified_count, attended_count
    # ... build activity_labels, activity_counts
    # ... build day_labels, regs_per_day (from Registrant.created_at grouped by date)
    return {
        "total_activities": len(activities),
        "total_registrants": total_registrants,
        "verified_count": verified,
        "attended_count": attended,
        "activity_labels": activity_labels,
        "activity_counts": activity_counts,
        "day_labels": day_labels,
        "regs_per_day": regs_per_day,
    }
```

### 2.2 Dashboard view

Pass `stats` from `get_dashboard_stats(active_year)` into the dashboard template.

### 2.3 Chart.js in template

**File: `app/templates/admin/dashboard.html`**

```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<canvas id="chartActivities" height="200"></canvas>
<canvas id="chartDays" height="200"></canvas>
<script>
(function(){
  var stats = {{ stats | tojson | safe }};
  new Chart(document.getElementById('chartActivities'), {
    type: 'bar',
    data: {
      labels: stats.activity_labels,
      datasets: [{ label: 'Registrants', data: stats.activity_counts, backgroundColor: '#1BA3A8' }]
    },
    options: { responsive: true, scales: { y: { beginAtZero: true } } }
  });
  new Chart(document.getElementById('chartDays'), {
    type: 'line',
    data: {
      labels: stats.day_labels.map(d => d.slice(5)),
      datasets: [{ label: 'Registrations', data: stats.regs_per_day, borderColor: '#F4B23C', fill: true }]
    },
    options: { responsive: true, scales: { y: { beginAtZero: true } } }
  });
})();
</script>
```

---

## 3. QR code attendance

### 3.1 Data model

**Registrant** gets:

- `check_in_code`: unique string (e.g. `secrets.token_urlsafe(12)`), generated on create; backfill for old rows in `ensure_check_in_code(reg)`.
- `attended_at`: datetime, set when check-in is recorded.

### 3.2 Check-in URL

Public URL format: `/checkin/<code>`.

- **GET** `/checkin/<code>`: find registrant by `check_in_code`, set `attended_at = now()` if not already set, render success/error page.

```python
# app/routes/public.py
@public_bp.route("/checkin/<code>")
def checkin(code):
    reg = get_registrant_by_check_in_code(code)
    if not reg:
        return render_template("public/checkin_result.html", success=False, registrant=None)
    already = reg.attended_at
    if not already:
        mark_attended_by_code(code)
    return render_template("public/checkin_result.html", success=True, registrant=reg, already_attended=already)
```

### 3.3 Admin: QR image and “Mark attended”

- **GET** `/admin/registrants/<id>/qr`: generate QR image (e.g. with `qrcode` library) encoding full URL `request.url_root + "/checkin/" + reg.check_in_code`, return PNG.
- Registrants list: show small QR thumbnail linking to that URL; add “Mark attended” button that POSTs to `/admin/registrants/<id>/attend` and sets `attended_at` server-side.

Example QR generation:

```python
import qrcode
import io

def registrant_qr(registrant_id):
    reg = Registrant.query.get_or_404(registrant_id)
    ensure_check_in_code(reg)
    checkin_url = request.url_root.rstrip("/") + url_for("public.checkin", code=reg.check_in_code, _external=False)
    img = qrcode.make(checkin_url)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return send_file(buffer, mimetype="image/png")
```

---

## 4. PDF export (participant list)

### 4.1 Dependencies

```
reportlab>=4.0.0
```

### 4.2 Export service

**File: `app/services/pdf_export_service.py`**

- Build a PDF with ReportLab: title “Go Slides – Participant List”, activity title, table with columns: #, Name, School, Email, Phone, Status, Attended.
- Return a `BytesIO` buffer.

Example structure:

```python
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle

def export_registrants_pdf(activity, registrants):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, ...)
    data = [["#", "Name", "School", "Email", "Phone", "Status", "Attended"]]
    for i, r in enumerate(registrants, 1):
        data.append([str(i), r.name, r.school, r.email, r.phone or "", r.status, "Yes" if r.attended_at else "No"])
    t = Table(data, ...)
    t.setStyle(TableStyle([...]))
    doc.build([Paragraph(...), t])
    buffer.seek(0)
    return buffer
```

### 4.3 Route

```python
@admin_bp.route("/activities/<int:activity_id>/registrants/export-pdf", methods=["GET"])
@login_required
@operator_or_above
def registrants_export_pdf(activity_id):
    activity = get_activity_or_404(activity_id)
    registrants = get_registrants_for_activity(activity_id)
    buffer = export_registrants_pdf(activity, registrants)
    return send_file(buffer, mimetype="application/pdf", as_attachment=True, download_name="participants-....pdf")
```

---

## 5. Activity log

### 5.1 Model

**File: `app/models/__init__.py`**

```python
class ActivityLog(db.Model):
    __tablename__ = "activity_log"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = db.Column(db.String(64), nullable=False)   # create, update, delete, login, logout, verify, attend
    entity_type = db.Column(db.String(64), nullable=True)  # year, activity, registrant, about
    entity_id = db.Column(db.String(64), nullable=True)
    details = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    user = db.relationship("User", backref="activity_logs")
```

### 5.2 Logging helper

**File: `app/services/activity_log_service.py`**

```python
def log_action(action, entity_type=None, entity_id=None, details=None):
    user_id = current_user.id if current_user.is_authenticated else None
    entry = ActivityLog(user_id=user_id, action=action, entity_type=entity_type, entity_id=str(entity_id) if entity_id else None, details=details)
    db.session.add(entry)
    db.session.commit()
```

Call after important actions, e.g.:

- Login / logout: `log_action("login", details=user.email)`, `log_action("logout")`
- Year: `log_action("create", entity_type="year", details=name)`, `log_action("update", entity_type="year", entity_id=year_id)`, `log_action("delete", entity_type="year", entity_id=year_id)`
- Activity: same pattern for create/update/delete.
- Registrant: `log_action("verify", entity_type="registrant", entity_id=id)`, `log_action("attend", entity_type="registrant", entity_id=id)`
- About: `log_action("update", entity_type="about")`

### 5.3 View (Super Admin only)

- Route: `GET /admin/activity-log`, protected with `@super_admin_required`.
- Query: `get_recent_logs(limit=100)` and render a table: time, user email, action, entity_type, entity_id, details.

---

## 6. WhatsApp notification integration

### 6.1 Service interface

**File: `app/services/whatsapp_service.py`**

- `send_whatsapp_message(phone, message)`:
  - Normalize `phone` (digits only).
  - If **Twilio** credentials are set (`TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_WHATSAPP_FROM`): POST to Twilio Messages API with `From=whatsapp:...`, `To=whatsapp:...`, `Body=message`.
  - Else if **generic webhook** is set (`WHATSAPP_WEBHOOK_URL`): POST JSON `{"phone": phone, "message": message}`.
  - Return `True` on success, `False` on failure (or when no provider is configured and you choose to skip sending).

- `notify_registration_confirmation(registrant, activity)`: if `registrant.phone` is present, build a short message (e.g. “Hi {name}! You have registered for {activity.title}…”) and call `send_whatsapp_message(registrant.phone, message)`.

### 6.2 When to send

Call `notify_registration_confirmation(reg, activity)` right after creating a registrant in the public registration flow.

### 6.3 Environment variables

- **Twilio**: `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_WHATSAPP_FROM` (e.g. `whatsapp:+14155238886`).
- **Webhook**: `WHATSAPP_WEBHOOK_URL` (POST endpoint that accepts `phone` and `message`).

---

## 7. Dependencies and schema summary

### 7.1 New Python packages

```
reportlab>=4.0.0
qrcode[pil]>=7.0
requests>=2.28.0
```

### 7.2 Schema changes (Phase 3)

- **users**: `role` remains; use values `super_admin`, `operator`.
- **registrants**: add `check_in_code VARCHAR(64) UNIQUE`, `attended_at TIMESTAMP`.
- **activity_log**: new table (id, user_id, action, entity_type, entity_id, details, created_at).

---

## 8. Quick reference: new routes

| Method | Path | Description | Role |
|--------|------|-------------|------|
| GET | `/checkin/<code>` | Public QR check-in | — |
| GET | `/admin/` | Dashboard with stats & Chart.js | Operator+ |
| GET | `/admin/activity-log` | Activity log list | Super Admin |
| GET | `/admin/activities/<id>/registrants/export-pdf` | Export participants PDF | Operator+ |
| GET | `/admin/registrants/<id>/qr` | QR code image | Operator+ |
| POST | `/admin/registrants/<id>/attend` | Mark attended | Operator+ |

All other existing admin routes are restricted with `@operator_or_above`; backup, activity log, and delete year/activity use `@super_admin_required`.
