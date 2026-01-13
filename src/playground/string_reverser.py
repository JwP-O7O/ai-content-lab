from loguru import logger


def reverse_string(text: str) -> str:
    """
    Reverses a string.

    Args:
        text: The string to reverse.

    Returns:
        The reversed string.

    Raises:
        TypeError: If the input is not a string.
    """
    try:
        if not isinstance(text, str):
            raise TypeError("Input must be a string.")
        return text[::-1]
    except TypeError as e:
        logger.error(f"TypeError: {e}")
        return ""  # Or handle the error in another appropriate way (e.g., raise it, return None)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return ""


if __name__ == "__main__":
    # Example usage
    test_string = "Hello, Phoenix OS!"
    reversed_string = reverse_string(test_string)
    logger.info(f"Original string: {test_string}")
    logger.info(f"Reversed string: {reversed_string}")

    # Test with a non-string input
    non_string_input = 123
    reversed_non_string = reverse_string(non_string_input)
    logger.info(f"Reversed non-string: {reversed_non_string}")