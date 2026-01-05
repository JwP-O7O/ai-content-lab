from contextlib import contextmanager
import sqlite3  #  Vervang dit met je eigen database-bibliotheek
import os

@contextmanager
def get_db():
    """
    Context manager voor database-interactie.  Zorgt voor verbinding,
    uitvoering van queries en correcte sluiting van de verbinding,
    met foutafhandeling.
    """
    conn = None
    try:
        # Bepaal het pad naar de database.  Gebruik een omgevingsvariabele
        # voor de locatie, met een fallback.
        db_path = os.environ.get("DATABASE_PATH", "mijn_database.db")

        # Verbind met de database
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Optioneel: retourneer resultaten als dictionaries

        cursor = conn.cursor()
        yield cursor
        conn.commit()  # Sla wijzigingen op
    except sqlite3.Error as e:  # Specifieke exception voor SQLite
        print(f"Database operatie mislukt: {e}")  # Logging in plaats van printen in productie
        if conn:
            conn.rollback()  # Rol transactie terug bij fout
        raise  # Her-raise de uitzondering zodat de applicatie weet dat er een probleem is
    finally:
        if conn:
            conn.close() # Sluit de verbinding