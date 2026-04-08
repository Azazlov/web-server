"""
FileShare Local v2.1 - Main Routes
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from modules.models import get_all_users
from modules.utils import (
    get_base_path, get_folder_contents, get_breadcrumbs, get_relative_path,
    search_files
)

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Root route - redirect to dashboard or login."""
    if current_user.is_authenticated:
        return redirect(url_for('main.personal'))
    return redirect(url_for('auth.login'))


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard - redirect to personal folder."""
    return redirect(url_for('main.personal'))


@main_bp.route('/shared')
@login_required
def shared():
    """View shared folder."""
    base_path = get_base_path('shared', current_app.config['UPLOAD_FOLDER'])
    rel_path = get_relative_path(base_path, request)
    
    if rel_path is None:
        flash('Неверный путь.', 'error')
        return redirect(url_for('main.shared'))
    
    items, current_path = get_folder_contents(base_path, rel_path)
    breadcrumbs = get_breadcrumbs(rel_path)
    
    return render_template('shared.html',
                         items=items,
                         current_path=current_path,
                         breadcrumbs=breadcrumbs)


@main_bp.route('/personal')
@login_required
def personal():
    """View personal folder."""
    base_path = get_base_path('personal', current_app.config['UPLOAD_FOLDER'], current_user.username)
    rel_path = get_relative_path(base_path, request)
    
    if rel_path is None:
        flash('Неверный путь.', 'error')
        return redirect(url_for('main.personal'))
    
    items, current_path = get_folder_contents(base_path, rel_path)
    breadcrumbs = get_breadcrumbs(rel_path)
    
    return render_template('personal.html',
                         items=items,
                         current_path=current_path,
                         breadcrumbs=breadcrumbs)


@main_bp.route('/search')
@login_required
def search():
    """Search for files and folders."""
    folder_type = request.args.get('folder_type', 'personal')
    query = request.args.get('q', '').strip()

    if not query:
        return render_template('search.html', folder_type=folder_type, query='', results=[])

    base_path = get_base_path(folder_type, current_app.config['UPLOAD_FOLDER'], current_user.username)
    if not base_path:
        flash('Неверный тип папки.', 'error')
        return redirect(url_for('main.personal'))

    results = search_files(base_path, query)

    return render_template('search.html', folder_type=folder_type, query=query, results=results)
