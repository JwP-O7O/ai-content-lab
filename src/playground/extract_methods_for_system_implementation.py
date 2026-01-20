from loguru import logger
import os
import time
import subprocess
import threading
import sys
from typing import List, Dict, Tuple, Callable

# Constants (moved for better organization)
UPDATE_SCRIPT_PATH = "/tmp/update_script.sh"  # Placeholder
REBOOT_COMMAND = "sudo reboot"
MAX_RETRIES = 3
RETRY_DELAY = 5
DEFAULT_SHELL = "/bin/bash"


def _execute_command(
    command: str, shell: bool = False, timeout: int = 60
) -> Tuple[int, str, str]:
    """Executes a shell command and captures output and error."""
    try:
        start_time = time.time()
        process = subprocess.Popen(
            command,
            shell=shell,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            executable=DEFAULT_SHELL,
        )

        stdout, stderr = process.communicate(timeout=timeout)
        end_time = time.time()
        execution_time = end_time - start_time

        stdout_str = stdout.decode("utf-8", errors="ignore").strip()
        stderr_str = stderr.decode("utf-8", errors="ignore").strip()
        return process.returncode, stdout_str, stderr_str, execution_time

    except subprocess.TimeoutExpired:
        process.kill()
        stdout, stderr = process.communicate()
        stdout_str = stdout.decode("utf-8", errors="ignore").strip()
        stderr_str = stderr.decode("utf-8", errors="ignore").strip()
        return -1, stdout_str, stderr_str, timeout
    except FileNotFoundError:
        return -1, "", f"Command not found: {command}", 0
    except Exception as e:
        return -1, "", f"An unexpected error occurred: {e}", 0


def _retry_command(
    command: Callable[[], Tuple[int, str, str, float]],
    retries: int = MAX_RETRIES,
    delay: int = RETRY_DELAY,
) -> Tuple[int, str, str, float]:
    """Retries a command if it fails."""
    for attempt in range(retries + 1):
        try:
            return command()
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed: {e}")
            if attempt == retries:
                logger.error(f"Command failed after {retries + 1} attempts.")
                raise  # Re-raise the exception after all retries
            time.sleep(delay)


def _write_update_script(script_content: str) -> bool:
    """Writes the update script to a temporary file."""
    try:
        with open(UPDATE_SCRIPT_PATH, "w") as f:
            f.write(script_content)
        os.chmod(UPDATE_SCRIPT_PATH, 0o755)
        return True
    except Exception as e:
        logger.error(f"Failed to write or chmod update script: {e}")
        return False


def _run_update_script() -> Tuple[int, str, str, float]:
    """Runs the update script and captures its output."""
    return _execute_command(f"sudo {UPDATE_SCRIPT_PATH}", shell=True)


def _reboot_system() -> Tuple[int, str, str, float]:
    """Reboots the system."""
    return _execute_command(REBOOT_COMMAND, shell=True)


def perform_system_update(
    update_script_content: str, reboot_after_update: bool = True
) -> bool:
    """
    Performs a system update using a provided script.

    Args:
        update_script_content: The content of the update script.
        reboot_after_update: Whether to reboot after the update.

    Returns:
        True if the update was (likely) successful, False otherwise.
    """
    try:
        if not _write_update_script(update_script_content):
            return False

        return_code, stdout, stderr, execution_time = _retry_command(_run_update_script)

        logger.info(f"Update script execution time: {execution_time:.2f} seconds")
        logger.info(f"Update script stdout: {stdout}")
        logger.info(f"Update script stderr: {stderr}")

        if return_code != 0:
            logger.error(
                f"Update script failed with code {return_code}.  See stderr for details."
            )
            return False

        if reboot_after_update:
            logger.info("Rebooting the system...")
            return_code, stdout, stderr, execution_time = _retry_command(_reboot_system)

            logger.info(f"Reboot command execution time: {execution_time:.2f} seconds")
            logger.info(f"Reboot command stdout: {stdout}")
            logger.info(f"Reboot command stderr: {stderr}")

            if return_code != 0:
                logger.error(f"Reboot failed with code {return_code}. Check stderr.")
                return False
        return True

    except Exception as e:
        logger.error(f"An unexpected error occurred during the update: {e}")
        return False


def is_process_running(process_name: str) -> bool:
    """Checks if a process is running."""
    try:
        command = f"pgrep {process_name}"
        return_code, stdout, stderr, _ = _execute_command(command, shell=True)
        return return_code == 0 and stdout.strip() != ""
    except Exception as e:
        logger.error(f"Error checking process: {e}")
        return False


def kill_process(process_name: str) -> bool:
    """Kills a process by name."""
    try:
        if not is_process_running(process_name):
            logger.info(f"Process {process_name} is not running.")
            return True

        command = f"pkill {process_name}"
        return_code, stdout, stderr, _ = _execute_command(command, shell=True)

        if return_code == 0:
            logger.info(f"Successfully killed process: {process_name}")
            return True
        else:
            logger.error(
                f"Failed to kill process {process_name}. Return code: {return_code}, stderr: {stderr}"
            )
            return False
    except Exception as e:
        logger.error(f"Error killing process: {e}")
        return False


def safely_remove_file(file_path: str) -> bool:
    """Safely removes a file, logging errors."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"File removed: {file_path}")
            return True
        else:
            logger.info(f"File does not exist: {file_path}")
            return True
    except Exception as e:
        logger.error(f"Failed to remove file {file_path}: {e}")
        return False


def execute_commands_in_parallel(
    commands: List[Tuple[str, bool, int]],
) -> List[Tuple[int, str, str]]:
    """Executes a list of commands in parallel using threads.

    Args:
        commands: A list of tuples, where each tuple contains:
            - command: The command to execute (str).
            - shell: Whether to execute the command in a shell (bool).
            - timeout: Timeout in seconds (int).

    Returns:
        A list of tuples, where each tuple contains:
            - return_code: The return code of the command (int).
            - stdout: The standard output of the command (str).
            - stderr: The standard error of the command (str).
    """
    results: List[Tuple[int, str, str]] = [
        (-2, "", "") for _ in commands
    ]  # Initialize with a distinct error code
    threads: List[threading.Thread] = []

    def _execute_command_wrapper(index: int, command: str, shell: bool, timeout: int):
        try:
            return_code, stdout, stderr, _ = _execute_command(command, shell, timeout)
            results[index] = (return_code, stdout, stderr)
        except Exception as e:
            logger.error(f"Error during parallel execution of command '{command}': {e}")
            results[index] = (-1, "", str(e))  # Capture the error

    for i, (command, shell, timeout) in enumerate(commands):
        thread = threading.Thread(
            target=_execute_command_wrapper, args=(i, command, shell, timeout)
        )
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    return results


def get_system_information() -> Dict[str, str]:
    """Gathers basic system information."""
    system_info: Dict[str, str] = {}
    try:
        _, system_info["kernel_version"], _, _ = _execute_command("uname -r")
        _, system_info["hostname"], _, _ = _execute_command("hostname")
        _, system_info["uptime"], _, _ = _execute_command("uptime -p")
    except Exception as e:
        logger.error(f"Failed to gather system information: {e}")
    return system_info