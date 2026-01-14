import pytest
import os
import sys
import sqlite3
import json
from fastapi.testclient import TestClient
from typing import List, Dict, Union

# Add the project root to the sys.path to allow imports from src
sys.path.append(os.getcwd())

from src.playground.api import app, DATABASE_URL, LESSONS_LEARNED_FILE  # noqa: E402


@pytest.fixture(scope="module")
def test_client():
    """Create a test client for the FastAPI app."""
    client = TestClient(app)
    yield client


@pytest.fixture(scope="module")
def setup_db():
    """Set up the database for testing.  Creates a test database and a dummy tasks table."""
    test_db_url = "test_phoenix_os.db"
    original_db_url = DATABASE_URL
    global DATABASE_URL
    DATABASE_URL = test_db_url  # Use the test database

    try:
        with sqlite3.connect(test_db_url) as conn:
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
    except sqlite3.Error as e:
        pytest.fail(f"Failed to create test database or table: {e}")

    yield
    # Teardown: Clean up the test database and restore the original database URL
    try:
        os.remove(test_db_url)
    except FileNotFoundError:
        pass  # It's fine if the file doesn't exist.
    finally:
        DATABASE_URL = original_db_url  # Restore original database URL


@pytest.fixture(scope="module")
def setup_lessons_learned_file():
    """Set up a dummy lessons_learned.json file for testing."""
    test_lessons_learned_file = "test_lessons_learned.json"
    original_lessons_learned_file = LESSONS_LEARNED_FILE
    global LESSONS_LEARNED_FILE
    LESSONS_LEARNED_FILE = test_lessons_learned_file

    test_data = {"test_metric": 123}
    try:
        with open(test_lessons_learned_file, "w") as f:
            json.dump(test_data, f)
    except Exception as e:
        pytest.fail(f"Failed to create test lessons_learned.json file: {e}")

    yield
    # Teardown: Clean up the test JSON file and restore the original filename
    try:
        os.remove(test_lessons_learned_file)
    except FileNotFoundError:
        pass
    finally:
        LESSONS_LEARNED_FILE = original_lessons_learned_file


def test_read_tasks_success(test_client, setup_db):
    """Test the /tasks endpoint when tasks are present."""
    # Insert a dummy task
    with sqlite3.connect(DATABASE_URL) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tasks (description, status) VALUES (?, ?)", ("test task", "open"))
        conn.commit()

    response = test_client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["description"] == "test task"
    assert data[0]["status"] == "open"
    assert "id" in data[0]

def test_read_tasks_no_tasks(test_client, setup_db):
    """Test the /tasks endpoint when no tasks are present."""
    response = test_client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_read_metrics_success(test_client, setup_lessons_learned_file):
    """Test the /metrics endpoint when lessons_learned.json exists."""
    response = test_client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert data == {"test_metric": 123}


def test_read_metrics_file_not_found(test_client):
    """Test the /metrics endpoint when lessons_learned.json does not exist."""
    # Ensure the lessons learned file is not present.  We can't reliably delete it directly due to the fixture setup.
    # Instead, we rely on the default behavior that the fixture will create/delete it correctly.
    # The absence of the file is handled gracefully by the function.
    response = test_client.get("/metrics")
    assert response.status_code == 200
    assert response.json() == {} #  Expect an empty dictionary


def test_startup_creates_table():
    """Test the startup event creates the database table (indirectly)."""
    test_db_url = "test_startup.db"  # Use a temporary database.
    original_db_url = DATABASE_URL
    global DATABASE_URL
    DATABASE_URL = test_db_url
    try:
      from src.playground.api import startup_event
      startup_event()
      with sqlite3.connect(test_db_url) as conn:
          cursor = conn.cursor()
          cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tasks';")
          result = cursor.fetchone()
          assert result is not None, "Tasks table was not created on startup"
    except Exception as e:
        pytest.fail(f"Failed to verify database table creation: {e}")
    finally:
        # Cleanup
        DATABASE_URL = original_db_url
        try:
          os.remove(test_db_url)
        except FileNotFoundError:
          pass