"""
Tests for file/folder rename functionality.
"""
import os
from modules.utils import rename_item


class TestRenameItem:
    """Tests for the rename_item utility function."""

    def test_rename_file(self, app, shared_folder):
        """Test renaming a file."""
        old_path = os.path.join(shared_folder, 'test.txt')
        assert os.path.exists(old_path)

        success, message = rename_item(shared_folder, '', 'test.txt', 'renamed.txt')

        assert success
        assert 'renamed.txt' in message
        assert os.path.exists(os.path.join(shared_folder, 'renamed.txt'))
        assert not os.path.exists(old_path)

    def test_rename_folder(self, app, shared_folder):
        """Test renaming a folder."""
        old_path = os.path.join(shared_folder, 'test_folder')
        assert os.path.exists(old_path)

        success, message = rename_item(shared_folder, '', 'test_folder', 'renamed_folder')

        assert success
        assert 'renamed_folder' in message
        assert os.path.exists(os.path.join(shared_folder, 'renamed_folder'))
        assert not os.path.exists(old_path)

    def test_rename_file_in_subfolder(self, app, shared_folder):
        """Test renaming a file inside a subfolder."""
        # Create a file in the subfolder
        subfolder = os.path.join(shared_folder, 'test_folder')
        test_file = os.path.join(subfolder, 'inner.txt')
        with open(test_file, 'w') as f:
            f.write('inner content')

        success, message = rename_item(shared_folder, 'test_folder', 'inner.txt', 'renamed_inner.txt')

        assert success
        assert os.path.exists(os.path.join(subfolder, 'renamed_inner.txt'))
        assert not os.path.exists(test_file)

    def test_rename_nonexistent_file(self, app, shared_folder):
        """Test renaming a file that doesn't exist."""
        success, message = rename_item(shared_folder, '', 'nonexistent.txt', 'new.txt')

        assert not success
        assert 'не найден' in message.lower()

    def test_rename_to_existing_name(self, app, shared_folder):
        """Test renaming to a name that already exists."""
        # Create a second file
        second_file = os.path.join(shared_folder, 'second.txt')
        with open(second_file, 'w') as f:
            f.write('second')

        success, message = rename_item(shared_folder, '', 'test.txt', 'second.txt')

        assert not success
        assert 'уже существует' in message.lower()

    def test_rename_path_traversal_blocked(self, app, shared_folder):
        """Test that path traversal attacks are blocked."""
        success, message = rename_item(
            shared_folder,
            '',
            'test.txt',
            '../../etc/passwd.txt'
        )

        assert not success
        assert 'доступ запрещён' in message.lower()

    def test_rename_preserves_extension(self, app, shared_folder):
        """Test that renaming a file preserves the extension logic."""
        success, message = rename_item(shared_folder, '', 'test.txt', 'new_name.txt')

        assert success
        new_path = os.path.join(shared_folder, 'new_name.txt')
        assert os.path.exists(new_path)

    def test_rename_invalid_name(self, app, shared_folder):
        """Test renaming with an invalid (empty after sanitization) name."""
        success, message = rename_item(shared_folder, '', 'test.txt', '')

        assert not success


class TestRenameRoute:
    """Tests for the /rename route."""

    def test_admin_rename_file(self, admin_client, shared_folder):
        """Test admin can rename files in shared folder."""
        response = admin_client.post('/rename', data={
            'folder_type': 'shared',
            'old_name': 'test.txt',
            'new_name': 'admin_renamed.txt',
            'path': '',
            'is_dir': 'false'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert os.path.exists(os.path.join(shared_folder, 'admin_renamed.txt'))

    def test_admin_rename_folder(self, admin_client, shared_folder):
        """Test admin can rename folders in shared folder."""
        response = admin_client.post('/rename', data={
            'folder_type': 'shared',
            'old_name': 'test_folder',
            'new_name': 'admin_renamed_folder',
            'path': '',
            'is_dir': 'true'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert os.path.exists(os.path.join(shared_folder, 'admin_renamed_folder'))

    def test_user_cannot_rename_in_shared(self, user_client, shared_folder):
        """Test regular user cannot rename items in shared folder."""
        response = user_client.post('/rename', data={
            'folder_type': 'shared',
            'old_name': 'test.txt',
            'new_name': 'user_renamed.txt',
            'path': '',
            'is_dir': 'false'
        }, follow_redirects=True)

        assert response.status_code == 200
        # File should still exist with original name
        assert os.path.exists(os.path.join(shared_folder, 'test.txt'))

    def test_user_can_rename_in_personal(self, user_client, personal_folder):
        """Test user can rename items in their personal folder."""
        response = user_client.post('/rename', data={
            'folder_type': 'personal',
            'old_name': 'personal_test.txt',
            'new_name': 'user_renamed.txt',
            'path': '',
            'is_dir': 'false'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert os.path.exists(os.path.join(personal_folder, 'user_renamed.txt'))

    def test_rename_empty_name(self, admin_client, shared_folder):
        """Test renaming with empty new name is rejected."""
        response = admin_client.post('/rename', data={
            'folder_type': 'shared',
            'old_name': 'test.txt',
            'new_name': '',
            'path': '',
            'is_dir': 'false'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert os.path.exists(os.path.join(shared_folder, 'test.txt'))

    def test_unauthenticated_cannot_rename(self, client, shared_folder):
        """Test unauthenticated users cannot rename."""
        response = client.post('/rename', data={
            'folder_type': 'shared',
            'old_name': 'test.txt',
            'new_name': 'hacked.txt',
            'path': '',
            'is_dir': 'false'
        }, follow_redirects=True)

        # Should redirect to login
        assert response.status_code == 200
        assert os.path.exists(os.path.join(shared_folder, 'test.txt'))
