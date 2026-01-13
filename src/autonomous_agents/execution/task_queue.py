from src.database.connection import get_db
from loguru import logger
import json

class TaskQueue:
    def __init__(self):
        pass

    def add_task(self, title, description="", source="system"):
        """Voegt een nieuwe taak toe aan de queue."""
        query = """
            INSERT INTO tasks (title, description, source, status)
            VALUES (?, ?, ?, 'pending')
        """
        try:
            with get_db() as cursor:
                cursor.execute(query, (title, description, source))
                logger.info(f"Task added to queue: {title}")
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Failed to add task: {e}")
            return None

    def get_next_pending_task(self):
        """Haalt de volgende 'pending' taak op en markeert deze als 'processing'."""
        select_query = """
            SELECT * FROM tasks 
            WHERE status = 'pending' 
            ORDER BY created_at ASC 
            LIMIT 1
        """
        update_query = """
            UPDATE tasks 
            SET status = 'processing', updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        """
        
        try:
            with get_db() as cursor:
                cursor.execute(select_query)
                row = cursor.fetchone()
                
                if row:
                    task = dict(row)
                    cursor.execute(update_query, (task['id'],))
                    return task
                return None
        except Exception as e:
            logger.error(f"Failed to get next task: {e}")
            return None

    def complete_task(self, task_id, result=""):
        """Markeert een taak als voltooid."""
        query = """
            UPDATE tasks 
            SET status = 'completed', result = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        """
        try:
            with get_db() as cursor:
                # Zorg dat result een string is (bijv. JSON string)
                if not isinstance(result, str):
                    result = json.dumps(result)
                    
                cursor.execute(query, (result, task_id))
                logger.info(f"Task {task_id} marked as completed.")
        except Exception as e:
            logger.error(f"Failed to complete task {task_id}: {e}")

    def fail_task(self, task_id, error_message):
        """Markeert een taak als gefaald."""
        query = """
            UPDATE tasks 
            SET status = 'failed', result = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        """
        try:
            with get_db() as cursor:
                cursor.execute(query, (error_message, task_id))
                logger.error(f"Task {task_id} marked as failed: {error_message}")
        except Exception as e:
            logger.error(f"Failed to mark task {task_id} as failed: {e}")
