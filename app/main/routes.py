from flask import render_template
from app.main import main
from app.models import ServiceCategory, Service, ProviderProfile, Review
from app.extensions import db


@main.route('/')
def index():
    categories = ServiceCategory.query.all()
    providers = (ProviderProfile.query
                 .filter_by(is_verified=True, is_online=True)
                 .order_by(ProviderProfile.rating.desc())
                 .limit(6).all())
    return render_template('main/index.html', categories=categories, providers=providers)


@main.route('/services')
def services():
    categories = ServiceCategory.query.all()
    services = Service.query.filter_by(is_active=True).all()
    return render_template('main/services.html', categories=categories, services=services)


@main.route('/about')
def about():
    return render_template('main/about.html')


@main.route('/how-it-works')
def how_it_works():
    return render_template('main/how_it_works.html')


@main.route('/contact')
def contact():
    return render_template('main/contact.html')
