"""
FileShare Local v2.1 - Authentication Routes
"""
import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from modules.models import User, get_user_by_username, create_user, get_user_count, change_password, get_folder_size, format_folder_size
from modules.config import config

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Введите имя пользователя и пароль.', 'error')
            return render_template('login.html')

        user = get_user_by_username(username)
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            flash(f'С возвращением, {user.username}!', 'success')
            return redirect(next_page if next_page else url_for('main.personal'))
        else:
            flash('Неверное имя пользователя или пароль.', 'error')

    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    if get_user_count() > 0:
        # Check if registration is allowed
        if not config.allow_registration:
            flash('Регистрация временно отключена. Обратитесь к администратору.', 'error')
            return redirect(url_for('auth.login'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not username or not password:
            flash('Заполните все поля.', 'error')
            return render_template('register.html')

        if password != confirm_password:
            flash('Пароли не совпадают.', 'error')
            return render_template('register.html')

        if len(password) < 6:
            flash('Пароль должен быть не менее 6 символов.', 'error')
            return render_template('register.html')

        if get_user_by_username(username):
            flash('Имя пользователя уже существует.', 'error')
            return render_template('register.html')

        # First user becomes admin
        is_first_user = get_user_count() == 0
        user = create_user(username, password, is_admin=is_first_user)
        
        role_text = 'администратор' if is_first_user else 'пользователь'
        flash(f'Регистрация успешна! Вы {role_text}.', 'success')
        return redirect(url_for('auth.login'))

    user_count = get_user_count()
    return render_template('register.html', user_count=user_count)


@auth_bp.route('/logout')
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    flash('Вы вышли из системы.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/profile')
@login_required
def profile():
    """User profile page with password change."""
    upload_folder = current_app.config['UPLOAD_FOLDER']
    personal_path = os.path.join(upload_folder, 'users', current_user.username)
    folder_size = get_folder_size(personal_path)
    size_human = format_folder_size(folder_size)

    return render_template('profile.html', size_human=size_human)


@auth_bp.route('/profile/password', methods=['POST'])
@login_required
def change_user_password():
    """Handle password change."""
    old_password = request.form.get('old_password', '')
    new_password = request.form.get('new_password', '')
    confirm_password = request.form.get('confirm_password', '')

    if not old_password or not new_password:
        flash('Заполните все поля.', 'error')
        return redirect(url_for('auth.profile'))

    if new_password != confirm_password:
        flash('Новые пароли не совпадают.', 'error')
        return redirect(url_for('auth.profile'))

    success, message = change_password(current_user.id, old_password, new_password)
    flash(message, 'success' if success else 'error')

    if success:
        return redirect(url_for('auth.profile'))
    return redirect(url_for('auth.profile'))
