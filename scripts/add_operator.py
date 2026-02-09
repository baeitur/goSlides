#!/usr/bin/env python3
"""
Buat akun Operator baru.
Jalankan dari folder proyek: python scripts/add_operator.py
Atau dengan email/kata sandi: python scripts/add_operator.py email@contoh.id katasandi123 "Nama Operator"
"""
import sys
import os

# Agar app bisa di-import dari root proyek
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from werkzeug.security import generate_password_hash
from app import create_app
from app.models import db, User
from app.models import ROLE_OPERATOR


def main():
    app = create_app()
    with app.app_context():
        email = sys.argv[1] if len(sys.argv) > 1 else "operator@goslides.local"
        password = sys.argv[2] if len(sys.argv) > 2 else "operator123"
        name = sys.argv[3] if len(sys.argv) > 3 else "Operator"

        if User.query.filter_by(email=email).first():
            print(f"Email {email} sudah terdaftar. Gunakan email lain atau ubah di database.")
            return 1

        user = User(
            name=name,
            email=email,
            password=generate_password_hash(password, method="scrypt"),
            role=ROLE_OPERATOR,
        )
        db.session.add(user)
        db.session.commit()
        print(f"Akun Operator berhasil dibuat.")
        print(f"  Email: {email}")
        print(f"  Kata sandi: {password}")
        print(f"  Masuk ke /admin/login dengan data di atas.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
