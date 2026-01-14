from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import json
from typing import List, Dict, Union
from loguru import logger

app = FastAPI()

# Configure CORS
origins = [
    "http://localhost:3000",  # React Frontend - aan te passen aan frontend host
    "http://localhost:8000",  # FastAPI development server - aan te passen aan frontend host
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = "phoenix_os.db"
LESSONS_LEARNED_FILE = "lessons_learned.json"


# --- Database Operations ---
def create_db_table() -> None:
    """Creates the tasks table if it doesn't exist."""
    try:
        with sqlite3.connect(DATABASE_URL) as conn:
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
        logger.error(f"Database error: {e}")
        raise  # Re-raise to be handled by the endpoint


def get_all_tasks() -> List[Dict[str, Union[int, str]]]:
    """Retrieves all tasks from the database."""
    try:
        with sqlite3.connect(DATABASE_URL) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, description, status FROM tasks")
            tasks = [
                {"id": row[0], "description": row[1], "status": row[2]}
                for row in cursor.fetchall()
            ]
            return tasks
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        raise  # Re-raise to be handled by the endpoint


def load_lessons_learned() -> Dict:
    """Loads metrics from lessons_learned.json."""
    try:
        with open(LESSONS_LEARNED_FILE, "r") as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        logger.warning(f"Lessons learned file not found: {LESSONS_LEARNED_FILE}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from {LESSONS_LEARNED_FILE}: {e}")
        return {}


# --- API Endpoints ---
@app.get("/tasks", response_model=List[Dict[str, Union[int, str]]])
def read_tasks():
    """Retrieves all tasks."""
    try:
        tasks = get_all_tasks()
        return tasks
    except Exception as e:
        logger.error(f"Failed to retrieve tasks: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve tasks")


@app.get("/metrics", response_model=Dict)
def read_metrics():
    """Retrieves metrics from lessons_learned.json."""
    try:
        metrics = load_lessons_learned()
        return metrics
    except Exception as e:
        logger.error(f"Failed to retrieve metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve metrics")


# --- Startup Event ---
@app.on_event("startup")
def startup_event():
    """Creates the database table on startup."""
    try:
        create_db_table()
    except Exception as e:
        logger.error(f"Failed to create database table on startup: {e}")