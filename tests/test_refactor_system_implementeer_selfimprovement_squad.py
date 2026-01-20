import pytest
import os
import sys
import shutil
from unittest.mock import patch, mock_open
from src.playground.refactor_system_implementeer_selfimprovement_squad import *

sys.path.append(os.getcwd())


@pytest.fixture
def cleanup():
    """Fixture to clean up created files and directories after each test."""
    yield
    # Clean up after each test
    for filename in ["example.txt", "example.txt.bak"]:
        if os.path.exists(filename):
            os.remove(filename)
    if os.path.exists("backups"):
        shutil.rmtree("backups")
    if os.path.exists("test_dir"):
        shutil.rmtree("test_dir")
    if os.path.exists("test_file"):
        os.remove("test_file")
    if os.path.exists("another_file.txt"):
        os.remove("another_file.txt")


def test_get_file_size_existing_file(cleanup):
    # Arrange
    filepath = "example.txt"
    content = "test content"
    with open(filepath, "w") as f:
        f.write(content)

    # Act
    size = get_file_size(filepath)

    # Assert
    assert size == len(content)


def test_get_file_size_non_existing_file(cleanup):
    # Arrange
    filepath = "non_existent_file.txt"

    # Act
    size = get_file_size(filepath)

    # Assert
    assert size is None


def test_execute_command_successful():
    # Arrange
    command = ["echo", "hello"]

    # Act
    return_code, stdout, stderr = execute_command(command)

    # Assert
    assert return_code == 0
    assert stdout.strip() == "hello"
    assert stderr == ""


def test_execute_command_failing():
    # Arrange
    command = ["nonexistentcommand"]

    # Act
    return_code, stdout, stderr = execute_command(command)

    # Assert
    assert return_code != 0
    assert stdout == ""
    assert "Command not found" in stderr


def test_create_directory_success(cleanup):
    # Arrange
    path = "test_dir"

    # Act
    success = create_directory(path)

    # Assert
    assert success is True
    assert os.path.exists(path)


def test_create_directory_already_exists(cleanup):
    # Arrange
    path = "test_dir"
    os.makedirs(path)

    # Act
    success = create_directory(path)

    # Assert
    assert success is True
    assert os.path.exists(path)


def test_copy_file_success(cleanup):
    # Arrange
    src = "test_file"
    dst = "test_file_copy"
    with open(src, "w") as f:
        f.write("test content")

    # Act
    success = copy_file(src, dst)

    # Assert
    assert success is True
    assert os.path.exists(dst)
    assert get_file_size(dst) == get_file_size(src)
    os.remove(src)
    os.remove(dst)


def test_copy_file_failure(cleanup):
    # Arrange
    src = "non_existent_file"
    dst = "test_file_copy"

    # Act
    success = copy_file(src, dst)

    # Assert
    assert success is False
    assert not os.path.exists(dst)


def test_delete_file_success(cleanup):
    # Arrange
    filepath = "test_file"
    with open(filepath, "w") as f:
        f.write("test content")

    # Act
    success = delete_file(filepath)

    # Assert
    assert success is True
    assert not os.path.exists(filepath)


def test_delete_file_non_existent_file(cleanup):
    # Arrange
    filepath = "non_existent_file"

    # Act
    success = delete_file(filepath)

    # Assert
    assert success is True  # Should still return True, as the intent was achieved
    assert not os.path.exists(filepath)


def test_read_file_success(cleanup):
    # Arrange
    filepath = "test_file"
    content = "test content"
    with open(filepath, "w") as f:
        f.write(content)

    # Act
    result = read_file(filepath)

    # Assert
    assert result == content


def test_read_file_failure(cleanup):
    # Arrange
    filepath = "non_existent_file"

    # Act
    result = read_file(filepath)

    # Assert
    assert result is None


def test_write_file_success(cleanup):
    # Arrange
    filepath = "test_file"
    content = "test content"

    # Act
    success = write_file(filepath, content)

    # Assert
    assert success is True
    with open(filepath, "r") as f:
        assert f.read() == content


def test_write_file_failure(cleanup):
    # Arrange
    filepath = "/path/to/nonexistent/file"  # Assuming a path that is unlikely to exist.
    content = "test content"

    # Act
    success = write_file(filepath, content)

    # Assert
    assert success is False


def test_analyze_and_backup_file_success(cleanup):
    # Arrange
    filepath = "example.txt"
    backup_dir = "backups"
    content = "test content"
    os.makedirs(backup_dir, exist_ok=True)
    with open(filepath, "w") as f:
        f.write(content)

    # Act
    success = analyze_and_backup_file(filepath, backup_dir)

    # Assert
    assert success is True
    assert os.path.exists(os.path.join(backup_dir, "example.txt.bak"))
    assert get_file_size(filepath) == get_file_size(os.path.join(backup_dir, "example.txt.bak"))


def test_analyze_and_backup_file_no_file(cleanup):
    # Arrange
    filepath = "non_existent_file.txt"
    backup_dir = "backups"
    os.makedirs(backup_dir, exist_ok=True)

    # Act
    success = analyze_and_backup_file(filepath, backup_dir)

    # Assert
    assert success is True
    assert not os.path.exists(os.path.join(backup_dir, "non_existent_file.txt.bak"))


def test_analyze_and_backup_file_size_error(cleanup):
    # Arrange
    filepath = "example.txt"
    backup_dir = "backups"
    os.makedirs(backup_dir, exist_ok=True)

    with patch('src.playground.refactor_system_implementeer_selfimprovement_squad.get_file_size') as mock_get_file_size:
        mock_get_file_size.return_value = None  # Simulate an error getting the file size
        with open(filepath, "w") as f:
            f.write("test")

        # Act
        success = analyze_and_backup_file(filepath, backup_dir)

        # Assert
        assert success is False
        assert not os.path.exists(os.path.join(backup_dir, "example.txt.bak"))


def test_process_file_content_success(cleanup):
    # Arrange
    filepath = "example.txt"
    search_string = "old"
    replace_string = "new"
    content = "This is the old value."
    with open(filepath, "w") as f:
        f.write(content)

    # Act
    success = process_file_content(filepath, search_string, replace_string)

    # Assert
    assert success is True
    with open(filepath, "r") as f:
        assert f.read() == "This is the new value."


def test_process_file_content_no_search_string(cleanup):
    # Arrange
    filepath = "example.txt"
    search_string = "not_in_file"
    replace_string = "new"
    content = "This is the old value."
    with open(filepath, "w") as f:
        f.write(content)

    # Act
    success = process_file_content(filepath, search_string, replace_string)

    # Assert
    assert success is True
    with open(filepath, "r") as f:
        assert f.read() == content  # Content should remain unchanged


def test_process_file_content_read_failure(cleanup):
    # Arrange
    filepath = "non_existent_file.txt"
    search_string = "old"
    replace_string = "new"

    # Act
    success = process_file_content(filepath, search_string, replace_string)

    # Assert
    assert success is False


def test_run_system_command_success():
    # Arrange
    command = "echo hello"

    # Act
    return_code, stdout, stderr = run_system_command(command)

    # Assert
    assert return_code == 0
    assert stdout.strip() == "hello"
    assert stderr == ""


def test_run_system_command_failure():
    # Arrange
    command = "nonexistentcommand"

    # Act
    return_code, stdout, stderr = run_system_command(command)

    # Assert
    assert return_code != 0
    assert stdout == ""
    assert "nonexistentcommand" in stderr or "Command not found" in stderr # different systems may have different error messages


def test_run_system_command_with_working_directory(cleanup):
    # Arrange
    os.makedirs("test_dir", exist_ok=True)
    command = "pwd"
    expected_output = os.path.abspath("test_dir") #pwd will return the current working directory
    # Act
    return_code, stdout, stderr = run_system_command(command, working_directory="test_dir")

    # Assert
    assert return_code == 0
    assert stdout.strip() == expected_output
    assert stderr == ""


def test_run_system_command_with_environment_variables():
    # Arrange
    command = "echo $TEST_VAR"
    env_vars = {"TEST_VAR": "test_value"}

    # Act
    return_code, stdout, stderr = run_system_command(command, environment_variables=env_vars)

    # Assert
    assert return_code == 0
    assert stdout.strip() == "test_value"
    assert stderr == ""


def test_main_success(cleanup):
    # Arrange
    with patch("src.playground.refactor_system_implementeer_selfimprovement_squad.logger.info") as mock_info, \
         patch("src.playground.refactor_system_implementeer_selfimprovement_squad.logger.error") as mock_error:
        # Act
        result = main()

        # Assert
        assert result == 0
        assert os.path.exists("example.txt") == False
        assert os.path.exists("backups/example.txt.bak") == True
        assert mock_error.call_count == 0  # No errors expected
        assert mock_info.call_count > 0  # Info calls expected


def test_main_directory_creation_failure(cleanup):
    # Arrange
    with patch("src.playground.refactor_system_implementeer_selfimprovement_squad.create_directory") as mock_create_dir, \
         patch("src.playground.refactor_system_implementeer_selfimprovement_squad.logger.error") as mock_error:

        mock_create_dir.return_value = False

        # Act
        result = main()

        # Assert
        assert result == 1
        mock_error.assert_called_with("Failed to create backup directory.")


def test_main_file_creation_failure(cleanup):
    # Arrange
    with patch("src.playground.refactor_system_implementeer_selfimprovement_squad.write_file") as mock_write_file, \
         patch("src.playground.refactor_system_implementeer_selfimprovement_squad.logger.error") as mock_error:

        mock_write_file.return_value = False

        # Act
        result = main()

        # Assert
        assert result == 1
        mock_error.assert_called_with("Failed to create example file.")


def test_main_backup_failure(cleanup):
    # Arrange
    with patch("src.playground.refactor_system_implementeer_selfimprovement_squad.analyze_and_backup_file") as mock_backup, \
         patch("src.playground.refactor_system_implementeer_selfimprovement_squad.logger.error") as mock_error:

        mock_backup.return_value = False

        # Act
        result = main()

        # Assert
        assert result == 1
        mock_error.assert_called_with("Failed to analyze and backup file.")


def test_main_process_content_failure(cleanup):
    # Arrange
    with patch("src.playground.refactor_system_implementeer_selfimprovement_squad.process_file_content") as mock_process, \
         patch("src.playground.refactor_system_implementeer_selfimprovement_squad.logger.error") as mock_error:

        mock_process.return_value = False

        # Act
        result = main()

        # Assert
        assert result == 1
        mock_error.assert_called_with("Failed to process file content.")


def test_main_command_execution_failure(cleanup):
    # Arrange
    with patch("src.playground.refactor_system_implementeer_selfimprovement_squad.run_system_command") as mock_run_command, \
         patch("src.playground.refactor_system_implementeer_selfimprovement_squad.logger.error") as mock_error:

        mock_run_command.return_value = (1, "", "error")  # Simulate command failure

        # Act
        result = main()

        # Assert
        assert result == 1
        mock_error.assert_called_with(f"System command failed with return code 1")