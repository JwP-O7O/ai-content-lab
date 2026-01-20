import pytest
import os
import sys
import shutil
from unittest.mock import patch, mock_open
from io import StringIO

# Add the project root to the Python path
sys.path.append(os.getcwd())
from src.playground.refactor_system_implementeer_selfimprovement_squad import *


@pytest.fixture
def cleanup_files():
    """
    Fixture to clean up files created during tests.
    """

    def _cleanup(file_paths):
        for path in file_paths:
            if os.path.exists(path):
                try:
                    if os.path.isfile(path):
                        os.remove(path)
                    elif os.path.isdir(path):
                        shutil.rmtree(path)
                except OSError as e:
                    print(f"Error cleaning up {path}: {e}")  # Print to console
    yield _cleanup
    # Cleanup is done after each test (using the yielded function)


class TestRefactorSystemImplementeerSelfImprovementSquad:
    def test_get_file_size_existing_file(self, cleanup_files, tmpdir):
        """Test get_file_size with an existing file."""
        test_file = tmpdir.join("test_file.txt")
        test_file.write("test content")
        file_path = str(test_file)
        size = get_file_size(file_path)
        assert size == 12  # Assuming "test content" has 12 bytes
        cleanup_files()


    def test_get_file_size_non_existing_file(self):
        """Test get_file_size with a non-existing file."""
        size = get_file_size("non_existent_file.txt")
        assert size is None


    def test_get_file_size_invalid_path(self, tmpdir):
        """Test get_file_size with an invalid path (e.g., a directory)."""
        test_dir = tmpdir.mkdir("test_dir")
        path = str(test_dir)
        size = get_file_size(path)
        assert size is None


    def test_execute_command_success(self):
        """Test execute_command with a successful command."""
        return_code, stdout, stderr = execute_command(["echo", "hello"])
        assert return_code == 0
        assert "hello" in stdout
        assert stderr == ""


    def test_execute_command_failure(self):
        """Test execute_command with a failing command."""
        return_code, stdout, stderr = execute_command(["invalid_command"])
        assert return_code != 0
        assert stdout == ""
        assert "Command not found" in stderr


    def test_execute_command_with_cwd(self, tmpdir):
        """Test execute_command with cwd argument."""
        cwd = str(tmpdir)
        return_code, stdout, stderr = execute_command(["pwd"], cwd=cwd)
        assert return_code == 0
        assert cwd in stdout
        assert stderr == ""


    def test_execute_command_with_env(self):
        """Test execute_command with env argument."""
        env = {"TEST_VAR": "test_value"}
        return_code, stdout, stderr = execute_command(["env"], env=env)
        assert return_code == 0
        assert "TEST_VAR=test_value" in stdout  # Assuming 'env' command shows env vars
        assert stderr == ""


    def test_create_directory_success(self, cleanup_files, tmpdir):
        """Test create_directory with a new directory."""
        dir_path = str(tmpdir.join("new_dir"))
        assert create_directory(dir_path) is True
        assert os.path.exists(dir_path)
        cleanup_files([dir_path])

    def test_create_directory_already_exists(self, cleanup_files, tmpdir):
        """Test create_directory when the directory already exists."""
        dir_path = str(tmpdir.mkdir("existing_dir"))
        assert create_directory(dir_path) is True
        assert os.path.exists(dir_path)
        cleanup_files([dir_path])


    def test_copy_file_success(self, cleanup_files, tmpdir):
        """Test copy_file with a successful copy."""
        src_file = tmpdir.join("src_file.txt")
        src_file.write("source content")
        src_path = str(src_file)
        dst_path = str(tmpdir.join("dst_file.txt"))
        assert copy_file(src_path, dst_path) is True
        assert os.path.exists(dst_path)
        with open(dst_path, "r") as f:
            content = f.read()
        assert content == "source content"
        cleanup_files([src_path, dst_path])


    def test_copy_file_failure(self):
        """Test copy_file with a failing copy (source does not exist)."""
        assert copy_file("non_existent_file.txt", "dst.txt") is False

    def test_delete_file_success(self, cleanup_files, tmpdir):
        """Test delete_file with a successful deletion."""
        file_path = str(tmpdir.join("file_to_delete.txt"))
        open(file_path, "w").close()
        assert delete_file(file_path) is True
        assert not os.path.exists(file_path)
        cleanup_files([file_path])

    def test_delete_file_non_existent(self):
        """Test delete_file with a non-existent file."""
        assert delete_file("non_existent_file.txt") is True

    def test_read_file_success(self, cleanup_files, tmpdir):
        """Test read_file with a successful read."""
        file_path = str(tmpdir.join("read_file.txt"))
        with open(file_path, "w") as f:
            f.write("read content")
        content = read_file(file_path)
        assert content == "read content"
        cleanup_files([file_path])

    def test_read_file_non_existent(self):
        """Test read_file with a non-existent file."""
        content = read_file("non_existent_file.txt")
        assert content is None

    def test_write_file_success(self, cleanup_files, tmpdir):
        """Test write_file with a successful write."""
        file_path = str(tmpdir.join("write_file.txt"))
        assert write_file(file_path, "write content") is True
        with open(file_path, "r") as f:
            content = f.read()
        assert content == "write content"
        cleanup_files([file_path])

    def test_analyze_and_backup_file_success(self, cleanup_files, tmpdir):
        """Test analyze_and_backup_file with a successful backup."""
        file_path = str(tmpdir.join("file_to_backup.txt"))
        with open(file_path, "w") as f:
            f.write("original content")
        backup_dir = str(tmpdir.mkdir("backups"))
        assert analyze_and_backup_file(file_path, backup_dir) is True
        backup_file = os.path.join(backup_dir, "file_to_backup.txt.bak")
        assert os.path.exists(backup_file)
        with open(backup_file, "r") as f:
            backup_content = f.read()
        assert backup_content == "original content"
        cleanup_files([file_path, backup_dir])


    def test_analyze_and_backup_file_no_file(self, cleanup_files, tmpdir):
        """Test analyze_and_backup_file when the original file does not exist."""
        file_path = str(tmpdir.join("nonexistent_file.txt"))
        backup_dir = str(tmpdir.mkdir("backups"))
        assert analyze_and_backup_file(file_path, backup_dir) is True
        # Backup should not be created.
        backup_file = os.path.join(backup_dir, "nonexistent_file.txt.bak")
        assert not os.path.exists(backup_file)
        cleanup_files([backup_dir])

    def test_process_file_content_success(self, cleanup_files, tmpdir):
        """Test process_file_content with a successful replacement."""
        file_path = str(tmpdir.join("process_file.txt"))
        with open(file_path, "w") as f:
            f.write("This is the old_value.")
        assert process_file_content(file_path, "old_value", "new_value") is True
        with open(file_path, "r") as f:
            content = f.read()
        assert content == "This is the new_value."
        cleanup_files([file_path])


    def test_process_file_content_no_match(self, cleanup_files, tmpdir):
        """Test process_file_content when the search string is not found."""
        file_path = str(tmpdir.join("process_file_no_match.txt"))
        with open(file_path, "w") as f:
            f.write("This is the original content.")
        assert process_file_content(file_path, "nonexistent", "replacement") is True
        with open(file_path, "r") as f:
            content = f.read()
        assert content == "This is the original content."
        cleanup_files([file_path])

    def test_run_system_command_success(self):
        """Test run_system_command with a successful command."""
        return_code, stdout, stderr = run_system_command("echo hello")
        assert return_code == 0
        assert "hello" in stdout
        assert stderr == ""

    def test_run_system_command_failure(self):
        """Test run_system_command with a failing command."""
        return_code, stdout, stderr = run_system_command("invalid_command")
        assert return_code != 0
        assert stdout == ""
        assert "Command not found" in stderr

    def test_main_success(self, cleanup_files, tmpdir, caplog):
        """Test main function for successful execution."""
        # Create a dummy example file
        example_file_path = str(tmpdir.join("example.txt"))
        with open(example_file_path, "w") as f:
            f.write("This is the old_value in the example file.")

        # Patch the system command to avoid external dependency
        with patch(
            "src.playground.refactor_system_implementeer_selfimprovement_squad.execute_command"
        ) as mock_execute_command:
            mock_execute_command.return_value = (0, "ls output", "")
            return_code = main()
            assert return_code == 0
            assert "System command executed successfully." in caplog.text

            # Assertions for file operations
            assert os.path.exists(os.path.join("backups", "example.txt.bak"))
            with open(example_file_path, "r") as f:
                assert "new_value" in f.read()


            cleanup_files([example_file_path, "backups"])



    def test_main_failure_create_backup_dir(self, tmpdir, caplog):
        """Test main when creating the backup directory fails."""
        with patch("src.playground.refactor_system_implementeer_selfimprovement_squad.create_directory") as mock_create_directory:
            mock_create_directory.return_value = False
            return_code = main()
            assert return_code == 1
            assert "Failed to create backup directory." in caplog.text


    def test_main_failure_analyze_backup(self, tmpdir, caplog):
        """Test main when analyzing and backing up the file fails."""

        # Create the example file
        example_file_path = str(tmpdir.join("example.txt"))
        with open(example_file_path, "w") as f:
            f.write("This is the old_value in the example file.")

        with patch("src.playground.refactor_system_implementeer_selfimprovement_squad.analyze_and_backup_file") as mock_backup:
            mock_backup.return_value = False
            return_code = main()
            assert return_code == 1
            assert "Failed to analyze and backup file." in caplog.text
            cleanup_files([example_file_path, "backups"])


    def test_main_failure_process_file_content(self, tmpdir, caplog):
        """Test main when processing the file content fails."""
        # Create the example file
        example_file_path = str(tmpdir.join("example.txt"))
        with open(example_file_path, "w") as f:
            f.write("This is the old_value in the example file.")

        with patch("src.playground.refactor_system_implementeer_selfimprovement_squad.process_file_content") as mock_process_content:
            mock_process_content.return_value = False
            return_code = main()
            assert return_code == 1
            assert "Failed to process file content." in caplog.text
            cleanup_files([example_file_path, "backups"])


    def test_main_failure_system_command(self, tmpdir, caplog):
        """Test main when the system command fails."""
        # Create the example file
        example_file_path = str(tmpdir.join("example.txt"))
        with open(example_file_path, "w") as f:
            f.write("This is the old_value in the example file.")


        with patch("src.playground.refactor_system_implementeer_selfimprovement_squad.run_system_command") as mock_run_command:
            mock_run_command.return_value = (1, "stdout", "stderr")
            return_code = main()
            assert return_code == 1
            assert "System command failed" in caplog.text
            cleanup_files([example_file_path, "backups"])