import pytest
import os
import sys
import shutil
from unittest.mock import patch, mock_open
from src.playground.refactor_system_implementeer_selfimprovement_squad import *

sys.path.append(os.getcwd())


class TestRefactorSystemImplementeerSelfimprovementSquad:
    """
    Test suite for the refactor_system_implementeer_selfimprovement_squad module.
    """

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, tmpdir):
        """
        Setup: create temporary working directory and files before each test.
        Teardown: remove temporary directory after each test.
        """
        self.tmpdir = tmpdir.strpath
        self.test_file = os.path.join(self.tmpdir, "test_file.txt")
        self.backup_dir = os.path.join(self.tmpdir, "backups")
        os.makedirs(self.backup_dir, exist_ok=True)

        # Create a dummy test file
        with open(self.test_file, "w") as f:
            f.write("This is a test file.")

        yield  # Run the test

        # Cleanup:  removed managed by tmpdir fixture

    def test_get_file_size_success(self):
        """Test get_file_size with a valid file."""
        size = get_file_size(self.test_file)
        assert isinstance(size, int)
        assert size > 0

    def test_get_file_size_file_not_found(self):
        """Test get_file_size with a non-existent file."""
        size = get_file_size(os.path.join(self.tmpdir, "nonexistent.txt"))
        assert size is None

    def test_get_file_size_error(self, tmpdir):
        """Test get_file_size with a file that causes an error (e.g., no permissions)."""
        # Create a file and then change permissions to prevent size retrieval.
        file_path = tmpdir.join("protected_file.txt")
        file_path.write("content")
        os.chmod(file_path.strpath, 0o000)  # Remove all permissions
        size = get_file_size(file_path.strpath)
        assert size is None

    def test_execute_command_success(self):
        """Test execute_command with a successful command."""
        return_code, stdout, stderr = execute_command(["ls", "-l", self.tmpdir])
        assert return_code == 0
        assert "test_file.txt" in stdout
        assert stderr == ""

    def test_execute_command_failure(self):
        """Test execute_command with a failing command."""
        return_code, stdout, stderr = execute_command(["nonexistent_command"])
        assert return_code != 0
        assert "Command not found" in stderr

    def test_create_directory_success(self):
        """Test create_directory when the directory doesn't exist."""
        new_dir = os.path.join(self.tmpdir, "new_dir")
        assert create_directory(new_dir) is True
        assert os.path.exists(new_dir)

    def test_create_directory_already_exists(self):
        """Test create_directory when the directory already exists."""
        new_dir = os.path.join(self.tmpdir, "new_dir")
        os.makedirs(new_dir, exist_ok=True)
        assert create_directory(new_dir) is True
        assert os.path.exists(new_dir)

    def test_create_directory_failure(self, tmpdir):
        """Test create_directory when directory creation fails (e.g., invalid path)."""
        invalid_dir = os.path.join(tmpdir.strpath, "invalid/dir")  # Invalid path
        assert create_directory(invalid_dir) is False

    def test_copy_file_success(self):
        """Test copy_file with a successful copy."""
        dst_file = os.path.join(self.tmpdir, "copy.txt")
        assert copy_file(self.test_file, dst_file) is True
        assert os.path.exists(dst_file)
        with open(self.test_file, "r") as f1, open(dst_file, "r") as f2:
            assert f1.read() == f2.read()

    def test_copy_file_failure(self, tmpdir):
        """Test copy_file with a failing copy (e.g., destination is a directory)."""
        dst_dir = self.tmpdir
        dst_file = os.path.join(dst_dir, "copy.txt")
        assert copy_file(self.test_file, dst_file) is True # create file.
        os.chmod(dst_file, 0o000) #make the new file not writeable.
        dst_file = os.path.join(dst_dir, "copy.txt")
        assert copy_file(self.test_file, dst_file) is False

    def test_delete_file_success(self):
        """Test delete_file with a successful deletion."""
        assert delete_file(self.test_file) is True
        assert not os.path.exists(self.test_file)

    def test_delete_file_not_found(self):
        """Test delete_file when the file does not exist."""
        assert delete_file(os.path.join(self.tmpdir, "nonexistent.txt")) is True

    def test_delete_file_failure(self, tmpdir):
        """Test delete_file when deletion fails (e.g., no permissions)."""
        file_path = tmpdir.join("protected_file.txt")
        file_path.write("content")
        os.chmod(file_path.strpath, 0o000)  # Remove all permissions
        assert delete_file(file_path.strpath) is False

    def test_read_file_success(self):
        """Test read_file with a successful read."""
        content = read_file(self.test_file)
        assert content == "This is a test file."

    def test_read_file_not_found(self):
        """Test read_file with a non-existent file."""
        content = read_file(os.path.join(self.tmpdir, "nonexistent.txt"))
        assert content is None

    def test_read_file_failure(self, tmpdir):
        """Test read_file when the read operation fails (e.g. no read permissions)."""
        file_path = tmpdir.join("protected_file.txt")
        file_path.write("content")
        os.chmod(file_path.strpath, 0o000)
        content = read_file(file_path.strpath)
        assert content is None

    def test_write_file_success(self):
        """Test write_file with a successful write."""
        new_content = "This is new content."
        assert write_file(self.test_file, new_content) is True
        with open(self.test_file, "r") as f:
            assert f.read() == new_content

    def test_write_file_failure(self, tmpdir):
        """Test write_file when the write operation fails (e.g., no write permissions)."""
        file_path = tmpdir.join("protected_file.txt")
        # create the file with write permission so the test file will be made.
        file_path.write("original content")
        os.chmod(file_path.strpath, 0o444) #remove write permission, but keep read
        assert write_file(file_path.strpath, "new content") is False

    def test_analyze_and_backup_file_success(self):
        """Test analyze_and_backup_file with a successful backup."""
        assert analyze_and_backup_file(self.test_file, self.backup_dir) is True
        backup_file = os.path.join(self.backup_dir, "test_file.txt.bak")
        assert os.path.exists(backup_file)
        with open(self.test_file, "r") as f1, open(backup_file, "r") as f2:
            assert f1.read() == f2.read()

    def test_analyze_and_backup_file_file_not_found(self):
        """Test analyze_and_backup_file when the file does not exist."""
        assert analyze_and_backup_file(
            os.path.join(self.tmpdir, "nonexistent.txt"), self.backup_dir
        ) is True  # Should return True because no error occurred, no backup needed

    def test_analyze_and_backup_file_backup_failure(self, tmpdir):
        """Test analyze_and_backup_file when backup fails."""
        # Create a file and make the backup directory read-only
        file_path = tmpdir.join("protected_file.txt")
        file_path.write("content")
        backup_dir = tmpdir.mkdir("readonly_backup")
        os.chmod(backup_dir.strpath, 0o444) #make read only
        assert analyze_and_backup_file(file_path.strpath, backup_dir.strpath) is False

    def test_process_file_content_success(self):
        """Test process_file_content with a successful replacement."""
        search_string = "test"
        replace_string = "replaced"
        assert process_file_content(self.test_file, search_string, replace_string) is True
        with open(self.test_file, "r") as f:
            assert "This is a replaced file." in f.read()

    def test_process_file_content_not_found(self):
        """Test process_file_content when the search string is not found."""
        search_string = "not_found"
        replace_string = "replaced"
        assert process_file_content(self.test_file, search_string, replace_string) is True
        with open(self.test_file, "r") as f:
            assert "This is a test file." in f.read()

    def test_process_file_content_read_failure(self, tmpdir):
        """Test process_file_content when the read operation fails."""
        file_path = tmpdir.join("protected_file.txt")
        file_path.write("original content")
        os.chmod(file_path.strpath, 0o000)
        assert process_file_content(file_path.strpath, "original", "new") is False

    def test_process_file_content_write_failure(self, tmpdir):
        """Test process_file_content when write operation fails."""
        file_path = tmpdir.join("protected_file.txt")
        file_path.write("original content")
        os.chmod(file_path.strpath, 0o444)  # Read-only
        assert process_file_content(file_path.strpath, "original", "new") is False

    def test_run_system_command_success(self):
        """Test run_system_command with a successful command."""
        return_code, stdout, stderr = run_system_command("ls -l", self.tmpdir)
        assert return_code == 0
        assert "test_file.txt" in stdout
        assert stderr == ""

    def test_run_system_command_failure(self):
        """Test run_system_command with a failing command."""
        return_code, stdout, stderr = run_system_command("nonexistent_command")
        assert return_code != 0
        assert "Command not found" in stderr

    def test_main_success(self):
        """Test main function with a successful run."""
        with patch("src.playground.refactor_system_implementeer_selfimprovement_squad.create_directory") as mock_create_dir, \
             patch("src.playground.refactor_system_implementeer_selfimprovement_squad.write_file") as mock_write_file, \
             patch("src.playground.refactor_system_implementeer_selfimprovement_squad.analyze_and_backup_file") as mock_backup, \
             patch("src.playground.refactor_system_implementeer_selfimprovement_squad.process_file_content") as mock_process, \
             patch("src.playground.refactor_system_implementeer_selfimprovement_squad.run_system_command") as mock_run_cmd, \
             patch("src.playground.refactor_system_implementeer_selfimprovement_squad.delete_file") as mock_delete_file:

            mock_create_dir.return_value = True
            mock_write_file.return_value = True
            mock_backup.return_value = True
            mock_process.return_value = True
            mock_run_cmd.return_value = (0, "stdout", "stderr")
            mock_delete_file.return_value = True

            assert main() == 0
            mock_create_dir.assert_called_once()
            mock_write_file.assert_called_once()
            mock_backup.assert_called_once()
            mock_process.assert_called_once()
            mock_run_cmd.assert_called_once()
            mock_delete_file.assert_called_once()

    def test_main_failure_create_dir(self):
        """Test main function failure due to create_directory."""
        with patch("src.playground.refactor_system_implementeer_selfimprovement_squad.create_directory") as mock_create_dir:
            mock_create_dir.return_value = False
            assert main() == 1

    def test_main_failure_write_file(self):
        """Test main function failure due to write_file."""
        with patch("src.playground.refactor_system_implementeer_selfimprovement_squad.create_directory") as mock_create_dir, \
                patch("src.playground.refactor_system_implementeer_selfimprovement_squad.write_file") as mock_write_file:
            mock_create_dir.return_value = True
            mock_write_file.return_value = False
            assert main() == 1

    def test_main_failure_backup(self):
        """Test main function failure due to analyze_and_backup_file."""
        with patch("src.playground.refactor_system_implementeer_selfimprovement_squad.create_directory") as mock_create_dir, \
                patch("src.playground.refactor_system_implementeer_selfimprovement_squad.write_file") as mock_write_file, \
                patch("src.playground.refactor_system_implementeer_selfimprovement_squad.analyze_and_backup_file") as mock_backup:
            mock_create_dir.return_value = True
            mock_write_file.return_value = True
            mock_backup.return_value = False
            assert main() == 1

    def test_main_failure_process_file_content(self):
        """Test main function failure due to process_file_content."""
        with patch("src.playground.refactor_system_implementeer_selfimprovement_squad.create_directory") as mock_create_dir, \
                patch("src.playground.refactor_system_implementeer_selfimprovement_squad.write_file") as mock_write_file, \
                patch("src.playground.refactor_system_implementeer_selfimprovement_squad.analyze_and_backup_file") as mock_backup, \
                patch("src.playground.refactor_system_implementeer_selfimprovement_squad.process_file_content") as mock_process:
            mock_create_dir.return_value = True
            mock_write_file.return_value = True
            mock_backup.return_value = True
            mock_process.return_value = False
            assert main() == 1

    def test_main_failure_system_command(self):
        """Test main function failure due to run_system_command."""
        with patch("src.playground.refactor_system_implementeer_selfimprovement_squad.create_directory") as mock_create_dir, \
                patch("src.playground.refactor_system_implementeer_selfimprovement_squad.write_file") as mock_write_file, \
                patch("src.playground.refactor_system_implementeer_selfimprovement_squad.analyze_and_backup_file") as mock_backup, \
                patch("src.playground.refactor_system_implementeer_selfimprovement_squad.process_file_content") as mock_process, \
                patch("src.playground.refactor_system_implementeer_selfimprovement_squad.run_system_command") as mock_run_cmd:
            mock_create_dir.return_value = True
            mock_write_file.return_value = True
            mock_backup.return_value = True
            mock_process.return_value = True
            mock_run_cmd.return_value = (1, "stdout", "stderr") # Simulate command failure
            assert main() == 1