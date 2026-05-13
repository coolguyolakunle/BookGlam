from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.admin import admin
from app.extensions import db, bcrypt
from app.models import User, ProviderProfile, Booking, Withdrawal, ServiceCategory, Service
from functools import wraps
from sqlalchemy import func


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.role != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated


@admin.route('/dashboard')
@login_required
@admin_required
def dashboard():
    # Total revenue = sum of all completed booking prices
    total_earnings_row = db.session.query(func.sum(Booking.price)).filter_by(status='completed').scalar()
    total_earnings = total_earnings_row or 0.0
    # Platform commission (15% of total earnings)
    platform_commission = total_earnings * 0.15
    # Total withdrawn (approved withdrawals)
    total_withdrawn_row = db.session.query(func.sum(Withdrawal.amount)).filter_by(status='approved').scalar()
    total_withdrawn = total_withdrawn_row or 0.0

    stats = {
        'total_users': User.query.count(),
        'total_providers': ProviderProfile.query.count(),
        'pending_providers': ProviderProfile.query.filter_by(is_verified=False).count(),
        'total_bookings': Booking.query.count(),
        'pending_bookings': Booking.query.filter_by(status='pending').count(),
        'completed_bookings': Booking.query.filter_by(status='completed').count(),
        'pending_withdrawals': Withdrawal.query.filter_by(status='pending').count(),
        'total_earnings': total_earnings,
        'platform_commission': platform_commission,
        'total_withdrawn': total_withdrawn,
    }
    recent_bookings = Booking.query.order_by(Booking.created_at.desc()).limit(10).all()
    return render_template('admin/dashboard.html', stats=stats, recent_bookings=recent_bookings)


@admin.route('/change-password', methods=['GET', 'POST'])
@login_required
@admin_required
def change_password():
    if request.method == 'POST':
        current_pw = request.form.get('current_password', '')
        new_pw = request.form.get('new_password', '')
        confirm_pw = request.form.get('confirm_password', '')

        if not bcrypt.check_password_hash(current_user.password_hash, current_pw):
            flash('Current password is incorrect.', 'danger')
            return render_template('admin/change_password.html')
        if len(new_pw) < 8:
            flash('New password must be at least 8 characters.', 'danger')
            return render_template('admin/change_password.html')
        if new_pw != confirm_pw:
            flash('New passwords do not match.', 'danger')
            return render_template('admin/change_password.html')

        current_user.password_hash = bcrypt.generate_password_hash(new_pw).decode('utf-8')
        db.session.commit()
        flash('Password updated successfully.', 'success')
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/change_password.html')


@admin.route('/providers')
@login_required
@admin_required
def providers():
    all_providers = ProviderProfile.query.all()
    return render_template('admin/providers.html', providers=all_providers)


@admin.route('/providers/<int:provider_id>/verify', methods=['POST'])
@login_required
@admin_required
def verify_provider(provider_id):
    profile = ProviderProfile.query.get_or_404(provider_id)
    profile.is_verified = not profile.is_verified
    db.session.commit()
    status = 'verified' if profile.is_verified else 'unverified'
    flash(f'Provider has been {status}.', 'success')
    return redirect(url_for('admin.providers'))


@admin.route('/users')
@login_required
@admin_required
def users():
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=all_users)


@admin.route('/users/<int:user_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('Cannot deactivate your own account.', 'warning')
        return redirect(url_for('admin.users'))
    user.is_active = not user.is_active
    db.session.commit()
    flash(f'User {"activated" if user.is_active else "deactivated"}.', 'success')
    return redirect(url_for('admin.users'))


@admin.route('/bookings')
@login_required
@admin_required
def bookings():
    status_filter = request.args.get('status', 'all')
    query = Booking.query
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    all_bookings = query.order_by(Booking.created_at.desc()).all()
    return render_template('admin/bookings.html', bookings=all_bookings, status_filter=status_filter)


@admin.route('/bookings/<int:booking_id>/resolve', methods=['POST'])
@login_required
@admin_required
def resolve_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    resolution = request.form.get('resolution', 'completed')
    booking.status = resolution
    db.session.commit()
    flash(f'Booking resolved as {resolution}.', 'success')
    return redirect(url_for('admin.bookings'))


@admin.route('/withdrawals')
@login_required
@admin_required
def withdrawals():
    pending = Withdrawal.query.filter_by(status='pending').all()
    all_w = Withdrawal.query.order_by(Withdrawal.created_at.desc()).all()
    return render_template('admin/withdrawals.html', pending=pending, all_withdrawals=all_w)


@admin.route('/withdrawals/<int:w_id>/process', methods=['POST'])
@login_required
@admin_required
def process_withdrawal(w_id):
    w = Withdrawal.query.get_or_404(w_id)
    action = request.form.get('action', 'approved')
    w.status = action
    from datetime import datetime
    w.processed_at = datetime.utcnow()
    if action == 'rejected':
        w.provider.earnings_balance += w.amount
    db.session.commit()
    flash(f'Withdrawal {action}.', 'success')
    return redirect(url_for('admin.withdrawals'))


@admin.route('/services')
@login_required
@admin_required
def services():
    categories = ServiceCategory.query.all()
    all_services = Service.query.all()
    return render_template('admin/services.html', categories=categories, services=all_services)
