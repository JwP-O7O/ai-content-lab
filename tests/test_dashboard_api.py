import pytest
import sys
import os
import sqlite3
import json
from fastapi.testclient import TestClient

# Add the project root to the Python path
sys.path.append(os.getcwd())
from src.playground.dashboard_api import app, DATABASE_NAME, METRICS_FILE, create_tasks_table, insert_task, get_all_tasks, read_metrics  # noqa: E501

@pytest.fixture(scope="session")
def test_client():
    """Provides a test client for the FastAPI app."""
    with TestClient(app) as client:
        yield client

@pytest.fixture(autouse=True)
def setup_and_teardown():
    """
    Sets up the test environment before each test and cleans up after.
    Creates a test database and removes it after each test. Also handles the
    metrics file.
    """
    # Setup - Create the test database and table
    if os.path.exists(DATABASE_NAME):
        os.remove(DATABASE_NAME)
    create_tasks_table()

    # Create the metrics file if it doesn't exist to avoid FileNotFoundError
    if os.path.exists(METRICS_FILE):
        os.remove(METRICS_FILE)
    with open(METRICS_FILE, "w") as f:
        json.dump({}, f)

    yield  # Run the tests

    # Teardown - Remove the test database
    if os.path.exists(DATABASE_NAME):
        os.remove(DATABASE_NAME)
    if os.path.exists(METRICS_FILE):
        os.remove(METRICS_FILE)

def test_get_tasks_empty(test_client):
    """Tests the /tasks endpoint when the database is empty."""
    response = test_client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []

def test_get_tasks_populated(test_client):
    """Tests the /tasks endpoint when the database has data."""
    # Insert some test data
    insert_task("Test task 1", "To Do")
    insert_task("Test task 2", "In Progress")

    response = test_client.get("/tasks")
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 2
    assert any(task["description"] == "Test task 1" for task in tasks)
    assert any(task["description"] == "Test task 2" for task in tasks)

def test_get_metrics_empty_file(test_client):
    """Tests the /metrics endpoint when the metrics file is empty."""
    response = test_client.get("/metrics")
    assert response.status_code == 200
    assert response.json() == {}

def test_get_metrics_populated_file(test_client):
    """Tests the /metrics endpoint when the metrics file has data."""
    metrics_data = {"key1": "value1", "key2": "value2"}
    with open(METRICS_FILE, "w") as f:
        json.dump(metrics_data, f)

    response = test_client.get("/metrics")
    assert response.status_code == 200
    assert response.json() == metrics_data

def test_insert_task():
    """Tests the insert_task helper function."""
    insert_task("Test task", "Done")
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT description, status FROM tasks WHERE description = 'Test task'")
        result = cursor.fetchone()
        assert result is not None
        assert result[0] == "Test task"
        assert result[1] == "Done"

def test_read_metrics_file_not_found():
    """Tests the read_metrics function when the metrics file is not found."""
    # Remove the metrics file if it exists
    if os.path.exists(METRICS_FILE):
        os.remove(METRICS_FILE)
    metrics = read_metrics()
    assert metrics == {}

def test_read_metrics_file_invalid_json():
    """Tests the read_metrics function when the metrics file contains invalid JSON."""
    with open(METRICS_FILE, "w") as f:
        f.write("invalid json")
    metrics = read_metrics()
    assert metrics == {}