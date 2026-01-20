from loguru import logger
import os
import shutil
import subprocess
import sys
from typing import List, Optional, Tuple, Dict


def get_file_size(filepath: str) -> Optional[int]:
    """
    Gets the size of a file in bytes.

    Args:
        filepath: The path to the file.

    Returns:
        The file size in bytes, or None if the file does not exist or an error occurs.
    """
    try:
        if os.path.exists(filepath) and os.path.isfile(filepath):
            return os.path.getsize(filepath)
        else:
            logger.warning(f"File not found or not a file: {filepath}")
            return None
    except OSError as e:
        logger.error(f"Error getting file size: {e}")
        return None


def execute_command(
    command: List[str], cwd: Optional[str] = None, env: Optional[Dict] = None
) -> Tuple[int, str, str]:
    """
    Executes a shell command.

    Args:
        command: The command to execute (as a list of strings).
        cwd: The current working directory.
        env: Environment variables to set.

    Returns:
        A tuple containing the return code, stdout, and stderr.
    """
    try:
        process = subprocess.Popen(
            command,
            cwd=cwd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,  # Important for decoding output as text
        )
        stdout, stderr = process.communicate()
        return_code = process.returncode
        return return_code, stdout, stderr
    except FileNotFoundError:
        logger.error(f"Command not found: {command[0]}")
        return 1, "", ""
    except Exception as e:
        logger.error(f"Error executing command: {e}")
        return 1, "", ""


def create_directory(path: str) -> bool:
    """
    Creates a directory if it doesn't exist.

    Args:
        path: The path to the directory.

    Returns:
        True if the directory was created or already exists, False otherwise.
    """
    try:
        if not os.path.exists(path):
            os.makedirs(path)
            logger.info(f"Created directory: {path}")
        return True
    except OSError as e:
        logger.error(f"Error creating directory: {e}")
        return False


def copy_file(src: str, dst: str) -> bool:
    """
    Copies a file from source to destination.

    Args:
        src: The source file path.
        dst: The destination file path.

    Returns:
        True if the file was copied successfully, False otherwise.
    """
    try:
        shutil.copy2(src, dst)
        logger.info(f"Copied file from {src} to {dst}")
        return True
    except OSError as e:
        logger.error(f"Error copying file: {e}")
        return False


def delete_file(filepath: str) -> bool:
    """
    Deletes a file.

    Args:
        filepath: The path to the file.

    Returns:
        True if the file was deleted successfully, False otherwise.
    """
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            logger.info(f"Deleted file: {filepath}")
            return True
        else:
            logger.warning(f"File not found for deletion: {filepath}")
            return True  # Consider it successful if the file wasn't there to begin with
    except OSError as e:
        logger.error(f"Error deleting file: {e}")
        return False


def read_file(filepath: str) -> Optional[str]:
    """
    Reads the content of a file.

    Args:
        filepath: The path to the file.

    Returns:
        The content of the file as a string, or None if an error occurs.
    """
    try:
        with open(filepath, "r") as f:
            content = f.read()
            return content
    except FileNotFoundError:
        logger.warning(f"File not found: {filepath}")
        return None
    except IOError as e:
        logger.error(f"Error reading file: {e}")
        return None


def write_file(filepath: str, content: str) -> bool:
    """
    Writes content to a file.

    Args:
        filepath: The path to the file.
        content: The content to write.

    Returns:
        True if the file was written successfully, False otherwise.
    """
    try:
        with open(filepath, "w") as f:
            f.write(content)
            logger.info(f"Wrote to file: {filepath}")
            return True
    except IOError as e:
        logger.error(f"Error writing to file: {e}")
        return False


def analyze_and_backup_file(filepath: str, backup_dir: str) -> bool:
    """
    Analyzes a file, creates a backup if it exists, and logs the process.

    Args:
        filepath: The path to the file to analyze.
        backup_dir: The directory to store backups.

    Returns:
        True if the analysis and backup (if needed) were successful, False otherwise.
    """
    if not os.path.exists(filepath):
        logger.warning(f"File does not exist: {filepath}")
        return True  # Consider it successful as there's nothing to back up

    file_size = get_file_size(filepath)
    if file_size is None:
        return False  # Failed to get file size

    logger.info(f"Analyzing file: {filepath}, Size: {file_size} bytes")

    backup_filepath = os.path.join(backup_dir, os.path.basename(filepath) + ".bak")
    if os.path.exists(filepath):
        if not copy_file(filepath, backup_filepath):
            logger.error(f"Failed to create backup for {filepath}")
            return False
        logger.info(f"Created backup: {backup_filepath}")
    else:
        logger.warning(f"File {filepath} does not exist, no backup needed.")
    return True


def process_file_content(
    filepath: str, search_string: str, replace_string: str
) -> bool:
    """
    Reads a file, replaces a string, and writes the modified content back.

    Args:
        filepath: The path to the file.
        search_string: The string to search for.
        replace_string: The string to replace with.

    Returns:
        True if the operation was successful, False otherwise.
    """
    file_content = read_file(filepath)
    if file_content is None:
        logger.error(f"Failed to read file: {filepath}")
        return False

    if search_string in file_content:
        new_content = file_content.replace(search_string, replace_string)
        if not write_file(filepath, new_content):
            logger.error(f"Failed to write to file: {filepath}")
            return False
        logger.info(f"Replaced '{search_string}' with '{replace_string}' in {filepath}")
    else:
        logger.info(f"Search string '{search_string}' not found in {filepath}")
    return True


def run_system_command(
    command: str,
    working_directory: str = ".",
    environment_variables: Optional[Dict] = None,
) -> Tuple[int, str, str]:
    """
    Runs a shell command and returns the return code, stdout, and stderr.

    Args:
        command: The shell command to run.
        working_directory: The working directory for the command.
        environment_variables: Optional environment variables to set.

    Returns:
        A tuple containing the return code, stdout, and stderr.
    """
    command_list = command.split()
    return execute_command(
        command_list, cwd=working_directory, env=environment_variables
    )


def main():
    """
    Main function to demonstrate file operations, backups, and command execution.
    """
    # Configuration
    target_file = "example.txt"
    backup_directory = "backups"
    search_term = "old_value"
    replace_term = "new_value"
    system_command = "ls -l"

    # --- Directory Operations ---
    if not create_directory(backup_directory):
        logger.error("Failed to create backup directory.")
        return 1

    # --- File Operations & Backups ---
    # Create a dummy file if it doesn't exist
    if not os.path.exists(target_file):
        if not write_file(target_file, "This is the old_value in the example file."):
            logger.error("Failed to create example file.")
            return 1

    if not analyze_and_backup_file(target_file, backup_directory):
        logger.error("Failed to analyze and backup file.")
        return 1

    # --- File Content Replacement ---
    if not process_file_content(target_file, search_term, replace_term):
        logger.error("Failed to process file content.")
        return 1

    # --- System Command Execution ---
    return_code, stdout, stderr = run_system_command(system_command)

    logger.info(f"System command output: \nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}")
    if return_code != 0:
        logger.error(f"System command failed with return code {return_code}")
        return return_code
    else:
        logger.info("System command executed successfully.")

    # --- Cleanup ---
    if delete_file(target_file):
        logger.info(f"Deleted {target_file}")

    return 0  # Success


if __name__ == "__main__":
    sys.exit(main())