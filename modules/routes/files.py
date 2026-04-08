"""
FileShare Local v2.1 - File Management Routes
"""
import os
import shutil
from flask import Blueprint, request, redirect, url_for, flash, current_app, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from modules.utils import (
    get_base_path, get_relative_path, validate_path_security,
    safe_filename, admin_required, is_previewable
)
from modules.models import User

files_bp = Blueprint('files', __name__)


@files_bp.route('/upload', methods=['POST'])
@login_required
def upload():
    """Handle file upload."""
    folder_type = request.form.get('folder_type', 'personal')

    # Check if user upload is blocked for personal folder
    if current_user.upload_blocked and folder_type == 'personal':
        flash('Ваша возможность загрузки файлов заблокирована. Обратитесь к администратору.', 'error')
        return redirect(url_for('main.personal'))

    # Check if user can upload to shared folder (admin or has permission)
    if folder_type == 'shared' and not current_user.can_upload_to_shared:
        flash('Доступ запрещён. У вас нет прав для загрузки в общую папку.', 'error')
        return redirect(url_for('main.shared'))
    
    base_path = get_base_path(folder_type, current_app.config['UPLOAD_FOLDER'], current_user.username)
    rel_path = request.form.get('path', '')
    
    if 'file' not in request.files:
        flash('Файл не выбран.', 'error')
        return redirect(url_for('main.shared' if folder_type == 'shared' else 'main.personal'))
    
    file = request.files['file']
    if file.filename == '':
        flash('Файл не выбран.', 'error')
        return redirect(url_for('main.shared' if folder_type == 'shared' else 'main.personal'))
    
    filename = safe_filename(file.filename)
    if not filename:
        flash('Неверное имя файла.', 'error')
        return redirect(url_for('main.shared' if folder_type == 'shared' else 'main.personal'))
    
    upload_path = os.path.join(base_path, rel_path) if rel_path else base_path
    os.makedirs(upload_path, exist_ok=True)
    file.save(os.path.join(upload_path, filename))
    
    flash(f'Файл "{filename}" успешно загружён.', 'success')
    return redirect(url_for('main.' + folder_type, path=rel_path) if rel_path else url_for('main.' + folder_type))


@files_bp.route('/download')
@login_required
def download():
    """Handle file download."""
    folder_type = request.args.get('folder_type', 'personal')
    filename = request.args.get('filename', '')
    rel_path = request.args.get('path', '')
    
    if not filename:
        flash('Файл не указан.', 'error')
        return redirect(url_for('main.shared' if folder_type == 'shared' else 'main.personal'))
    
    base_path = get_base_path(folder_type, current_app.config['UPLOAD_FOLDER'], current_user.username)
    full_path, is_valid = validate_path_security(base_path, rel_path, filename)
    
    if not is_valid:
        flash('Доступ запрещён.', 'error')
        return redirect(url_for('main.shared' if folder_type == 'shared' else 'main.personal'))
    
    if not os.path.exists(full_path):
        flash('Файл не найден.', 'error')
        return redirect(url_for('main.shared' if folder_type == 'shared' else 'main.personal'))
    
    directory = os.path.dirname(full_path)
    return send_from_directory(directory, os.path.basename(full_path), as_attachment=True)


@files_bp.route('/preview')
@login_required
def preview():
    """Serve a file inline for preview (not as attachment)."""
    folder_type = request.args.get('folder_type', 'personal')
    filename = request.args.get('filename', '')
    rel_path = request.args.get('path', '')

    if not filename:
        flash('Файл не указан.', 'error')
        return redirect(url_for('main.shared' if folder_type == 'shared' else 'main.personal'))

    if not is_previewable(filename):
        flash('Предпросмотр недоступен для этого типа файлов.', 'error')
        return redirect(url_for('main.shared' if folder_type == 'shared' else 'main.personal'))

    base_path = get_base_path(folder_type, current_app.config['UPLOAD_FOLDER'], current_user.username)
    full_path, is_valid = validate_path_security(base_path, rel_path, filename)

    if not is_valid:
        flash('Доступ запрещён.', 'error')
        return redirect(url_for('main.shared' if folder_type == 'shared' else 'main.personal'))

    if not os.path.exists(full_path):
        flash('Файл не найден.', 'error')
        return redirect(url_for('main.shared' if folder_type == 'shared' else 'main.personal'))

    directory = os.path.dirname(full_path)
    return send_from_directory(directory, os.path.basename(full_path), as_attachment=False)


@files_bp.route('/delete', methods=['POST'])
@login_required
def delete():
    """Handle file/folder deletion."""
    folder_type = request.form.get('folder_type', 'personal')
    filename = request.form.get('filename', '')
    rel_path = request.form.get('path', '')
    is_dir = request.form.get('is_dir', 'false') == 'true'

    if folder_type == 'shared' and not current_user.can_upload_to_shared:
        flash('Доступ запрещён. У вас нет прав для удаления в общей папке.', 'error')
        return redirect(url_for('main.shared'))
    
    base_path = get_base_path(folder_type, current_app.config['UPLOAD_FOLDER'], current_user.username)
    full_path, is_valid = validate_path_security(base_path, rel_path, filename)
    
    if not is_valid:
        flash('Доступ запрещён.', 'error')
        return redirect(url_for('main.shared' if folder_type == 'shared' else 'main.personal'))
    
    if not os.path.exists(full_path):
        flash('Элемент не найден.', 'error')
        return redirect(url_for('main.shared' if folder_type == 'shared' else 'main.personal'))
    
    try:
        if is_dir:
            shutil.rmtree(full_path)
            flash(f'Папка "{filename}" удалена.', 'success')
        else:
            os.remove(full_path)
            flash(f'Файл "{filename}" удалён.', 'success')
    except Exception as e:
        flash(f'Ошибка при удалении: {str(e)}', 'error')
    
    return redirect(url_for('main.' + folder_type, path=rel_path) if rel_path else url_for('main.' + folder_type))


@files_bp.route('/mkdir', methods=['POST'])
@login_required
def mkdir():
    """Handle folder creation."""
    folder_type = request.form.get('folder_type', 'personal')
    folder_name = request.form.get('folder_name', '')
    rel_path = request.form.get('path', '')

    if folder_type == 'shared' and not current_user.can_upload_to_shared:
        flash('Доступ запрещён. У вас нет прав для создания папок в общей папке.', 'error')
        return redirect(url_for('main.shared'))
    
    if not folder_name:
        flash('Введите имя папки.', 'error')
        return redirect(url_for('main.shared' if folder_type == 'shared' else 'main.personal'))
    
    base_path = get_base_path(folder_type, current_app.config['UPLOAD_FOLDER'], current_user.username)
    parent_path = os.path.join(base_path, rel_path) if rel_path else base_path
    
    # Security check
    parent_path = os.path.normpath(parent_path)
    if not parent_path.startswith(base_path):
        flash('Доступ запрещён.', 'error')
        return redirect(url_for('main.shared' if folder_type == 'shared' else 'main.personal'))
    
    new_folder_path = os.path.join(parent_path, secure_filename(folder_name))
    
    if os.path.exists(new_folder_path):
        flash('Папка уже существует.', 'error')
    else:
        os.makedirs(new_folder_path, exist_ok=True)
        flash(f'Папка "{folder_name}" создана.', 'success')
    
    return redirect(url_for('main.' + folder_type, path=rel_path) if rel_path else url_for('main.' + folder_type))
