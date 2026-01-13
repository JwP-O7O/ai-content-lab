import pytest
import os
import sys
import sqlite3
import json
from fastapi.testclient import TestClient

# Add the project root to the sys.path to make imports work
sys.path.append(os.getcwd())
from src.playground.dashboard_api import app, DATABASE_NAME, METRICS_FILE, create_tasks_table, insert_task, get_all_tasks, read_metrics

# Create a TestClient instance
client = TestClient(app)

# Fixture to set up and tear down the database for each test
@pytest.fixture(scope="function")
def test_db():
    # Setup - Create a temporary database and populate with test data
    if os.path.exists(DATABASE_NAME):
        os.remove(DATABASE_NAME)
    create_tasks_table()
    test_task_data = [
        ("Test task 1", "To Do"),
        ("Test task 2", "In Progress"),
        ("Test task 3", "Done"),
    ]
    task_ids = []
    for description, status in test_task_data:
        task_ids.append(insert_task(description, status))
    yield
    # Teardown - Remove the temporary database after the test
    if os.path.exists(DATABASE_NAME):
        os.remove(DATABASE_NAME)

# Fixture to create and delete the metrics file
@pytest.fixture(scope="function")
def test_metrics_file():
    # Setup: Create a test metrics file
    test_metrics_data = {"lessons": ["Test lesson 1", "Test lesson 2"]}
    with open(METRICS_FILE, "w") as f:
        json.dump(test_metrics_data, f)
    yield
    # Teardown: Remove the test metrics file
    if os.path.exists(METRICS_FILE):
        os.remove(METRICS_FILE)


def test_get_tasks_success(test_db):
    response = client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3  # Check for the inserted test data
    assert all("id" in task and "description" in task and "status" in task for task in data)


def test_get_tasks_empty(test_db):
     # Empty the database to test the empty scenario
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks")
        conn.commit()

    response = client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0

def test_get_tasks_internal_server_error():
    # Mock the get_all_tasks to raise an exception
    def mock_get_all_tasks():
        raise sqlite3.Error("Simulated database error")

    # Monkeypatch the get_all_tasks function
    from src.playground.dashboard_api import get_all_tasks as original_get_all_tasks
    import src.playground.dashboard_api
    src.playground.dashboard_api.get_all_tasks = mock_get_all_tasks

    response = client.get("/tasks")
    assert response.status_code == 500
    assert "Internal server error" in response.json()["detail"]

    # Restore the original function
    src.playground.dashboard_api.get_all_tasks = original_get_all_tasks


def test_get_metrics_success(test_metrics_file):
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "lessons" in data
    assert isinstance(data["lessons"], list)
    assert len(data["lessons"]) == 2


def test_get_metrics_not_found():
    # Remove the metrics file before the test
    if os.path.exists(METRICS_FILE):
        os.remove(METRICS_FILE)

    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert data == {}


def test_get_metrics_internal_server_error():
    # Mock the read_metrics function to raise an exception
    def mock_read_metrics():
        raise Exception("Simulated file error")
    
    # Monkeypatch the read_metrics function
    from src.playground.dashboard_api import read_metrics as original_read_metrics
    import src.playground.dashboard_api
    src.playground.dashboard_api.read_metrics = mock_read_metrics
    
    response = client.get("/metrics")
    assert response.status_code == 500
    assert "Internal server error" in response.json()["detail"]
    
    # Restore the original function
    src.playground.dashboard_api.read_metrics = original_read_metrics