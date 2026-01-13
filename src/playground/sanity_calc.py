from loguru import logger

def add(x: float, y: float) -> float:
    """Voegt twee getallen bij elkaar op."""
    return x + y

def subtract(x: float, y: float) -> float:
    """Trekt een getal van een ander getal af."""
    return x - y

def multiply(x: float, y: float) -> float:
    """Vermenigvuldigt twee getallen."""
    return x * y

def divide(x: float, y: float) -> float:
    """Deelt een getal door een ander getal, met error handling voor delen door nul."""
    try:
        result = x / y
        return result
    except ZeroDivisionError:
        logger.error("Fout: Delen door nul is niet toegestaan.")
        return float('inf')  # Of een andere waarde die je wilt retourneren bij een fout

def main():
    """Hoofdprogramma voor de calculator."""
    try:
        num1 = float(input("Voer het eerste getal in: "))
        num2 = float(input("Voer het tweede getal in: "))
        operator = input("Voer de operator (+, -, *, /) in: ")

        if operator == '+':
            result = add(num1, num2)
            logger.info(f"Resultaat: {num1} + {num2} = {result}")
        elif operator == '-':
            result = subtract(num1, num2)
            logger.info(f"Resultaat: {num1} - {num2} = {result}")
        elif operator == '*':
            result = multiply(num1, num2)
            logger.info(f"Resultaat: {num1} * {num2} = {result}")
        elif operator == '/':
            result = divide(num1, num2)
            logger.info(f"Resultaat: {num1} / {num2} = {result}")
        else:
            logger.error("Ongeldige operator.")
    except ValueError:
        logger.error("Fout: Ongeldige invoer.  Zorg ervoor dat je getallen invoert.")
    except Exception as e:
        logger.error(f"Er is een onverwachte fout opgetreden: {e}")

if __name__ == "__main__":
    main()