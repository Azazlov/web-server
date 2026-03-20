"""
FileShare Local v2.1 - Admin Routes
"""
import sys
import os
import time
from threading import Thread
from flask import Blueprint, render_template, redirect, url_for, flash, current_app, request
from flask_login import login_required, current_user
from modules.utils import admin_required
from modules.models import get_all_users, get_user_by_id, toggle_user_upload_block, User, db
from modules.config import config

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/admin')
@login_required
@admin_required
def admin_panel():
    """Admin panel with settings and user management."""
    all_users = get_all_users()
    config_info = {
        'port': config.server_port,
        'max_upload_size': config.max_upload_size_bytes,
        'allow_registration': config.allow_registration,
        'upload_folder': current_app.config.get('UPLOAD_FOLDER', ''),
        'debug': config.debug_mode
    }
    return render_template('admin.html', all_users=all_users, config_info=config_info)


@admin_bp.route('/admin/settings', methods=['POST'])
@login_required
@admin_required
def admin_settings():
    """Handle admin settings actions."""
    action = request.form.get('action')
    
    if action == 'toggle_registration':
        new_status = config.toggle_registration()
        current_app.config['ALLOW_REGISTRATION'] = new_status
        status = 'включена' if new_status else 'отключена'
        flash(f'Регистрация пользователей {status}.', 'success')
    
    elif action == 'restart_server':
        # Save current state before restart
        config.save()
        flash('Сервер перезапускается...', 'info')
        
        def restart():
            time.sleep(2)
            try:
                os.execv(sys.executable, [sys.executable] + sys.argv)
            except Exception as e:
                print(f'Restart error: {e}')
        
        Thread(target=restart, daemon=True).start()
        return redirect(url_for('admin.admin_panel'))
    
    elif action == 'toggle_upload_block':
        user_id = request.form.get('user_id', type=int)
        user = get_user_by_id(user_id)
        
        if user and user.id != current_user.id:
            new_status = toggle_user_upload_block(user_id)
            status = 'запрещена' if new_status else 'разрешена'
            flash(f'Загрузка файлов пользователю {user.username} {status}.', 'success')
        else:
            flash('Нельзя изменить права самому себе.', 'error')
    
    return redirect(url_for('admin.admin_panel'))
