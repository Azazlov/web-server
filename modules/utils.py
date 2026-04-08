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


# Previewable file types
PREVIEWABLE_EXTENSIONS = {
    # Images
    'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg', 'ico', 'tiff', 'tif',
    # PDF
    'pdf',
    # Text / code
    'txt', 'md', 'csv', 'json', 'xml', 'html', 'htm', 'css', 'js', 'py',
    'java', 'c', 'cpp', 'h', 'rb', 'go', 'rs', 'ts', 'yaml', 'yml', 'ini',
    'cfg', 'conf', 'log', 'sh', 'bat', 'sql', 'r', 'm',
    # Office (viewable via browser if MIME is supported)
    'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
}

# MIME types we can render directly in an iframe
INLINE_MIME_TYPES = {
    'image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/webp',
    'image/svg+xml', 'image/tiff', 'image/x-icon',
    'application/pdf',
    'text/plain', 'text/html', 'text/css', 'text/csv', 'text/xml',
    'application/json',
}


def is_previewable(filename):
    """Check if a file is previewable based on extension."""
    if not filename or '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in PREVIEWABLE_EXTENSIONS


def safe_filename(filename):
    """Get secure filename."""
    return secure_filename(filename) if filename else ''


def rename_item(base_path, rel_path, old_name, new_name, is_dir=False):
    """
    Rename a file or folder within a base path.

    Args:
        base_path: Base directory path (e.g. uploads/shared)
        rel_path: Relative path to parent directory of the item
        old_name: Current name of the file/folder
        new_name: New name for the file/folder
        is_dir: Whether the item is a directory

    Returns:
        tuple: (success: bool, message: str)
    """
    old_full_path = os.path.join(base_path, rel_path, old_name) if rel_path else os.path.join(base_path, old_name)
    new_full_path = os.path.join(base_path, rel_path, new_name) if rel_path else os.path.join(base_path, new_name)

    # Security check
    old_full_path = os.path.normpath(old_full_path)
    new_full_path = os.path.normpath(new_full_path)

    if not old_full_path.startswith(os.path.normpath(base_path)):
        return False, 'Доступ запрещён.'

    if not new_full_path.startswith(os.path.normpath(base_path)):
        return False, 'Доступ запрещён.'

    # Check source exists
    if not os.path.exists(old_full_path):
        return False, 'Элемент не найден.'

    # Check target doesn't exist
    if os.path.exists(new_full_path):
        return False, 'Файл или папка с таким именем уже существует.'

    # Validate new name
    if is_dir:
        safe_new_name = secure_filename(new_name)
    else:
        # For files, preserve extension
        if '.' in new_name:
            name_part, ext = new_name.rsplit('.', 1)
            safe_name = secure_filename(name_part)
            safe_ext = secure_filename(ext)
            safe_new_name = f'{safe_name}.{safe_ext}' if safe_name else None
        else:
            safe_new_name = secure_filename(new_name)

        if safe_new_name is None:
            return False, 'Неверное имя файла.'

    if not safe_new_name:
        return False, 'Неверное имя.'

    new_full_path = os.path.join(os.path.dirname(new_full_path), safe_new_name)

    try:
        os.rename(old_full_path, new_full_path)
        return True, f'Элемент переименован в "{safe_new_name}".'
    except OSError as e:
        return False, f'Ошибка при переименовании: {str(e)}'


def search_files(base_path, query, rel_path=''):
    """
    Search for files and folders by name in base_path and all subdirectories.

    Args:
        base_path: Base directory to search in
        query: Search query (substring match, case-insensitive)
        rel_path: Starting relative path (optional)

    Returns:
        list: Matching items with metadata
    """
    if not query or not query.strip():
        return []

    query_lower = query.strip().lower()
    results = []
    search_root = os.path.join(base_path, rel_path) if rel_path else base_path

    if not os.path.exists(search_root):
        return []

    for root, dirs, files in os.walk(search_root):
        # Search directories
        for d in dirs:
            if query_lower in d.lower():
                full_path = os.path.join(root, d)
                item_rel = os.path.relpath(full_path, base_path).replace('\\', '/')
                results.append({
                    'name': d,
                    'is_dir': True,
                    'path': item_rel,
                    'parent': os.path.dirname(item_rel).replace('\\', '/'),
                    'size': 0,
                    'size_human': '-',
                    'modified': datetime.fromtimestamp(os.stat(full_path).st_mtime).strftime('%Y-%m-%d %H:%M'),
                })

        # Search files
        for f in files:
            if query_lower in f.lower():
                full_path = os.path.join(root, f)
                item_rel = os.path.relpath(full_path, base_path).replace('\\', '/')
                stat = os.stat(full_path)
                results.append({
                    'name': f,
                    'is_dir': False,
                    'path': item_rel,
                    'parent': os.path.dirname(item_rel).replace('\\', '/'),
                    'size': stat.st_size,
                    'size_human': format_size(stat.st_size),
                    'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M'),
                })

    # Sort: dirs first, then alphabetically
    results.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))
    return results
