import asyncio
import logging
import threading
from functools import wraps

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class LazyInit:
    def __init__(self, init_function):
        self.init_function = init_function
        self.instance = None
        self.lock = threading.Lock()
        self.initialized = False

    def __call__(self, *args, **kwargs):
        if not self.initialized:
            with self.lock:
                if not self.initialized:
                    self.instance = self.init_function(*args, **kwargs)
                    self.initialized = True
        return self.instance


def threadsafe(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with threading.Lock():
            return func(*args, **kwargs)

    return wrapper


class FileHandler:
    def __init__(self, filename, mode="r"):
        self.filename = filename
        self.mode = mode
        self.file = None

    def __enter__(self):
        try:
            self.file = open(self.filename, self.mode)
            return self.file
        except FileNotFoundError:
            logging.error(f"File not found: {self.filename}")
            raise
        except IOError as e:
            logging.error(f"IOError opening file: {self.filename} - {e}")
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file:
            try:
                self.file.close()
            except IOError as e:
                logging.error(f"IOError closing file: {self.filename} - {e}")
            self.file = None


async def async_generator(data):
    for item in data:
        await asyncio.sleep(0)  # Simulate async operation
        yield item


@LazyInit
def expensive_initialization(param1, param2):
    logging.info(f"Performing expensive initialization with {param1} and {param2}")
    return {"result": f"Initialized with {param1} and {param2}"}


class MyClass:
    def __init__(self, value):
        self.value = value

    @threadsafe
    def modify_value(self, new_value):
        self.value = new_value
        logging.info(f"Value modified to: {new_value}")

    async def async_operation(self):
        try:
            async for item in async_generator(range(3)):
                logging.info(f"Processing item: {item}")
                await asyncio.sleep(0.1)
        except Exception as e:
            logging.error(f"Error in async operation: {e}")

    @staticmethod
    def static_method():
        logging.info("Static method called")

    @classmethod
    def class_method(cls):
        logging.info("Class method called")


if __name__ == "__main__":
    # Example usage
    try:
        with FileHandler("example.txt", "w") as f:
            f.write("Some content")
        with FileHandler("example.txt", "r") as f:
            content = f.read()
            logging.info(f"File content: {content}")
    except FileNotFoundError:
        pass  # Handled above in FileHandler
    except IOError:
        pass  # Handled above in FileHandler

    try:
        init_result = expensive_initialization("arg1", "arg2")
        logging.info(f"Initialization result: {init_result}")

        my_instance = MyClass(10)
        my_instance.modify_value(20)
        asyncio.run(my_instance.async_operation())
        MyClass.static_method()
        MyClass.class_method()

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
