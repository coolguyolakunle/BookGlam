from flask import Flask
from app.extensions import db, login_manager, bcrypt, migrate, socketio
import os
from dotenv import load_dotenv
import cloudinary


def create_app(config_name='default'):
    load_dotenv()

    app = Flask(__name__)

    # ─── CORE CONFIG ───
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    if not app.config['SECRET_KEY']:
        raise ValueError("SECRET_KEY is missing in .env")

    database_url = os.getenv('DATABASE_URL', 'sqlite:///bookglam.db')
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max upload

    # ─── CLOUDINARY CONFIG (ONLY ONCE) ───
    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
        api_key=os.getenv("CLOUDINARY_API_KEY"),
        api_secret=os.getenv("CLOUDINARY_API_SECRET"),
        secure=True
    )

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app, cors_allowed_origins="*", async_mode="threading")

    # Register blueprints
    from app.main import main as main_bp
    app.register_blueprint(main_bp)

    from app.auth import auth as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.client import client as client_bp
    app.register_blueprint(client_bp, url_prefix='/client')

    from app.provider import provider as provider_bp
    app.register_blueprint(provider_bp, url_prefix='/provider')

    from app.admin import admin as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # Register Socket.IO event handlers.
    from app import socket_events  # noqa: F401

    # Create tables
    with app.app_context():
        db.create_all()
        _seed_categories(db)

    return app


def _seed_categories(db):
    from app.models import ServiceCategory, Service
    if ServiceCategory.query.count() == 0:
        categories = [
            {'name': 'Hair', 'icon': 'scissors', 'description': 'Haircuts, styling, coloring and more'},
            {'name': 'Barbing', 'icon': 'razor', 'description': 'Fades, lineups, beard trims'},
            {'name': 'Makeup', 'icon': 'sparkles', 'description': 'Full glam, natural looks, bridal'},
            {'name': 'Nails', 'icon': 'hand', 'description': 'Manicure, pedicure, nail art'},
        ]
        for cat_data in categories:
            cat = ServiceCategory(**cat_data)
            db.session.add(cat)
        db.session.commit()

        services = [
            # Hair
            {'category_id': 1, 'name': 'Wash & Style', 'base_price_basic': 3000, 'base_price_standard': 6000, 'base_price_premium': 12000, 'duration_minutes': 60},
            {'category_id': 1, 'name': 'Hair Braiding', 'base_price_basic': 5000, 'base_price_standard': 10000, 'base_price_premium': 20000, 'duration_minutes': 120},
            {'category_id': 1, 'name': 'Hair Coloring', 'base_price_basic': 8000, 'base_price_standard': 15000, 'base_price_premium': 30000, 'duration_minutes': 90},
            # Barbing
            {'category_id': 2, 'name': 'Haircut & Fade', 'base_price_basic': 1500, 'base_price_standard': 3000, 'base_price_premium': 6000, 'duration_minutes': 30},
            {'category_id': 2, 'name': 'Beard Trim & Shape', 'base_price_basic': 1000, 'base_price_standard': 2000, 'base_price_premium': 4000, 'duration_minutes': 20},
            # Makeup
            {'category_id': 3, 'name': 'Natural Makeup', 'base_price_basic': 5000, 'base_price_standard': 10000, 'base_price_premium': 20000, 'duration_minutes': 60},
            {'category_id': 3, 'name': 'Bridal Makeup', 'base_price_basic': 15000, 'base_price_standard': 30000, 'base_price_premium': 60000, 'duration_minutes': 120},
            # Nails
            {'category_id': 4, 'name': 'Manicure', 'base_price_basic': 2000, 'base_price_standard': 4000, 'base_price_premium': 8000, 'duration_minutes': 45},
            {'category_id': 4, 'name': 'Pedicure', 'base_price_basic': 2500, 'base_price_standard': 5000, 'base_price_premium': 10000, 'duration_minutes': 45},
            {'category_id': 4, 'name': 'Nail Art', 'base_price_basic': 3000, 'base_price_standard': 6000, 'base_price_premium': 15000, 'duration_minutes': 60},
        ]
        for svc_data in services:
            svc = Service(**svc_data)
            db.session.add(svc)
        db.session.commit()
