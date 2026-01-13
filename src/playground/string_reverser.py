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
        return ""
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return ""