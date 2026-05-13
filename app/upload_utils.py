import json
import os
from uuid import uuid4

import cloudinary.uploader
from flask import current_app, url_for
from werkzeug.utils import secure_filename


IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
VIDEO_EXTENSIONS = {'mp4', 'mov', 'webm', 'avi', 'mkv'}
ALLOWED_EXTENSIONS = IMAGE_EXTENSIONS | VIDEO_EXTENSIONS


def file_kind(filename):
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    if ext in IMAGE_EXTENSIONS:
        return 'image'
    if ext in VIDEO_EXTENSIONS:
        return 'video'
    return None


def upload_media(file_storage, folder):
    if not file_storage or not file_storage.filename:
        return None

    kind = file_kind(file_storage.filename)
    if not kind:
        raise ValueError('Unsupported file type.')

    if os.getenv('CLOUDINARY_CLOUD_NAME'):
        result = cloudinary.uploader.upload(
            file_storage,
            folder=f'bookglam/{folder}',
            resource_type='auto',
        )
        return {
            'url': result['secure_url'],
            'type': result.get('resource_type', kind),
        }

    filename = secure_filename(file_storage.filename)
    ext = filename.rsplit('.', 1)[-1].lower()
    stored_name = f'{uuid4().hex}.{ext}'
    upload_dir = os.path.join(current_app.static_folder, 'uploads', folder)
    os.makedirs(upload_dir, exist_ok=True)
    file_storage.save(os.path.join(upload_dir, stored_name))

    return {
        'url': url_for('static', filename=f'uploads/{folder}/{stored_name}'),
        'type': kind,
    }


def load_portfolio_media(profile):
    if not profile.portfolio_images:
        return []
    try:
        raw_items = json.loads(profile.portfolio_images)
    except json.JSONDecodeError:
        return []

    media_items = []
    for item in raw_items:
        if isinstance(item, str):
            media_items.append({'url': item, 'type': 'image'})
        elif isinstance(item, dict) and item.get('url'):
            media_items.append({
                'url': item['url'],
                'type': item.get('type', 'image'),
            })
    return media_items
