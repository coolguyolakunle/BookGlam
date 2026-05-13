from datetime import datetime
from flask_login import UserMixin
from app.extensions import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='client')  # client | provider | admin
    avatar = db.Column(db.String(256), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    client_bookings = db.relationship('Booking', foreign_keys='Booking.client_id', backref='client', lazy=True)
    provider_profile = db.relationship('ProviderProfile', backref='user', uselist=False, lazy=True)

    def __repr__(self):
        return f'<User {self.email} ({self.role})>'


class ProviderProfile(db.Model):
    __tablename__ = 'provider_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    specialties = db.Column(db.String(256), nullable=True)   # comma-separated
    location = db.Column(db.String(256), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    is_online = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)
    tier = db.Column(db.String(20), default='standard')  # basic | standard | premium
    years_experience = db.Column(db.Integer, nullable=True)
    rating = db.Column(db.Float, default=0.0)
    total_reviews = db.Column(db.Integer, default=0)
    earnings_balance = db.Column(db.Float, default=0.0)
    id_document = db.Column(db.String(256), nullable=True)
    portfolio_images = db.Column(db.Text, nullable=True)  # JSON array of image paths
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    bookings = db.relationship('Booking', foreign_keys='Booking.provider_id', backref='provider', lazy=True)
    portfolio_items = db.relationship('ProviderPortfolio', backref='provider', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<ProviderProfile user_id={self.user_id}>'


class ProviderPortfolio(db.Model):
    __tablename__ = 'provider_portfolios'
    id = db.Column(db.Integer, primary_key=True)
    provider_id = db.Column(db.Integer, db.ForeignKey('provider_profiles.id'), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    caption = db.Column(db.String(160), nullable=True)
    service_tag = db.Column(db.String(80), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ProviderPortfolio provider_id={self.provider_id}>'


class ServiceCategory(db.Model):
    __tablename__ = 'service_categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    icon = db.Column(db.String(80), nullable=True)
    description = db.Column(db.Text, nullable=True)
    services = db.relationship('Service', backref='category', lazy=True)

    def __repr__(self):
        return f'<ServiceCategory {self.name}>'


class Service(db.Model):
    __tablename__ = 'services'
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('service_categories.id'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    base_price_basic = db.Column(db.Float, nullable=False, default=0.0)
    base_price_standard = db.Column(db.Float, nullable=False, default=0.0)
    base_price_premium = db.Column(db.Float, nullable=False, default=0.0)
    duration_minutes = db.Column(db.Integer, default=60)
    image = db.Column(db.String(256), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    bookings = db.relationship('Booking', backref='service', lazy=True)

    def __repr__(self):
        return f'<Service {self.name}>'


class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    provider_id = db.Column(db.Integer, db.ForeignKey('provider_profiles.id'), nullable=True)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    booking_type = db.Column(db.String(20), default='home')  # home | shop
    service_tier = db.Column(db.String(20), default='standard')  # basic | standard | premium
    status = db.Column(db.String(30), default='pending')
    # pending | accepted | on_the_way | in_progress | completed | cancelled | disputed
    scheduled_at = db.Column(db.DateTime, nullable=True)
    is_instant = db.Column(db.Boolean, default=False)
    address = db.Column(db.String(300), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    price = db.Column(db.Float, nullable=True)
    payment_method = db.Column(db.String(30), default='cash')  # cash | transfer | wallet | card
    payment_status = db.Column(db.String(20), default='unpaid')  # unpaid | paid
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    review = db.relationship('Review', backref='booking', uselist=False, lazy=True)

    def __repr__(self):
        return f'<Booking #{self.id} status={self.status}>'


class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1–5
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Review booking_id={self.booking_id} rating={self.rating}>'


class Withdrawal(db.Model):
    __tablename__ = 'withdrawals'
    id = db.Column(db.Integer, primary_key=True)
    provider_id = db.Column(db.Integer, db.ForeignKey('provider_profiles.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending | approved | rejected
    bank_name = db.Column(db.String(100), nullable=True)
    account_number = db.Column(db.String(20), nullable=True)
    account_name = db.Column(db.String(120), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime, nullable=True)

    provider = db.relationship('ProviderProfile', backref='withdrawals', lazy=True)

    def __repr__(self):
        return f'<Withdrawal provider_id={self.provider_id} amount={self.amount}>'

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    body = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages', lazy=True)
    booking = db.relationship('Booking', backref='messages', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'booking_id': self.booking_id,
            'sender_id': self.sender_id,
            'sender_name': self.sender.full_name,
            'sender_avatar': self.sender.avatar,
            'body': self.body,
            'is_read': self.is_read,
            'created_at': self.created_at.strftime('%I:%M %p'),
        }

    def __repr__(self):
        return f'<Message booking_id={self.booking_id} sender_id={self.sender_id}>'


class LocationUpdate(db.Model):
    __tablename__ = 'location_updates'
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    booking = db.relationship('Booking', backref='location_updates', lazy=True)
    user = db.relationship('User', foreign_keys=[user_id], lazy=True)

    def __repr__(self):
        return f'<LocationUpdate booking_id={self.booking_id} user_id={self.user_id}>'
