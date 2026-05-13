from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.auth import auth
from app.extensions import db, bcrypt
from app.models import User, ProviderProfile


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return _redirect_by_role(current_user.role)
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user, remember=request.form.get('remember'))
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else _redirect_by_role(user.role)
        flash('Invalid email or password.', 'danger')
    return render_template('auth/login.html')


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return _redirect_by_role(current_user.role)
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        role = request.form.get('role', 'client')  # client | provider

        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('auth/signup.html')

        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(full_name=full_name, email=email, phone=phone,
                    password_hash=hashed_pw, role=role)
        db.session.add(user)
        db.session.flush()  # get user.id

        if role == 'provider':
            profile = ProviderProfile(user_id=user.id)
            db.session.add(profile)

        db.session.commit()
        login_user(user)
        flash('Account created! Welcome to BookGlam.', 'success')
        return _redirect_by_role(role)

    return render_template('auth/signup.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


def _redirect_by_role(role):
    if role == 'admin':
        return redirect(url_for('admin.dashboard'))
    elif role == 'provider':
        return redirect(url_for('provider.dashboard'))
    else:
        return redirect(url_for('client.dashboard'))
