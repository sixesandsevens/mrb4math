from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from ..forms.forms import LoginForm, RegisterForm
from ..models.models import User
from .. import db
from sqlalchemy.exc import SQLAlchemyError

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            return redirect(url_for('admin.admin_home'))
        else:
            flash('Invalid username or password')
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=hashed_password,
            is_admin=False
        )
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully. You can now log in.', 'success')
            return redirect(url_for('auth.login'))
        except SQLAlchemyError:
            db.session.rollback()
            flash('An error occurred while creating your account.', 'danger')
    
    return render_template('register.html', form=form)
