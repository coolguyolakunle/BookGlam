"""
Run this once to create the first admin account.
Usage: python seed_admin.py
"""

import os
from dotenv import load_dotenv

from app import create_app
from app.extensions import db, bcrypt
from app.models import User

# Load .env variables
load_dotenv()

app = create_app()

with app.app_context():

    ADMIN_NAME = os.getenv("ADMIN_NAME")
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

    if not ADMIN_EMAIL or not ADMIN_PASSWORD:
        print("❌ Missing admin credentials in .env")
        exit()

    # Check if admin exists
    existing = User.query.filter_by(email=ADMIN_EMAIL).first()

    if existing:
        print("✅ Admin already exists.")
    else:
        hashed = bcrypt.generate_password_hash(
            ADMIN_PASSWORD
        ).decode("utf-8")

        admin = User(
            full_name=ADMIN_NAME,
            email=ADMIN_EMAIL,
            password_hash=hashed,
            role="admin",
        )

        db.session.add(admin)
        db.session.commit()

        print("✓ Admin created.")
        print(f"  Email:    {ADMIN_EMAIL}")
        print("  Password: [Hidden]")
        print("  Please change the password after first login.")