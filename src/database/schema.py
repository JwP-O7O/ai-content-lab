import sqlite3
import os
from loguru import logger


def init_db():
    """Initialiseert de database en tabellen."""
    db_path = os.environ.get("DATABASE_PATH", "mijn_database.db")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Tasks tabel
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                source TEXT DEFAULT 'system',
                status TEXT DEFAULT 'pending',
                result TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        logger.info("Database schema initialized.")

    except sqlite3.Error as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    init_db()
