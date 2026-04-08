"""
Pytest fixtures for FileShare Local tests.
"""
import os
import shutil
import tempfile
import pytest

from app import create_app
from modules.models import db, User
from modules.config import config as app_config


@pytest.fixture
def app():
    """Create application with test configuration."""
    # Create a temporary directory for test uploads
    test_upload_dir = tempfile.mkdtemp()

    app = create_app()

    # Override configuration for testing
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'UPLOAD_FOLDER': test_upload_dir,
        'SECRET_KEY': 'test-secret-key',
    })

    # Ensure upload directories exist
    os.makedirs(os.path.join(test_upload_dir, 'shared'), exist_ok=True)
    os.makedirs(os.path.join(test_upload_dir, 'users'), exist_ok=True)

    yield app

    # Cleanup
    shutil.rmtree(test_upload_dir, ignore_errors=True)


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a CLI runner."""
    return app.test_cli_runner()


@pytest.fixture
def admin_user(app):
    """Create an admin user."""
    with app.app_context():
        user = User(username='admin', role='admin')
        user.set_password('admin123')
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def regular_user(app):
    """Create a regular user."""
    with app.app_context():
        user = User(username='user1', role='user')
        user.set_password('user123')
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def admin_client(client, admin_user):
    """Create a test client logged in as admin."""
    with client.session_transaction() as sess:
        sess['user_id'] = admin_user.id
        sess['_fresh'] = True
    return client


@pytest.fixture
def user_client(client, regular_user):
    """Create a test client logged in as regular user."""
    with client.session_transaction() as sess:
        sess['user_id'] = regular_user.id
        sess['_fresh'] = True
    return client


@pytest.fixture
def shared_folder(app):
    """Create a shared folder with test files."""
    upload_folder = app.config['UPLOAD_FOLDER']
    shared_path = os.path.join(upload_folder, 'shared')
    os.makedirs(shared_path, exist_ok=True)

    # Create test files
    test_file = os.path.join(shared_path, 'test.txt')
    with open(test_file, 'w') as f:
        f.write('test content')

    # Create test subfolder
    subfolder = os.path.join(shared_path, 'test_folder')
    os.makedirs(subfolder, exist_ok=True)

    return shared_path


@pytest.fixture
def personal_folder(app, regular_user):
    """Create a personal folder for the regular user."""
    upload_folder = app.config['UPLOAD_FOLDER']
    personal_path = os.path.join(upload_folder, 'users', regular_user.username)
    os.makedirs(personal_path, exist_ok=True)

    # Create test files
    test_file = os.path.join(personal_path, 'personal_test.txt')
    with open(test_file, 'w') as f:
        f.write('personal content')

    # Create test subfolder
    subfolder = os.path.join(personal_path, 'personal_folder')
    os.makedirs(subfolder, exist_ok=True)

    return personal_path
