"""
Manual test runner for rename functionality (no pytest dependency).
"""
import os
import sys
import tempfile
import shutil

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.utils import rename_item


def test_rename_file():
    """Test renaming a file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test file
        test_file = os.path.join(tmpdir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('test content')

        success, message = rename_item(tmpdir, '', 'test.txt', 'renamed.txt')

        assert success, f"Expected success, got: {message}"
        assert os.path.exists(os.path.join(tmpdir, 'renamed.txt')), "New file doesn't exist"
        assert not os.path.exists(test_file), "Old file still exists"
        print("  PASS: test_rename_file")


def test_rename_folder():
    """Test renaming a folder."""
    with tempfile.TemporaryDirectory() as tmpdir:
        folder = os.path.join(tmpdir, 'test_folder')
        os.makedirs(folder)

        success, message = rename_item(tmpdir, '', 'test_folder', 'renamed_folder')

        assert success, f"Expected success, got: {message}"
        assert os.path.exists(os.path.join(tmpdir, 'renamed_folder')), "New folder doesn't exist"
        assert not os.path.exists(folder), "Old folder still exists"
        print("  PASS: test_rename_folder")


def test_rename_in_subfolder():
    """Test renaming a file inside a subfolder."""
    with tempfile.TemporaryDirectory() as tmpdir:
        subfolder = os.path.join(tmpdir, 'sub')
        os.makedirs(subfolder)
        test_file = os.path.join(subfolder, 'inner.txt')
        with open(test_file, 'w') as f:
            f.write('inner')

        success, message = rename_item(tmpdir, 'sub', 'inner.txt', 'renamed_inner.txt')

        assert success, f"Expected success, got: {message}"
        assert os.path.exists(os.path.join(subfolder, 'renamed_inner.txt'))
        assert not os.path.exists(test_file)
        print("  PASS: test_rename_in_subfolder")


def test_rename_nonexistent():
    """Test renaming a file that doesn't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        success, message = rename_item(tmpdir, '', 'nonexistent.txt', 'new.txt')

        assert not success, "Should have failed"
        assert 'не найден' in message.lower()
        print("  PASS: test_rename_nonexistent")


def test_rename_to_existing():
    """Test renaming to a name that already exists."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file1 = os.path.join(tmpdir, 'file1.txt')
        file2 = os.path.join(tmpdir, 'file2.txt')
        for f in [file1, file2]:
            with open(f, 'w') as fh:
                fh.write('content')

        success, message = rename_item(tmpdir, '', 'file1.txt', 'file2.txt')

        assert not success, "Should have failed"
        assert 'уже существует' in message.lower()
        print("  PASS: test_rename_to_existing")


def test_rename_path_traversal_blocked():
    """Test that path traversal attacks are blocked."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('test')

        success, message = rename_item(tmpdir, '', 'test.txt', '../../etc/passwd.txt')

        assert not success, "Path traversal should be blocked"
        assert 'доступ запрещён' in message.lower()
        print("  PASS: test_rename_path_traversal_blocked")


def test_rename_empty_name():
    """Test renaming with empty new name."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('test')

        success, message = rename_item(tmpdir, '', 'test.txt', '')

        assert not success, "Empty name should be rejected"
        print("  PASS: test_rename_empty_name")


def test_rename_preserves_content():
    """Test that renaming preserves file content."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, 'original.txt')
        original_content = 'hello world content'
        with open(test_file, 'w') as f:
            f.write(original_content)

        rename_item(tmpdir, '', 'original.txt', 'renamed.txt')

        new_file = os.path.join(tmpdir, 'renamed.txt')
        with open(new_file, 'r') as f:
            assert f.read() == original_content
        print("  PASS: test_rename_preserves_content")


if __name__ == '__main__':
    print("Running rename functionality tests...\n")
    tests = [
        test_rename_file,
        test_rename_folder,
        test_rename_in_subfolder,
        test_rename_nonexistent,
        test_rename_to_existing,
        test_rename_path_traversal_blocked,
        test_rename_empty_name,
        test_rename_preserves_content,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"  FAIL: {test.__name__}: {e}")
            failed += 1

    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed")
    if failed == 0:
        print("All tests passed!")
    else:
        sys.exit(1)
