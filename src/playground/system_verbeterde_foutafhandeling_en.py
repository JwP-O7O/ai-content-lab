import random
import contextlib
import time

class Resource:
    def __init__(self, value):
        self.value = value
        self.is_open = False

    def open(self):
        if not self.is_open:
            print(f"Opening resource with value: {self.value}")
            self.is_open = True
        else:
            print("Resource already open.")

    def use(self):
        if self.is_open:
            try:
                result = random.randint(1, 10) * self.value
                print(f"Using resource with value {self.value}, result: {result}")
                return result
            except Exception as e:
                print(f"Error during use: {e}")
                raise
        else:
            raise ValueError("Resource not open")

    def close(self):
        if self.is_open:
            print(f"Closing resource with value: {self.value}")
            self.is_open = False
        else:
            print("Resource already closed.")


class ResourceContextManager:
    def __init__(self, value):
        self.resource = Resource(value)

    def __enter__(self):
        try:
            self.resource.open()
            return self.resource
        except Exception as e:
            print(f"Error opening resource: {e}")
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.resource.close()
        except Exception as e:
            print(f"Error closing resource: {e}")
            pass # Suppress closing errors

def main():
    try:
        with ResourceContextManager(5) as resource:
            result = resource.use()
            print(f"Result in main: {result}")
            if random.random() < 0.2:
                raise ValueError("Simulated error during use.")
    except ValueError as e:
        print(f"Caught an error in main: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    try:
         with ResourceContextManager(10) as resource:
             resource.use()
             time.sleep(0.1)
             if random.random() < 0.1:
                raise ZeroDivisionError("Simulated division by zero")

    except ZeroDivisionError as e:
        print(f"Caught a zero division error: {e}")
    except Exception as e:
         print(f"Unexpected error: {e}")


    print("Program finished.")


if __name__ == "__main__":
    main()