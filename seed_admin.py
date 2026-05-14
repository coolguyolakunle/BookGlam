"""
Create or repair the first admin account.
Usage: python seed_admin.py

Required environment variables:
- ADMIN_EMAIL
- ADMIN_PASSWORD

Optional:
- ADMIN_NAME
- RESET_ADMIN_PASSWORD=true
"""

import os

from dotenv import load_dotenv

from app import create_app
from app.extensions import bcrypt, db
from app.models import User


load_dotenv()

app = create_app()

with app.app_context():
    admin_name = os.getenv("ADMIN_NAME", "BookGlam Admin").strip()
    admin_email = os.getenv("ADMIN_EMAIL", "").strip().lower()
    admin_password = os.getenv("ADMIN_PASSWORD", "")
    reset_password = os.getenv("RESET_ADMIN_PASSWORD", "").strip().lower() in ("1", "true", "yes")

    if not admin_email or not admin_password:
        print("Missing admin credentials. Set ADMIN_EMAIL and ADMIN_PASSWORD.")
        raise SystemExit(1)

    existing = User.query.filter_by(email=admin_email).first()

    if existing:
        existing.role = "admin"
        existing.full_name = admin_name or existing.full_name
        existing.is_active = True
        if reset_password:
            existing.password_hash = bcrypt.generate_password_hash(admin_password).decode("utf-8")
            print("Admin already exists. Password reset.")
        else:
            print("Admin already exists. Set RESET_ADMIN_PASSWORD=true to reset the password.")
        db.session.commit()
    else:
        admin = User(
            full_name=admin_name,
            email=admin_email,
            password_hash=bcrypt.generate_password_hash(admin_password).decode("utf-8"),
            role="admin",
            is_active=True,
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin created.")

    print(f"Email: {admin_email}")
