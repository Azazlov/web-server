"""
FileShare Local v2.1 - Database Models Module
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User model for authentication and authorization."""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    role = db.Column(db.Text, default='user', nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    upload_blocked = db.Column(db.Boolean, default=False, nullable=False)
    can_upload_shared = db.Column(db.Boolean, default=False, nullable=False)
    
    def set_password(self, password):
        """Hash and set user password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password against hash."""
        return check_password_hash(self.password_hash, password)
    
    @property
    def is_admin(self):
        """Check if user is administrator."""
        return self.role == 'admin'
    
    @property
    def can_upload(self):
        """Check if user can upload files."""
        return not self.upload_blocked

    @property
    def can_upload_to_shared(self):
        """Check if user can upload files to shared folder."""
        return self.is_admin or self.can_upload_shared

    def __repr__(self):
        return f'<User {self.username}>'


def init_db(app):
    """Initialize database with app context."""
    db.init_app(app)
    with app.app_context():
        db.create_all()


def get_user_count():
    """Get total number of users."""
    return User.query.count()


def get_admin_count():
    """Get number of administrators."""
    return User.query.filter_by(role='admin').count()


def get_all_users():
    """Get all users from database."""
    return User.query.all()


def get_user_by_id(user_id):
    """Get user by ID."""
    return User.query.get(int(user_id))


def get_user_by_username(username):
    """Get user by username."""
    return User.query.filter_by(username=username).first()


def create_user(username, password, is_admin=False):
    """Create new user."""
    user = User(username=username, role='admin' if is_admin else 'user')
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


def delete_user(user_id):
    """Delete user by ID."""
    user = User.query.get(int(user_id))
    if user:
        db.session.delete(user)
        db.session.commit()
        return True
    return False


def toggle_user_upload_block(user_id):
    """Toggle user upload block status."""
    user = User.query.get(int(user_id))
    if user:
        user.upload_blocked = not user.upload_blocked
        db.session.commit()
        return user.upload_blocked
    return None


def toggle_user_shared_upload(user_id):
    """Toggle user shared folder upload permission."""
    user = User.query.get(int(user_id))
    if user:
        user.can_upload_shared = not user.can_upload_shared
        db.session.commit()
        return user.can_upload_shared
    return None


def migrate_database_schema():
    """Add missing columns to existing database tables."""
    from sqlalchemy import inspect

    inspector = inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns('users')]

    if 'upload_blocked' not in columns:
        print('Adding upload_blocked column to users table...')
        with db.engine.connect() as conn:
            conn.execute(db.text('ALTER TABLE users ADD COLUMN upload_blocked BOOLEAN DEFAULT 0'))
            conn.commit()
        print('Column upload_blocked added successfully!')

    if 'can_upload_shared' not in columns:
        print('Adding can_upload_shared column to users table...')
        with db.engine.connect() as conn:
            conn.execute(db.text('ALTER TABLE users ADD COLUMN can_upload_shared BOOLEAN DEFAULT 0'))
            conn.commit()
        print('Column can_upload_shared added successfully!')
