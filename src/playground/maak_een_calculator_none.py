class Calculator:
    def __init__(self):
        pass

    def add(self, x, y):
        if x is None or y is None:
            return None
        return x + y

    def subtract(self, x, y):
        if x is None or y is None:
            return None
        return x - y

    def multiply(self, x, y):
        if x is None or y is None:
            return None
        return x * y

    def divide(self, x, y):
        if x is None or y is None:
            return None
        if y == 0:
            return None
        return x / y

    def calculate(self, operation, x, y):
        if operation == "add":
            return self.add(x, y)
        elif operation == "subtract":
            return self.subtract(x, y)
        elif operation == "multiply":
            return self.multiply(x, y)
        elif operation == "divide":
            return self.divide(x, y)
        else:
            return None

if __name__ == '__main__':
    calc = Calculator()
    print(calc.add(5, 3))
    print(calc.subtract(10, 4))
    print(calc.multiply(2, 6))
    print(calc.divide(8, 2))
    print(calc.divide(5, 0))
    print(calc.add(None, 5))
    print(calc.calculate("add", 7, 2))
    print(calc.calculate("invalid", 7, 2))