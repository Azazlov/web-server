"""
FileShare Local v2.1 - Main Application Entry Point

A local file sharing server with role-based access control.
"""
import os
from flask import Flask
from flask_login import LoginManager

from modules.config import config
from modules.models import db, User, migrate_database_schema
from modules.utils import ensure_upload_dirs, migrate_user_folders
from modules.routes import auth_bp, main_bp, files_bp, admin_bp


def create_app():
    """Application factory for creating Flask app instance."""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = config.max_upload_size_bytes
    
    # Load additional config from file
    app.config['SERVER_PORT'] = config.server_port
    app.config['ALLOW_REGISTRATION'] = config.allow_registration
    app.config['DEBUG_MODE'] = config.debug_mode
    
    # Initialize extensions
    db.init_app(app)
    
    # Initialize login manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Custom Jinja2 filter
    @app.template_filter('dirname')
    def dirname_filter(path):
        import os
        return os.path.dirname(path)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(files_bp)
    app.register_blueprint(admin_bp)
    
    # Initialize database and folders
    with app.app_context():
        db.create_all()
        migrate_database_schema()
        ensure_upload_dirs(app.config['UPLOAD_FOLDER'])
        migrate_user_folders(app.config['UPLOAD_FOLDER'])
    
    return app


# Create app instance
app = create_app()


if __name__ == '__main__':
    # Run on configured port (requires admin/sudo privileges for port 80)
    port = config.server_port
    debug = config.debug_mode
    app.run(host='0.0.0.0', port=port, debug=debug)
