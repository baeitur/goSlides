# Go Slides – Flask routes

## Public

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Landing (hero, countdown, featured photos, event cards) |
| GET | `/events` | Event list (active year) |
| GET | `/about` | About page (admin-editable) |
| GET, POST | `/contact` | Contact (WhatsApp button + message form) |
| GET | `/competition/<id>` | Competition detail (countdown, gallery preview) |
| GET | `/competition/<id>/guideline` | Download guideline PDF |
| GET, POST | `/competition/<id>/register` | Online registration form |
| GET | `/competition/<id>/gallery` | Gallery for activity |
| GET | `/uploads/gallery/<filename>` | Serve gallery image |

## Admin (prefix `/admin`)

| Method | Path | Description |
|--------|------|-------------|
| GET, POST | `/admin/login` | Login |
| GET | `/admin/logout` | Logout |
| GET | `/admin/` | Dashboard |
| GET, POST | `/admin/years` | List years, add year |
| POST | `/admin/years/<id>/activate` | Set active year |
| GET, POST | `/admin/years/<id>/edit` | Edit year |
| POST | `/admin/years/<id>/delete` | Delete year |
| GET | `/admin/years/<id>/activities` | List activities for year |
| GET, POST | `/admin/years/<id>/activities/new` | New activity |
| GET, POST | `/admin/activities/<id>/edit` | Edit activity |
| POST | `/admin/activities/<id>/delete` | Delete activity |
| GET | `/admin/activities/<id>/registrants` | List registrants |
| GET, POST | `/admin/activities/<id>/gallery` | Gallery: upload images, feature, delete |
| POST | `/admin/registrants/<id>/verify` | Verify registrant |
| POST | `/admin/registrants/<id>/status` | Set status (pending/verified) |
| GET, POST | `/admin/about` | Edit About page content |
| GET | `/admin/contact-messages` | View contact form submissions |
| GET | `/admin/backup` | Download database backup (SQLite) |
| POST | `/admin/gallery/<id>/delete` | Delete gallery image |
| POST | `/admin/gallery/<id>/featured` | Toggle featured on homepage |
