import pytest
import sys
import os
import sqlite3
import json
from fastapi.testclient import TestClient
from typing import List, Dict, Any

# Assuming the script is run from the project root. Adjust if needed.
sys.path.append(os.getcwd())
from src.playground.dashboard_api import app, DATABASE_PATH, TASKS_TABLE, METRICS_FILE, create_database, initialize_metrics_file, get_tasks_from_db, get_metrics_from_file

# Create a test client
client = TestClient(app)

# Fixture to set up and tear down the database and metrics file
@pytest.fixture(scope="function")
def test_setup_and_teardown():
    # Setup - Create a fresh database and metrics file before each test
    if os.path.exists(DATABASE_PATH):
        os.remove(DATABASE_PATH)
    if os.path.exists(METRICS_FILE):
        os.remove(METRICS_FILE)
    create_database()
    initialize_metrics_file()

    # Yield control to the test function
    yield

    # Teardown - Clean up after each test
    if os.path.exists(DATABASE_PATH):
        os.remove(DATABASE_PATH)
    if os.path.exists(METRICS_FILE):
        os.remove(METRICS_FILE)

def test_get_tasks_empty_db(test_setup_and_teardown):
    """Tests GET /tasks when the database is empty."""
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []

def test_get_metrics_empty_file(test_setup_and_teardown):
    """Tests GET /metrics when the metrics file is empty."""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert response.json() == {}

def test_get_tasks_with_data(test_setup_and_teardown):
    """Tests GET /tasks with data in the database."""
    # Insert some data into the database
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO {TASKS_TABLE} (description, status) VALUES (?, ?)", ("Test task 1", "open"))
        cursor.execute(f"INSERT INTO {TASKS_TABLE} (description, status) VALUES (?, ?)", ("Test task 2", "in progress"))
        conn.commit()

    response = client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["description"] == "Test task 1"
    assert data[1]["description"] == "Test task 2"

def test_get_metrics_with_data(test_setup_and_teardown):
    """Tests GET /metrics with data in the metrics file."""
    # Write some data to the metrics file
    metrics_data = {"key1": "value1", "key2": "value2"}
    with open(METRICS_FILE, "w") as f:
        json.dump(metrics_data, f)

    response = client.get("/metrics")
    assert response.status_code == 200
    assert response.json() == metrics_data

def test_get_tasks_db_error(mocker, test_setup_and_teardown):
    """Tests GET /tasks when there's a database error."""
    # Mock the get_tasks_from_db function to raise an exception
    mocker.patch('src.playground.dashboard_api.get_tasks_from_db', side_effect=Exception("Simulated DB error"))
    response = client.get("/tasks")
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}

def test_get_metrics_file_error(mocker, test_setup_and_teardown):
    """Tests GET /metrics when there's a file reading error."""
    # Mock the get_metrics_from_file function to raise an exception
    mocker.patch('src.playground.dashboard_api.get_metrics_from_file', side_effect=Exception("Simulated file error"))
    response = client.get("/metrics")
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}