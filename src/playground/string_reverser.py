from loguru import logger


def reverse_string(text: str) -> str:
    """Reverses a given string.

    Args:
        text: The string to be reversed.

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
        return ""  # Or handle the error as appropriate for Phoenix OS.  Returning empty string is a simple fallback.
    except Exception as e:  # Catch any other unexpected errors
        logger.error(f"An unexpected error occurred: {e}")
        return ""


if __name__ == "__main__":
    # Example usage and testing
    test_string = "Hello, Phoenix OS!"
    reversed_string = reverse_string(test_string)
    logger.info(f"Original string: {test_string}")
    logger.info(f"Reversed string: {reversed_string}")

    # Test with a non-string input
    non_string_input = 12345
    reversed_non_string = reverse_string(non_string_input)
    logger.info(f"Reversed non-string input: {reversed_non_string}")