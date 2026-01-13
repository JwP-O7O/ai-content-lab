import pytest
import sys
import os
import sqlite3
import json
from fastapi.testclient import TestClient
from typing import List, Dict, Any

sys.path.append(os.getcwd())
from src.playground.dashboard_api import app, DATABASE_PATH, TASKS_TABLE, METRICS_FILE, create_database, initialize_metrics_file, get_tasks_from_db, get_metrics_from_file

@pytest.fixture(scope="session")
def test_client():
    """Provides a test client for the FastAPI app."""
    with TestClient(app) as client:
        yield client

@pytest.fixture(scope="function")
def database_setup():
    """Sets up and tears down the database for each test."""
    # Setup - Create a new database and table
    create_database()
    initialize_metrics_file()
    yield
    # Teardown - Clean up the database
    try:
        os.remove(DATABASE_PATH)
    except FileNotFoundError:
        pass
    try:
        os.remove(METRICS_FILE)
    except FileNotFoundError:
        pass



def test_get_tasks_success(test_client, database_setup):
    """Tests the /tasks endpoint for successful retrieval of tasks."""
    # Arrange - Insert a task into the database
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO {TASKS_TABLE} (description, status) VALUES (?, ?)", ("Test Task", "Open"))
        conn.commit()

    # Act - Call the /tasks endpoint
    response = test_client.get("/tasks")

    # Assert - Check the response
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["description"] == "Test Task"
    assert data[0]["status"] == "Open"
    assert "id" in data[0]

def test_get_tasks_empty(test_client, database_setup):
    """Tests the /tasks endpoint when the database is empty."""

    response = test_client.get("/tasks")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0

def test_get_metrics_success(test_client, database_setup):
    """Tests the /metrics endpoint for successful retrieval of metrics."""

    # Arrange - Create a metrics file with some content
    metrics_data = {"test_metric": 123}
    with open(METRICS_FILE, "w") as f:
        json.dump(metrics_data, f)

    # Act - Call the /metrics endpoint
    response = test_client.get("/metrics")

    # Assert - Check the response
    assert response.status_code == 200
    data = response.json()
    assert data == metrics_data


def test_get_metrics_empty(test_client, database_setup):
    """Tests the /metrics endpoint when the metrics file is empty or doesn't exist."""

    # Act - Call the /metrics endpoint
    response = test_client.get("/metrics")

    # Assert - Check the response
    assert response.status_code == 200
    data = response.json()
    assert data == {}

def test_get_metrics_file_not_found(test_client, database_setup):
    """Tests the /metrics endpoint when the metrics file does not exist. (Simulate by deleting it)."""

    # Ensure file does not exist before test (it should be deleted by the database_setup fixture)
    assert not os.path.exists(METRICS_FILE)

    # Act - Call the /metrics endpoint
    response = test_client.get("/metrics")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data == {}