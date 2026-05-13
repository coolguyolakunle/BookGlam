from flask import request
from flask_login import current_user
from flask_socketio import emit, join_room, leave_room
from app.extensions import socketio, db
from app.models import Message, Booking, LocationUpdate
from datetime import datetime


def booking_room(booking_id):
    return f'booking_{booking_id}'


def user_can_access_booking(booking):
    if not current_user.is_authenticated:
        return False
    if current_user.role == 'admin':
        return True
    if booking.client_id == current_user.id:
        return True
    return bool(booking.provider and booking.provider.user_id == current_user.id)


@socketio.on('join_booking')
def on_join(data):
    booking_id = data.get('booking_id')
    if not booking_id:
        return
    booking = Booking.query.get(booking_id)
    if not booking or not user_can_access_booking(booking):
        return
    room = booking_room(booking_id)
    join_room(room)


@socketio.on('leave_booking')
def on_leave(data):
    booking_id = data.get('booking_id')
    if not booking_id:
        return
    leave_room(booking_room(booking_id))


@socketio.on('send_message')
def on_send_message(data):
    booking_id = data.get('booking_id')
    body = (data.get('body') or '').strip()

    if not booking_id or not body or not current_user.is_authenticated:
        return

    booking = Booking.query.get(booking_id)
    if not booking or not user_can_access_booking(booking):
        return

    msg = Message(
        booking_id=booking_id,
        sender_id=current_user.id,
        body=body,
    )
    db.session.add(msg)
    db.session.commit()

    emit('new_message', msg.to_dict(), room=booking_room(booking_id))


@socketio.on('location_update')
def on_location_update(data):
    booking_id = data.get('booking_id')
    lat = data.get('latitude')
    lng = data.get('longitude')

    if not booking_id or lat is None or lng is None or not current_user.is_authenticated:
        return

    booking = Booking.query.get(booking_id)
    if not booking or not user_can_access_booking(booking):
        return

    # Upsert: one live location row per user+booking
    loc = LocationUpdate.query.filter_by(
        booking_id=booking_id, user_id=current_user.id
    ).first()
    if loc:
        loc.latitude = lat
        loc.longitude = lng
        loc.updated_at = datetime.utcnow()
    else:
        loc = LocationUpdate(
            booking_id=booking_id,
            user_id=current_user.id,
            latitude=lat,
            longitude=lng,
        )
        db.session.add(loc)
    db.session.commit()

    emit('location_updated', {
        'user_id': current_user.id,
        'latitude': lat,
        'longitude': lng,
        'role': data.get('role', 'unknown'),
    }, room=booking_room(booking_id))
