from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.client import client
from app.extensions import db
from app.models import (
    Booking,
    Service,
    ServiceCategory,
    ProviderProfile,
    ProviderPortfolio,
    Review,
    Message,
    LocationUpdate,
)
from app.upload_utils import load_portfolio_media, upload_media
from datetime import datetime
from functools import wraps


def client_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.role not in ('client', 'admin'):
            flash('Access denied.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated


def _split_specialties(profile):
    if not profile.specialties:
        return []
    return [item.strip() for item in profile.specialties.split(',') if item.strip()]


def _provider_matches_service(profile, service):
    haystack = ' '.join([
        profile.specialties or '',
        profile.bio or '',
        profile.tier or '',
    ]).lower()
    service_words = [service.name.lower(), service.category.name.lower() if service.category else '']
    return any(word and word in haystack for word in service_words)


def _mock_provider_stats(profile, booking_id=None):
    seed = (profile.id * 17) + ((booking_id or 0) * 7)
    completed = Booking.query.filter_by(provider_id=profile.id, status='completed').count()
    completed_jobs = max(completed, 86 + (seed % 320))
    rating = profile.rating if profile.rating and profile.rating >= 4.0 else round(4.7 + ((seed % 4) / 10), 1)
    return {
        'rating': min(rating, 5.0),
        'completed_jobs': completed_jobs,
        'distance': round(1.0 + ((seed % 42) / 10), 1),
        'eta': 12 + (seed % 24),
        'repeat_customers': 24 + (seed % 58),
        'years_experience': profile.years_experience or (3 + (seed % 9)),
        'specialties': _split_specialties(profile)[:4],
    }


def _portfolio_media(profile):
    items = [
        {'url': item.image_url, 'type': 'image', 'caption': item.caption}
        for item in ProviderPortfolio.query
        .filter_by(provider_id=profile.id)
        .order_by(ProviderPortfolio.created_at.desc())
        .all()
    ]
    if items:
        return items
    return load_portfolio_media(profile)


def _providers_for_service(service, booking_id=None):
    providers = (ProviderProfile.query
                 .filter_by(is_verified=True)
                 .order_by(ProviderProfile.is_online.desc(), ProviderProfile.rating.desc())
                 .all())
    matched = [provider for provider in providers if _provider_matches_service(provider, service)]
    selected = matched or providers
    cards = []
    for provider in selected:
        stats = _mock_provider_stats(provider, booking_id)
        portfolio = _portfolio_media(provider)
        cards.append({
            'profile': provider,
            'stats': stats,
            'portfolio': portfolio[:3],
        })
    return cards


@client.route('/dashboard')
@login_required
@client_required
def dashboard():
    bookings = (Booking.query
                .filter_by(client_id=current_user.id)
                .order_by(Booking.created_at.desc())
                .limit(5).all())
    return render_template('client/dashboard.html', bookings=bookings)


@client.route('/book', methods=['GET', 'POST'])
@login_required
@client_required
def book():
    categories = ServiceCategory.query.all()
    services = Service.query.filter_by(is_active=True).all()
    providers = ProviderProfile.query.filter_by(is_verified=True).all()
    if request.method == 'POST':
        service_id = request.form.get('service_id', type=int)
        booking_type = request.form.get('booking_type', 'home')
        tier = request.form.get('tier', 'standard')
        is_instant = request.form.get('is_instant') == 'true'
        scheduled_str = request.form.get('scheduled_at')
        address = request.form.get('address', '')
        payment_method = request.form.get('payment_method', 'cash')
        notes = request.form.get('notes', '')

        scheduled_at = None
        if scheduled_str and not is_instant:
            try:
                scheduled_at = datetime.strptime(scheduled_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                pass

        service = Service.query.get_or_404(service_id)
        price_map = {'basic': service.base_price_basic,
                     'standard': service.base_price_standard,
                     'premium': service.base_price_premium}
        price = price_map.get(tier, service.base_price_standard)

        booking = Booking(
            client_id=current_user.id,
            provider_id=None,
            service_id=service_id,
            booking_type=booking_type,
            service_tier=tier,
            is_instant=is_instant,
            scheduled_at=scheduled_at,
            address=address,
            payment_method=payment_method,
            notes=notes,
            price=price,
            status='pending',
        )
        db.session.add(booking)
        db.session.commit()
        flash('Booking details saved. Choose your preferred provider next.', 'success')
        return redirect(url_for('client.select_provider', booking_id=booking.id))

    return render_template('client/book.html',
                           categories=categories,
                           services=services,
                           providers=providers)


@client.route('/bookings')
@login_required
@client_required
def bookings():
    all_bookings = (Booking.query
                    .filter_by(client_id=current_user.id)
                    .order_by(Booking.created_at.desc()).all())
    return render_template('client/bookings.html', bookings=all_bookings)


@client.route('/bookings/<int:booking_id>')
@login_required
@client_required
def booking_detail(booking_id):
    booking = Booking.query.filter_by(id=booking_id, client_id=current_user.id).first_or_404()
    return render_template('client/booking_detail.html', booking=booking)


@client.route('/select-provider/<int:booking_id>')
@login_required
@client_required
def select_provider(booking_id):
    booking = Booking.query.filter_by(id=booking_id, client_id=current_user.id).first_or_404()
    provider_cards = _providers_for_service(booking.service, booking.id)
    return render_template('client/select_provider.html',
                           booking=booking,
                           provider_cards=provider_cards)


@client.route('/select-provider/<int:booking_id>/<int:provider_id>', methods=['POST'])
@login_required
@client_required
def choose_provider(booking_id, provider_id):
    booking = Booking.query.filter_by(id=booking_id, client_id=current_user.id).first_or_404()
    provider = ProviderProfile.query.filter_by(id=provider_id, is_verified=True).first_or_404()
    if booking.status not in ('pending', 'accepted'):
        flash('This booking can no longer be reassigned.', 'warning')
        return redirect(url_for('client.booking_detail', booking_id=booking.id))
    service_matches = [
        item for item in ProviderProfile.query.filter_by(is_verified=True).all()
        if _provider_matches_service(item, booking.service)
    ]
    if service_matches and not _provider_matches_service(provider, booking.service):
        flash('That provider is not listed for this service yet.', 'warning')
        return redirect(url_for('client.select_provider', booking_id=booking.id))

    booking.provider_id = provider.id
    booking.status = 'pending'
    db.session.commit()
    flash(f'{provider.user.full_name} has been selected for your booking.', 'success')
    return redirect(url_for('client.booking_detail', booking_id=booking.id))


@client.route('/bookings/<int:booking_id>/chat')
@login_required
@client_required
def chat(booking_id):
    booking = Booking.query.filter_by(id=booking_id, client_id=current_user.id).first_or_404()
    messages = (Message.query
                .filter_by(booking_id=booking.id)
                .order_by(Message.created_at.asc()).all())
    return render_template('shared/chat.html',
                           booking=booking,
                           messages=messages,
                           role='client')


@client.route('/bookings/<int:booking_id>/track')
@login_required
@client_required
def track(booking_id):
    booking = Booking.query.filter_by(id=booking_id, client_id=current_user.id).first_or_404()
    if not booking.provider:
        flash('Tracking is available after a provider accepts your booking.', 'warning')
        return redirect(url_for('client.booking_detail', booking_id=booking.id))

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
                           role='client',
                           provider_user_id=booking.provider.user_id,
                           locations=locations,
                           avatars=avatars)


@client.route('/provider/<int:provider_id>')
@client.route('/providers/<int:provider_id>')
@login_required
@client_required
def provider_profile(provider_id):
    profile = ProviderProfile.query.get_or_404(provider_id)
    portfolio_media = _portfolio_media(profile)
    stats = _mock_provider_stats(profile)
    reviews = (Review.query
               .join(Booking)
               .filter(Booking.provider_id == profile.id)
               .order_by(Review.created_at.desc())
               .limit(8).all())
    booking_id = request.args.get('booking_id', type=int)
    booking = None
    if booking_id:
        booking = Booking.query.filter_by(id=booking_id, client_id=current_user.id).first()
    return render_template('client/provider_profile.html',
                           profile=profile,
                           portfolio_media=portfolio_media,
                           stats=stats,
                           reviews=reviews,
                           booking=booking)


@client.route('/bookings/<int:booking_id>/review', methods=['POST'])
@login_required
@client_required
def leave_review(booking_id):
    booking = Booking.query.filter_by(id=booking_id, client_id=current_user.id).first_or_404()
    if booking.status != 'completed':
        flash('You can only review completed bookings.', 'warning')
        return redirect(url_for('client.booking_detail', booking_id=booking_id))
    if booking.review:
        flash('You have already reviewed this booking.', 'info')
        return redirect(url_for('client.booking_detail', booking_id=booking_id))

    rating = request.form.get('rating', type=int)
    comment = request.form.get('comment', '')
    review = Review(booking_id=booking_id, rating=rating, comment=comment)
    db.session.add(review)

    # Update provider average rating
    if booking.provider:
        provider = booking.provider
        all_reviews = [r for b in provider.bookings for r in [b.review] if r]
        total = sum(r.rating for r in all_reviews) + rating
        count = len(all_reviews) + 1
        provider.rating = round(total / count, 1)
        provider.total_reviews = count

    db.session.commit()
    flash('Review submitted. Thank you!', 'success')
    return redirect(url_for('client.booking_detail', booking_id=booking_id))


@client.route('/profile', methods=['GET', 'POST'])
@login_required
@client_required
def profile():
    if request.method == 'POST':
        current_user.full_name = request.form.get('full_name', current_user.full_name)
        current_user.phone = request.form.get('phone', current_user.phone)
        avatar = request.files.get('avatar')
        if avatar and avatar.filename:
            try:
                current_user.avatar = upload_media(avatar, 'avatars')['url']
            except ValueError as exc:
                flash(str(exc), 'danger')
                return redirect(url_for('client.profile'))
        db.session.commit()
        flash('Profile updated.', 'success')
    return render_template('client/profile.html')
