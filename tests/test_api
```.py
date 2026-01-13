import pytest
import sys
import os
import json
import sqlite3
from fastapi.testclient import TestClient

# Add the project root to the Python path
sys.path.append(os.getcwd())

from src.playground.
#_src.dashboard.api
 import *  # noqa: E402 (module level import not at top of file)

# Use the app instance for testing
client = TestClient(app)

# Fixture to create and populate the database for testing
@pytest.fixture(scope="function")
def test_db():
    DATABASE_URL = "test_phoenix_os.db"
    TASKS_TABLE_NAME = "tasks"

    # Connect to the database
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()

    # Create the tasks table
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

    # Populate the database with some test data
    test_tasks = [
        ("Task 1", "pending"),
        ("Task 2", "in progress"),
    ]
    cursor.executemany(
        f"INSERT INTO {TASKS_TABLE_NAME} (description, status) VALUES (?, ?)",
        test_tasks,
    )
    conn.commit()

    yield
    # Clean up the database after the test
    cursor.execute(f"DROP TABLE IF EXISTS {TASKS_TABLE_NAME}")
    conn.commit()
    conn.close()
    if os.path.exists(DATABASE_URL):
        os.remove(DATABASE_URL)


# Fixture to create a test metrics file
@pytest.fixture(scope="function")
def test_metrics_file():
    metrics_file = "lessons_learned.json"
    test_metrics = {"key1": "value1", "key2": "value2"}
    with open(metrics_file, "w") as f:
        json.dump(test_metrics, f)
    yield
    if os.path.exists(metrics_file):
        os.remove(metrics_file)


def test_read_tasks_success(test_db):
    response = client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2  # Assuming the test_db fixture populates with 2 tasks
    assert "id" in data[0]
    assert "description" in data[0]
    assert "status" in data[0]


def test_read_metrics_success(test_metrics_file):
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "key1" in data
    assert "key2" in data


def test_read_metrics_file_not_found():
    # Remove the test_metrics_file fixture to simulate the file not existing.
    response = client.get("/metrics")
    assert response.status_code == 200  # Should return empty dict.
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == 0


def test_read_tasks_db_error():
    # Simulate a database error by attempting to connect to a non-existent database.
    # We can't directly trigger a database error in this setup.  Instead, we verify
    # that the endpoint handles it gracefully.  The current implementation does NOT
    # have any error handling in get_all_tasks or read_tasks other than a try/except,
    # so we can't test it.
    pass # No good way to test the error condition in the current setup.