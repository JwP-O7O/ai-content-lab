from loguru import logger

def add(x: float, y: float) -> float:
    """Adds two numbers."""
    return x + y

def subtract(x: float, y: float) -> float:
    """Subtracts two numbers."""
    return x - y

def multiply(x: float, y: float) -> float:
    """Multiplies two numbers."""
    return x * y

def divide(x: float, y: float) -> float:
    """Divides two numbers, handles ZeroDivisionError."""
    try:
        return x / y
    except ZeroDivisionError:
        logger.error("Division by zero error!")
        return float('inf')  # Or return None, or raise the exception again, depending on the desired behavior

def calculator():
    """Simple calculator with error handling."""
    while True:
        try:
            num1 = float(input("Enter first number: "))
            operator = input("Enter operator (+, -, *, /) or 'q' to quit: ")

            if operator == 'q':
                logger.info("Calculator exiting.")
                break

            num2 = float(input("Enter second number: "))

            if operator == '+':
                result = add(num1, num2)
            elif operator == '-':
                result = subtract(num1, num2)
            elif operator == '*':
                result = multiply(num1, num2)
            elif operator == '/':
                result = divide(num1, num2)
            else:
                logger.warning("Invalid operator.")
                continue

            logger.info(f"Result: {result}")

        except ValueError:
            logger.error("Invalid input. Please enter numbers only.")
        except Exception as e:
            logger.exception(f"An unexpected error occurred: {e}")  # Log the entire traceback.

if __name__ == "__main__":
    logger.info("Calculator started.")
    calculator()