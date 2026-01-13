import pytest
import sys
import os
import sqlite3
import json
from fastapi.testclient import TestClient

# Add the project root to the Python path
sys.path.append(os.getcwd())
from src.playground.
#_src.dashboard.api
 import *

# Initialize the FastAPI app for testing
client = TestClient(app)

# Constants for testing
DATABASE_URL_TEST = "test_phoenix_os.db"
TASKS_TABLE_NAME_TEST = "test_tasks"
METRICS_FILE_TEST = "test_lessons_learned.json"

# Fixtures

@pytest.fixture(scope="session")
def database_setup():
    """Sets up the test database and table."""
    conn = sqlite3.connect(DATABASE_URL_TEST)
    cursor = conn.cursor()
    cursor.execute(f"DROP TABLE IF EXISTS {TASKS_TABLE_NAME_TEST}")  # Clean up from previous runs
    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {TASKS_TABLE_NAME_TEST} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            status TEXT DEFAULT 'pending'
        )
    """
    )
    conn.commit()
    conn.close()

    yield  # Let the tests run

    # Teardown: Clean up after tests
    conn = sqlite3.connect(DATABASE_URL_TEST)
    cursor = conn.cursor()
    cursor.execute(f"DROP TABLE IF EXISTS {TASKS_TABLE_NAME_TEST}")
    conn.commit()
    conn.close()
    if os.path.exists(METRICS_FILE_TEST):
        os.remove(METRICS_FILE_TEST)



@pytest.fixture
def populate_tasks(database_setup):
    """Populates the test database with sample tasks."""
    with sqlite3.connect(DATABASE_URL_TEST) as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"INSERT INTO {TASKS_TABLE_NAME_TEST} (description, status) VALUES (?, ?)",
            ("Task 1", "pending"),
        )
        cursor.execute(
            f"INSERT INTO {TASKS_TABLE_NAME_TEST} (description, status) VALUES (?, ?)",
            ("Task 2", "in progress"),
        )
        conn.commit()
        
@pytest.fixture
def create_metrics_file():
    """Creates a sample metrics file."""
    metrics_data = {"key1": "value1", "key2": 123}
    with open(METRICS_FILE_TEST, "w") as f:
        json.dump(metrics_data, f)
    yield
    if os.path.exists(METRICS_FILE_TEST):
        os.remove(METRICS_FILE_TEST)


# Tests

def test_read_tasks_empty_db(database_setup):
    """Tests the /tasks endpoint when the database is empty."""
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []


def test_read_tasks_populated_db(database_setup, populate_tasks):
    """Tests the /tasks endpoint when the database has data."""
    # Override the DATABASE_URL to use the test database
    global DATABASE_URL
    DATABASE_URL = DATABASE_URL_TEST
    response = client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert {"id": 1, "description": "Task 1", "status": "pending"} in data
    assert {"id": 2, "description": "Task 2", "status": "in progress"} in data
    # Reset DATABASE_URL after test
    DATABASE_URL = "phoenix_os.db"



def test_read_metrics_file_exists(database_setup, create_metrics_file):
    """Tests the /metrics endpoint when the metrics file exists."""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert response.json() == {"key1": "value1", "key2": 123}


def test_read_metrics_file_not_found(database_setup):
    """Tests the /metrics endpoint when the metrics file does not exist."""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert response.json() == {}

def test_get_all_tasks_db_error(database_setup, mocker):
    """Tests the get_all_tasks function when a database error occurs."""

    mocker.patch('sqlite3.connect', side_effect=sqlite3.Error("Test DB Error"))
    with pytest.raises(HTTPException) as excinfo:
        get_all_tasks()
    assert excinfo.value.status_code == 500
    assert "Database error" in str(excinfo.value.detail)

def test_get_metrics_file_error(database_setup, mocker):
    """Tests the get_metrics function when a file error occurs."""
    mocker.patch('builtins.open', side_effect=FileNotFoundError)

    with pytest.raises(HTTPException) as excinfo:
        get_metrics()
    assert excinfo.value.status_code == 500
    assert "Error reading metrics file" in str(excinfo.value.detail)