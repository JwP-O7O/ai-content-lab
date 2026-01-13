from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import json
from loguru import logger
import os

app = FastAPI()

# Configure CORS
origins = [
    "http://localhost:3000",  # React development server
    "http://localhost",
    "http://127.0.0.1",
    # Add other origins as needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_NAME = "tasks.db"
METRICS_FILE = "lessons_learned.json"


# Helper functions for database operations
def create_tasks_table() -> None:
    """Creates the tasks table if it doesn't exist."""
    try:
        with sqlite3.connect(DATABASE_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    description TEXT NOT NULL,
                    status TEXT NOT NULL
                )
            """
            )
            conn.commit()
            logger.info("Tasks table created (if not exists)")
    except sqlite3.Error as e:
        logger.error(f"Error creating tasks table: {e}")
        raise  # Re-raise to allow FastAPI to handle the error


def insert_task(description: str, status: str) -> int:
    """Inserts a new task into the database."""
    try:
        with sqlite3.connect(DATABASE_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO tasks (description, status) VALUES (?, ?)",
                (description, status),
            )
            conn.commit()
            return cursor.lastrowid  # Return the ID of the inserted row
    except sqlite3.Error as e:
        logger.error(f"Error inserting task: {e}")
        raise  # Re-raise to allow FastAPI to handle the error


def get_all_tasks() -> List[Dict[str, Any]]:
    """Retrieves all tasks from the database."""
    try:
        with sqlite3.connect(DATABASE_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, description, status FROM tasks")
            tasks = [
                {"id": row[0], "description": row[1], "status": row[2]}
                for row in cursor.fetchall()
            ]
            return tasks
    except sqlite3.Error as e:
        logger.error(f"Error retrieving tasks: {e}")
        raise  # Re-raise to allow FastAPI to handle the error


def read_metrics() -> Dict[str, Any]:
    """Reads metrics from the lessons_learned.json file."""
    try:
        if not os.path.exists(METRICS_FILE):
            logger.warning(
                f"Metrics file not found: {METRICS_FILE}. Returning empty metrics."
            )
            return {}
        with open(METRICS_FILE, "r") as f:
            metrics = json.load(f)
            return metrics
    except FileNotFoundError:
        logger.error(f"Metrics file not found: {METRICS_FILE}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON in {METRICS_FILE}: {e}")
        return {}
    except Exception as e:
        logger.error(f"An unexpected error occurred reading metrics: {e}")
        return {}


# Initialize the database (create table if it doesn't exist)
try:
    create_tasks_table()
    # Example data. Remove or comment out in production
    if not get_all_tasks():  # Only populate with data if table is empty
        insert_task("Implement user authentication", "To Do")
        insert_task("Design database schema", "Done")
        insert_task("Write API documentation", "In Progress")
        logger.info("Initialized the tasks table with example data")
except Exception as e:
    logger.critical(f"Failed to initialize database: {e}")
    # Consider exiting the application here if database initialization is critical


@app.get("/tasks", response_model=List[Dict[str, Any]])
def get_tasks():
    """Retrieves all tasks from the database."""
    try:
        tasks = get_all_tasks()
        return tasks
    except Exception as e:
        logger.error(f"Error in /tasks endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


@app.get("/metrics", response_model=Dict[str, Any])
def get_metrics():
    """Retrieves metrics from the lessons_learned.json file."""
    try:
        metrics = read_metrics()
        return metrics
    except Exception as e:
        logger.error(f"Error in /metrics endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")