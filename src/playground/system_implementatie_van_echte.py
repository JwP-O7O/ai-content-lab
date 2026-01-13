import sqlite3
import logging
import contextlib
import threading

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

DATABASE_NAME = "mydatabase.db"
lock = threading.Lock()


class DatabaseError(Exception):
    pass


@contextlib.contextmanager
def get_db():
    conn = None
    try:
        with lock:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()
            yield cursor
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        raise DatabaseError(f"Database operation failed: {e}") from e
    finally:
        if conn:
            try:
                conn.commit()
            except sqlite3.Error as e:
                logging.error(f"Commit error: {e}")
            try:
                conn.close()
            except sqlite3.Error as e:
                logging.error(f"Close error: {e}")


def create_table():
    try:
        with get_db() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS items (
                    id INTEGER PRIMARY KEY,
                    name TEXT
                )
            """)
        logging.info("Table 'items' created (if not exists).")
    except DatabaseError as e:
        logging.error(f"Failed to create table: {e}")


def insert_item(name):
    try:
        with get_db() as cursor:
            cursor.execute("INSERT INTO items (name) VALUES (?)", (name,))
        logging.info(f"Inserted item: {name}")
    except DatabaseError as e:
        logging.error(f"Failed to insert item: {e}")


def get_all_items():
    items = []
    try:
        with get_db() as cursor:
            cursor.execute("SELECT * FROM items")
            items = cursor.fetchall()
        logging.info("Retrieved all items.")
    except DatabaseError as e:
        logging.error(f"Failed to get items: {e}")
    return items


def main():
    create_table()
    insert_item("Example Item")
    all_items = get_all_items()
    print(all_items)


if __name__ == "__main__":
    main()
