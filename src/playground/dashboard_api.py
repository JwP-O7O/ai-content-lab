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
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost",
    "http://127.0.0.1",
    "http://localhost:8080", # Frontend Dashboard Port
    "*" # Allow all for development convenience
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database Setup
DATABASE_PATH = os.environ.get("DATABASE_PATH", "mijn_database.db")
# Note: TASKS_TABLE definition in original file might differ from actual schema (tasks vs tasks table). 
# We should inspect actual schema, but let's point to the right DB file first.
TASKS_TABLE = "tasks" 
METRICS_FILE = "data/improvement_plans/lessons_learned.json"


def create_database() -> None:
    """Creates the SQLite database and tasks table if they don't exist."""
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {TASKS_TABLE} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    description TEXT NOT NULL,
                    status TEXT NOT NULL
                )
            """
            )
            conn.commit()
            logger.info("Database and tasks table created (if not exists).")

    except sqlite3.Error as e:
        logger.error(f"Error creating database or table: {e}")
        raise  # Re-raise to stop server if DB creation fails.


def initialize_metrics_file() -> None:
    """Creates the lessons_learned.json file if it doesn't exist."""
    if not os.path.exists(METRICS_FILE):
        try:
            with open(METRICS_FILE, "w") as f:
                json.dump({}, f)
            logger.info(f"Initialized metrics file: {METRICS_FILE}")
        except IOError as e:
            logger.error(f"Error initializing metrics file: {e}")
            raise  # Re-raise to stop server if file creation fails.


create_database()
initialize_metrics_file()


# Helper Functions
def get_tasks_from_db() -> List[Dict[str, Any]]:
    """Retrieves all tasks from the database."""
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {TASKS_TABLE}")
            columns = [col[0] for col in cursor.description]
            tasks = [dict(zip(columns, row)) for row in cursor.fetchall()]
            logger.info(f"Retrieved {len(tasks)} tasks from the database.")
            return tasks
    except sqlite3.Error as e:
        logger.error(f"Error fetching tasks from database: {e}")
        raise HTTPException(status_code=500, detail="Database error")


def get_metrics_from_file() -> Dict[str, Any]:
    """Retrieves metrics from the lessons_learned.json file."""
    try:
        with open(METRICS_FILE, "r") as f:
            metrics = json.load(f)
            logger.info(f"Retrieved metrics from {METRICS_FILE}")
            return metrics
    except FileNotFoundError:
        logger.warning(
            f"Metrics file not found: {METRICS_FILE}. Returning empty metrics."
        )
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from {METRICS_FILE}: {e}")
        raise HTTPException(status_code=500, detail="Error reading metrics file")


# API Endpoints
@app.get("/tasks", response_model=List[Dict[str, Any]])
async def get_tasks():
    """Retrieves all tasks from the database."""
    try:
        tasks = get_tasks_from_db()
        return tasks
    except HTTPException as e:
        raise e  # Re-raise HTTPExceptions
    except Exception as e:
        logger.error(f"Unexpected error in /tasks endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/metrics", response_model=Dict[str, Any])
async def get_metrics():
    """Retrieves metrics from the lessons_learned.json file."""
    try:
        metrics = get_metrics_from_file()
        return metrics
    except HTTPException as e:
        raise e  # Re-raise HTTPExceptions
    except Exception as e:
        logger.error(f"Unexpected error in /metrics endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")