#!/usr/bin/env python3
"""
Update kolom email di tabel registrants agar nullable (opsional).
Jalankan dari folder proyek: python scripts/update_registrant_email_nullable.py
"""
import sys
import os

# Agar app bisa di-import dari root proyek
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import db
from sqlalchemy import text


def main():
    app = create_app()
    with app.app_context():
        try:
            # Untuk SQLite, kita perlu recreate table karena ALTER COLUMN terbatas
            # Langkah 1: Rename table lama
            db.session.execute(text("ALTER TABLE registrants RENAME TO registrants_old"))

            # Langkah 2: Create table baru dengan email nullable
            db.session.execute(text("""
                CREATE TABLE registrants (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    activity_id INTEGER NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    school VARCHAR(255) NOT NULL,
                    phone VARCHAR(64),
                    email VARCHAR(255),
                    file VARCHAR(255),
                    status VARCHAR(32) NOT NULL DEFAULT 'pending',
                    check_in_code VARCHAR(64) UNIQUE,
                    attended_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (activity_id) REFERENCES activities(id) ON DELETE CASCADE
                )
            """))

            # Langkah 3: Copy data dari table lama ke table baru
            db.session.execute(text("""
                INSERT INTO registrants (id, activity_id, name, school, phone, email, file, status, check_in_code, attended_at, created_at)
                SELECT id, activity_id, name, school, phone, email, file, status, check_in_code, attended_at, created_at
                FROM registrants_old
            """))

            # Langkah 4: Drop table lama
            db.session.execute(text("DROP TABLE registrants_old"))

            # Commit perubahan
            db.session.commit()

            print("Kolom email di tabel registrants berhasil diubah menjadi nullable (opsional).")
            return 0

        except Exception as e:
            db.session.rollback()
            print(f"Error updating database: {e}")
            return 1


if __name__ == "__main__":
    sys.exit(main())