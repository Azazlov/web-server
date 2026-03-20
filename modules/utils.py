"""
FileShare Local v2.1 - Utility Functions Module
"""
import os
import shutil
from datetime import datetime
from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user
from werkzeug.utils import secure_filename


def format_size(size):
    """Convert bytes to human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"


def get_folder_contents(base_path, rel_path=''):
    """
    Get contents of a folder with metadata.
    
    Returns:
        tuple: (items list, relative path)
    """
    full_path = os.path.join(base_path, rel_path) if rel_path else base_path
    
    if not os.path.exists(full_path):
        return [], []
    
    items = []
    for name in os.listdir(full_path):
        item_path = os.path.join(full_path, name)
        stat = os.stat(item_path)
        is_dir = os.path.isdir(item_path)
        
        items.append({
            'name': name,
            'is_dir': is_dir,
            'size': stat.st_size if not is_dir else 0,
            'size_human': format_size(stat.st_size) if not is_dir else '-',
            'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M'),
            'path': os.path.join(rel_path, name) if rel_path else name
        })
    
    # Sort: directories first, then files, alphabetically
    items.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))
    return items, rel_path


def get_breadcrumbs(rel_path):
    """Generate breadcrumbs for navigation."""
    crumbs = [{'name': 'Корень', 'path': ''}]
    if rel_path:
        parts = rel_path.replace('\\', '/').split('/')
        current = ''
        for part in parts:
            if part:
                current = os.path.join(current, part) if current else part
                crumbs.append({'name': part, 'path': current})
    return crumbs


def get_relative_path(base_path, request):
    """
    Get and validate relative path from request.
    
    Returns:
        str or None: Relative path or None if invalid
    """
    rel_path = request.args.get('path', '')
    rel_path = rel_path.replace('..', '')  # Basic path traversal prevention
    full_path = os.path.normpath(os.path.join(base_path, rel_path))
    
    # Security check: ensure path is within base
    if not full_path.startswith(base_path):
        return None
    return rel_path


def get_base_path(folder_type, upload_folder, username=None):
    """Get base path for folder type."""
    if folder_type == 'shared':
        return os.path.join(upload_folder, 'shared')
    elif folder_type == 'personal' and username:
        return os.path.join(upload_folder, 'users', username)
    return None


def ensure_upload_dirs(upload_folder):
    """Ensure upload directories exist."""
    os.makedirs(os.path.join(upload_folder, 'shared'), exist_ok=True)
    os.makedirs(os.path.join(upload_folder, 'users'), exist_ok=True)


def migrate_user_folders(upload_folder, get_all_users_func=None):
    """Migrate old user folders (user_1, user_2) to new username-based folders."""
    from modules.models import get_all_users
    
    users_folder = os.path.join(upload_folder, 'users')
    if not os.path.exists(users_folder):
        return
    
    users = get_all_users()
    user_id_map = {user.id: user.username for user in users}
    
    for item in os.listdir(users_folder):
        item_path = os.path.join(users_folder, item)
        if os.path.isdir(item_path) and item.startswith('user_'):
            try:
                user_id = int(item.replace('user_', ''))
                if user_id in user_id_map:
                    new_name = user_id_map[user_id]
                    new_path = os.path.join(users_folder, new_name)
                    if not os.path.exists(new_path):
                        os.rename(item_path, new_path)
                        print(f'Migrated folder: {item} -> {new_name}')
                    else:
                        shutil.rmtree(item_path)
                        print(f'Removed old folder: {item}')
            except (ValueError, OSError) as e:
                print(f'Error migrating folder {item}: {e}')


def validate_path_security(base_path, rel_path='', filename=''):
    """
    Validate that path is within allowed base path.
    
    Returns:
        tuple: (full_path, is_valid)
    """
    full_path = os.path.join(base_path, rel_path, filename) if rel_path or filename else base_path
    full_path = os.path.normpath(full_path)
    is_valid = full_path.startswith(base_path)
    return full_path, is_valid


def admin_required(f):
    """Decorator to require admin privileges."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Доступ запрещён. Требуются права администратора.', 'error')
            return redirect(url_for('main.shared'))
        return f(*args, **kwargs)
    return decorated_function


def allowed_file(filename, allowed_extensions=None):
    """
    Check if file extension is allowed.
    By default, all files are allowed.
    """
    if allowed_extensions is None:
        return True
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def safe_filename(filename):
    """Get secure filename."""
    return secure_filename(filename) if filename else ''
