# Go Slides

School event and competition web platform — **From Event to Achievement**.

Built with **Flask**, **SQLite**, and **Tailwind CSS**.

## Branding

- **Primary:** Teal `#1BA3A8`
- **Accent:** Gold `#F4B23C`
- **Background:** Light gray `#F5F7FA`
- **Fonts:** Poppins (headings), Inter (body)

## Setup

```bash
cd go_slides
python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

## Run

```bash
python run.py
```

Open http://127.0.0.1:5000

## Login

### Super Admin (akun default)
- **Email:** admin@goslides.local (atau admin@goslides.com sesuai konfigurasi)
- **Kata sandi:** admin123  
- Akses penuh: backup, log aktivitas, hapus tahun/acara.

### Operator
Tidak ada akun operator bawaan. Untuk **login sebagai operator**:

1. Buat akun operator dengan skrip (dari folder proyek):
   ```bash
   python scripts/add_operator.py
   ```
   Ini membuat operator dengan email `operator@goslides.local` dan kata sandi `operator123`.

2. Atau dengan email dan kata sandi sendiri:
   ```bash
   python scripts/add_operator.py email@sekolah.id katasandi123 "Nama Operator"
   ```

3. Buka **/admin/login** dan masuk dengan email serta kata sandi operator tersebut.

Operator bisa mengelola tahun, acara, pendaftar, galeri, tentang, dan pesan kontak; tidak bisa backup basis data, log aktivitas, atau menghapus tahun/acara.

## Optional: WhatsApp button on Contact page

Set env var to show “Chat on WhatsApp” (use digits only, e.g. country code + number):

```bash
export WHATSAPP_NUMBER=6281234567890
```

## Project structure

```
app/
  routes/       # public + admin blueprints
  models/       # User, Year, Activity, Registrant, Gallery, About, ContactMessage
  services/     # auth, years, activities, registrants, about, contact, gallery
  templates/    # Jinja + Tailwind
  static/
  uploads/      # guidelines (PDFs), gallery (images)
schema.sql      # SQL schema (reference)
docs/
  ERD.md        # Entity relationship diagram
  ROUTES.md     # Route list
```

## Features

- **Public:** Landing (countdown, featured photos), event list, About, Contact (form + WhatsApp), competition detail, PDF guidelines, online registration, per-activity gallery
- **Admin:** Login, event years, activities, guideline PDF, quota/auto-close, registrants, **edit About**, **view contact messages**, **upload gallery images** (per activity, feature on homepage), **backup database**
