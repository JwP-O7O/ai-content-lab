import sqlite3
import functools
import logging
from contextlib import contextmanager

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

DATABASE_NAME = "activity.db"


def log_activity(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            log_message = f"Function '{func.__name__}' called successfully with args: {args} and kwargs: {kwargs}"
            _log_activity(func.__name__, "success", log_message)
            return result
        except Exception as e:
            error_message = f"Function '{func.__name__}' failed with args: {args} and kwargs: {kwargs}. Error: {str(e)}"
            _log_activity(func.__name__, "error", error_message)
            raise

    return wrapper


@contextmanager
def database_connection():
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        yield conn
        conn.commit()
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        logging.error(f"Database error: {e}")
        raise
    finally:
        if conn:
            conn.close()


def _log_activity(function_name, status, message):
    with database_connection() as conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS activity_log (
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    function_name TEXT,
                    status TEXT,
                    message TEXT
                )
            """)
            cursor.execute(
                "INSERT INTO activity_log (function_name, status, message) VALUES (?, ?, ?)",
                (function_name, status, message),
            )
        except sqlite3.Error as e:
            logging.error(f"Error logging activity: {e}")


@log_activity
def example_function(arg1, arg2):
    if arg1 == "error":
        raise ValueError("Simulated error")
    return arg1 + arg2


@log_activity
def another_function():
    return "Another function executed"


if __name__ == "__main__":
    try:
        example_function("test", "ing")
        example_function("error", "test")
        another_function()
    except Exception as e:
        print(f"Caught an exception: {e}")
