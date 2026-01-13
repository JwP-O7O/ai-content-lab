import pytest
import os
import sys
import sqlite3
import json
from fastapi.testclient import TestClient

# Add the project root to the sys.path to allow imports from src
sys.path.append(os.getcwd())
from src.playground.dashboard_api import app, DATABASE_PATH, TASKS_TABLE, METRICS_FILE, create_database, initialize_metrics_file, get_tasks_from_db, get_metrics_from_file

@pytest.fixture(scope="function")
def test_client():
    """Provides a test client for the FastAPI app."""
    return TestClient(app)

@pytest.fixture(scope="function")
def setup_and_teardown_db():
    """Sets up a test database and cleans it up after the test."""
    # Ensure the database file doesn't exist before the test
    if os.path.exists(DATABASE_PATH):
        os.remove(DATABASE_PATH)
    create_database()
    # Populate the database with some initial data
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO {TASKS_TABLE} (description, status) VALUES (?, ?)", ("Test task 1", "open"))
        cursor.execute(f"INSERT INTO {TASKS_TABLE} (description, status) VALUES (?, ?)", ("Test task 2", "in progress"))
        conn.commit()

    yield
    # Teardown: Remove the database file after the test
    if os.path.exists(DATABASE_PATH):
        os.remove(DATABASE_PATH)


@pytest.fixture(scope="function")
def setup_and_teardown_metrics_file():
    """Sets up and tears down the metrics file."""
    # Ensure the metrics file doesn't exist before the test
    if os.path.exists(METRICS_FILE):
        os.remove(METRICS_FILE)
    initialize_metrics_file()
    # Populate the metrics file with initial data
    with open(METRICS_FILE, "w") as f:
        json.dump({"test_metric": 123}, f)

    yield
    # Teardown: Remove the metrics file
    if os.path.exists(METRICS_FILE):
        os.remove(METRICS_FILE)


def test_get_tasks_success(test_client, setup_and_teardown_db):
    """Tests the /tasks endpoint for successful retrieval of tasks."""
    response = test_client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2  # Verify the initial data is present
    assert all(isinstance(task, dict) for task in data)
    assert all("id" in task and "description" in task and "status" in task for task in data)

def test_get_metrics_success(test_client, setup_and_teardown_metrics_file):
    """Tests the /metrics endpoint for successful retrieval of metrics."""
    response = test_client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "test_metric" in data
    assert data["test_metric"] == 123