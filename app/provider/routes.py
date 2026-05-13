from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.provider import provider
from app.extensions import db
from app.models import Booking, ProviderProfile, Withdrawal, Message, LocationUpdate
from app.upload_utils import load_portfolio_media, upload_media
from functools import wraps


def provider_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.role not in ('provider', 'admin'):
            flash('Access denied.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated


def get_profile():
    return ProviderProfile.query.filter_by(user_id=current_user.id).first_or_404()


@provider.route('/dashboard')
@login_required
@provider_required
def dashboard():
    profile = get_profile()
    pending = Booking.query.filter_by(provider_id=profile.id, status='pending').count()
    active = Booking.query.filter_by(provider_id=profile.id, status='in_progress').count()
    completed = Booking.query.filter_by(provider_id=profile.id, status='completed').count()
    recent = (Booking.query
              .filter_by(provider_id=profile.id)
              .order_by(Booking.created_at.desc())
              .limit(5).all())
    return render_template('provider/dashboard.html',
                           profile=profile,
                           pending=pending,
                           active=active,
                           completed=completed,
                           recent=recent)


@provider.route('/jobs')
@login_required
@provider_required
def jobs():
    profile = get_profile()
    status_filter = request.args.get('status', 'all')
    query = Booking.query.filter_by(provider_id=profile.id)
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    jobs = query.order_by(Booking.created_at.desc()).all()
    return render_template('provider/jobs.html', jobs=jobs, status_filter=status_filter)


@provider.route('/jobs/<int:booking_id>/chat')
@login_required
@provider_required
def chat(booking_id):
    profile = get_profile()
    booking = Booking.query.filter_by(id=booking_id, provider_id=profile.id).first_or_404()
    messages = (Message.query
                .filter_by(booking_id=booking.id)
                .order_by(Message.created_at.asc()).all())
    return render_template('shared/chat.html',
                           booking=booking,
                           messages=messages,
                           role='provider')


@provider.route('/jobs/<int:booking_id>/track')
@login_required
@provider_required
def track(booking_id):
    profile = get_profile()
    booking = Booking.query.filter_by(id=booking_id, provider_id=profile.id).first_or_404()
    locations = {
        str(loc.user_id): {'lat': loc.latitude, 'lng': loc.longitude}
        for loc in LocationUpdate.query.filter_by(booking_id=booking.id).all()
    }
    avatars = {
        str(booking.client_id): booking.client.avatar,
        str(booking.provider.user_id): booking.provider.user.avatar,
    }
    return render_template('shared/track.html',
                           booking=booking,
                           role='provider',
                           provider_user_id=booking.provider.user_id,
                           locations=locations,
                           avatars=avatars)


@provider.route('/jobs/<int:booking_id>/update', methods=['POST'])
@login_required
@provider_required
def update_job(booking_id):
    profile = get_profile()
    booking = Booking.query.filter_by(id=booking_id, provider_id=profile.id).first_or_404()
    new_status = request.form.get('status')
    allowed = {
        'pending': ['accepted', 'cancelled'],
        'accepted': ['on_the_way', 'cancelled'],
        'on_the_way': ['in_progress'],
        'in_progress': ['completed'],
    }
    if new_status in allowed.get(booking.status, []):
        booking.status = new_status
        if new_status == 'completed' and booking.price:
            commission = booking.price * 0.15
            profile.earnings_balance += booking.price - commission
        db.session.commit()
        flash(f'Job status updated to {new_status}.', 'success')
    else:
        flash('Invalid status transition.', 'danger')
    return redirect(url_for('provider.jobs'))


@provider.route('/available-jobs')
@login_required
@provider_required
def available_jobs():
    profile = get_profile()
    jobs = (Booking.query
            .filter_by(status='pending', provider_id=None)
            .order_by(Booking.created_at.desc()).all())
    return render_template('provider/available_jobs.html', jobs=jobs, profile=profile)


@provider.route('/available-jobs/<int:booking_id>/accept', methods=['POST'])
@login_required
@provider_required
def accept_job(booking_id):
    profile = get_profile()
    booking = Booking.query.filter_by(id=booking_id, status='pending', provider_id=None).first_or_404()
    booking.provider_id = profile.id
    booking.status = 'accepted'
    db.session.commit()
    flash('Job accepted!', 'success')
    return redirect(url_for('provider.jobs'))


@provider.route('/toggle-availability', methods=['POST'])
@login_required
@provider_required
def toggle_availability():
    profile = get_profile()
    profile.is_online = not profile.is_online
    db.session.commit()
    status = 'online' if profile.is_online else 'offline'
    return jsonify({'status': status, 'is_online': profile.is_online})


@provider.route('/earnings')
@login_required
@provider_required
def earnings():
    profile = get_profile()
    withdrawals = (Withdrawal.query
                   .filter_by(provider_id=profile.id)
                   .order_by(Withdrawal.created_at.desc()).all())
    return render_template('provider/earnings.html', profile=profile, withdrawals=withdrawals)


@provider.route('/withdraw', methods=['POST'])
@login_required
@provider_required
def withdraw():
    profile = get_profile()
    amount = request.form.get('amount', type=float)
    bank_name = request.form.get('bank_name', '')
    account_number = request.form.get('account_number', '')
    account_name = request.form.get('account_name', '')

    if not amount or amount <= 0 or amount > profile.earnings_balance:
        flash('Invalid withdrawal amount.', 'danger')
        return redirect(url_for('provider.earnings'))

    w = Withdrawal(provider_id=profile.id, amount=amount,
                   bank_name=bank_name, account_number=account_number,
                   account_name=account_name)
    profile.earnings_balance -= amount
    db.session.add(w)
    db.session.commit()
    flash('Withdrawal request submitted.', 'success')
    return redirect(url_for('provider.earnings'))


@provider.route('/profile', methods=['GET', 'POST'])
@login_required
@provider_required
def profile_page():
    prof = get_profile()
    if request.method == 'POST':
        current_user.full_name = request.form.get('full_name', current_user.full_name)
        current_user.phone = request.form.get('phone', current_user.phone)
        prof.bio = request.form.get('bio', prof.bio)
        prof.specialties = request.form.get('specialties', prof.specialties)
        prof.location = request.form.get('location', prof.location)
        prof.tier = request.form.get('tier', prof.tier)
        years_experience = request.form.get('years_experience', type=int)
        prof.years_experience = years_experience if years_experience and years_experience >= 0 else None
        avatar = request.files.get('avatar')
        if avatar and avatar.filename:
            try:
                current_user.avatar = upload_media(avatar, 'avatars')['url']
            except ValueError as exc:
                flash(str(exc), 'danger')
                return redirect(url_for('provider.profile_page'))

        media_items = load_portfolio_media(prof)

        for media_file in request.files.getlist('portfolio_media'):
            if not media_file or not media_file.filename:
                continue
            try:
                media_items.append(upload_media(media_file, 'provider-work'))
            except ValueError as exc:
                flash(str(exc), 'danger')
                return redirect(url_for('provider.profile_page'))
        import json
        prof.portfolio_images = json.dumps(media_items) if media_items else None
        db.session.commit()
        flash('Profile updated.', 'success')
    portfolio_media = load_portfolio_media(prof)
    return render_template('provider/profile.html',
                           profile=prof,
                           portfolio_media=portfolio_media)
