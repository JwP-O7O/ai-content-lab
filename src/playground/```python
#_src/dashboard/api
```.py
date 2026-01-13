from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import json
from loguru import logger

app = FastAPI()

# Configure CORS
origins = [
    "http://localhost:3000",  # React Frontend (example)
    "http://localhost:8000",  # FastAPI development server
    # Add other allowed origins here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database Setup
DATABASE_URL = "phoenix_os.db"
TASKS_TABLE_NAME = "tasks"


def create_tasks_table():
    """Creates the tasks table if it doesn't exist."""
    try:
        with sqlite3.connect(DATABASE_URL) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {TASKS_TABLE_NAME} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    description TEXT NOT NULL,
                    status TEXT DEFAULT 'pending'
                )
            """
            )
            conn.commit()
            logger.info("Tasks table created (if it didn't exist).")
    except sqlite3.Error as e:
        logger.error(f"Error creating tasks table: {e}")


create_tasks_table()


# Data models (optional, but good practice)
class Task(object):
    id: int
    description: str
    status: str

    def __init__(self, id: int, description: str, status: str):
        self.id = id
        self.description = description
        self.status = status

    def to_dict(self):
        return {"id": self.id, "description": self.description, "status": self.status}


# Helper functions for database interaction
def get_all_tasks() -> List[Task]:
    """Retrieves all tasks from the database."""
    tasks: List[Task] = []
    try:
        with sqlite3.connect(DATABASE_URL) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT id, description, status FROM {TASKS_TABLE_NAME}")
            rows = cursor.fetchall()
            for row in rows:
                tasks.append(Task(id=row[0], description=row[1], status=row[2]))
        logger.info("Retrieved tasks from database.")
        return tasks
    except sqlite3.Error as e:
        logger.error(f"Error getting tasks: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


def get_metrics() -> Dict[str, Any]:
    """Reads metrics from lessons_learned.json."""
    try:
        with open("lessons_learned.json", "r") as f:
            metrics: Dict[str, Any] = json.load(f)
        logger.info("Retrieved metrics from lessons_learned.json")
        return metrics
    except FileNotFoundError:
        logger.warning("lessons_learned.json not found.")
        return {}  # Or raise an exception, depending on your needs
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding lessons_learned.json: {e}")
        raise HTTPException(status_code=500, detail="Error decoding metrics file.")
    except Exception as e:
        logger.error(
            f"An unexpected error occurred while reading lessons_learned.json: {e}"
        )
        raise HTTPException(status_code=500, detail="Error reading metrics file.")


# API Endpoints
@app.get("/tasks", response_model=List[dict])
def read_tasks():
    """Retrieves all tasks."""
    try:
        tasks = get_all_tasks()
        return [task.to_dict() for task in tasks]
    except HTTPException as e:
        raise e  # Re-raise the HTTPException
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/metrics", response_model=Dict[str, Any])
def read_metrics():
    """Retrieves metrics."""
    try:
        metrics = get_metrics()
        return metrics
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")