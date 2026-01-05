import sqlite3
import os

class DatabaseManager:
    def __init__(self, db_file="ai_database.db"):
        self.db_file = db_file
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()

    def connect(self):
        try:
            self.conn = sqlite3.connect(self.db_file)
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            print(f"Database connectie fout: {e}")

    def create_tables(self):
        # Voorbeeld: Tabel om research resultaten op te slaan
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS research_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_name TEXT,
                query TEXT,
                result TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Voorbeeld: Tabel om features op te slaan
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS features (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                feature_name TEXT,
                description TEXT,
                status TEXT,
                created_by TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)


    def execute_query(self, query, params=None):
        try:
            if self.cursor:
                if params:
                    self.cursor.execute(query, params)
                else:
                    self.cursor.execute(query)
                self.conn.commit()
                return self.cursor.lastrowid # Return laatste ID voor INSERT queries.
        except sqlite3.Error as e:
            print(f"Database query fout: {e}. Query: {query}, Parameters: {params if params else 'None'}")
            return None

    def fetch_one(self, query, params=None):
        try:
            if self.cursor:
                if params:
                    self.cursor.execute(query, params)
                else:
                    self.cursor.execute(query)
                return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Database fetch_one fout: {e}. Query: {query}, Parameters: {params if params else 'None'}")
            return None

    def fetch_all(self, query, params=None):
        try:
            if self.cursor:
                if params:
                    self.cursor.execute(query, params)
                else:
                    self.cursor.execute(query)
                return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Database fetch_all fout: {e}. Query: {query}, Parameters: {params if params else 'None'}")
            return None

    def insert_research_result(self, agent_name, query, result):
        self.execute_query("""
            INSERT INTO research_results (agent_name, query, result)
            VALUES (?, ?, ?)
        """, (agent_name, query, result))

    def get_research_results_by_agent(self, agent_name):
        return self.fetch_all("""
            SELECT query, result, timestamp
            FROM research_results
            WHERE agent_name = ?
            ORDER BY timestamp DESC
        """, (agent_name,))

    def insert_feature(self, feature_name, description, status, created_by):
        self.execute_query("""
            INSERT INTO features (feature_name, description, status, created_by)
            VALUES (?, ?, ?, ?)
        """, (feature_name, description, status, created_by))

    def get_features_by_status(self, status):
         return self.fetch_all("""
            SELECT feature_name, description, status, created_by, timestamp
            FROM features
            WHERE status = ?
            ORDER BY timestamp DESC
        """, (status,))


    def close(self):
        if self.conn:
            self.conn.close()