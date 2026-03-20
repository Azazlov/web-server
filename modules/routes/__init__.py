"""
FileShare Local v2.1 - Routes Package
"""
from .auth import auth_bp
from .main import main_bp
from .files import files_bp
from .admin import admin_bp

__all__ = ['auth_bp', 'main_bp', 'files_bp', 'admin_bp']
