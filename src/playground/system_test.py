from loguru import logger
import os


def create_system_test_file(filepath: str, content: str) -> bool:
    """
    Creates a file with the specified content.

    Args:
        filepath: The path to the file to create.
        content: The content to write to the file.

    Returns:
        True if the file was created successfully, False otherwise.
    """
    try:
        with open(filepath, "w") as f:
            f.write(content)
        logger.info(f"File '{filepath}' created successfully.")
        return True
    except Exception as e:
        logger.error(f"Error creating file '{filepath}': {e}")
        return False


if __name__ == "__main__":
    filepath = "system_test.txt"
    content = "Verification Successful"
    if create_system_test_file(filepath, content):
        logger.success("System test file creation verification successful.")
    else:
        logger.error("System test file creation verification failed.")