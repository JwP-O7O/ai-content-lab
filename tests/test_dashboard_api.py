import pytest
import sys
import os
import sqlite3
from fastapi.testclient import TestClient
from typing import List, Dict, Any
import json

# Add the project root to the Python path
sys.path.append(os.getcwd())
from src.playground.dashboard_api import app, DATABASE_NAME, METRICS_FILE, create_tasks_table, insert_task, get_all_tasks, read_metrics  # noqa: E501

# Create a TestClient instance
client = TestClient(app)


# Fixture to set up and tear down the database for each test
@pytest.fixture(scope="function")
def test_db():
    # Setup - Create a temporary database and table
    if os.path.exists(DATABASE_NAME):
        os.remove(DATABASE_NAME)
    create_tasks_table()
    yield  # Run the tests
    # Teardown - Remove the temporary database
    if os.path.exists(DATABASE_NAME):
        os.remove(DATABASE_NAME)


# Fixture to set up and tear down the metrics file for each test
@pytest.fixture(scope="function")
def test_metrics_file():
    # Setup - Create a temporary metrics file
    if os.path.exists(METRICS_FILE):
        os.remove(METRICS_FILE)
    yield  # Run the tests
    # Teardown - Remove the temporary metrics file
    if os.path.exists(METRICS_FILE):
        os.remove(METRICS_FILE)


def test_get_tasks_empty_db(test_db):
    """Tests the /tasks endpoint when the database is empty."""
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []


def test_get_tasks_populated_db(test_db):
    """Tests the /tasks endpoint when the database is populated."""
    # Insert a task
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tasks (description, status) VALUES (?, ?)", ("Test task", "Testing"))
        conn.commit()

    response = client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["description"] == "Test task"
    assert data[0]["status"] == "Testing"


def test_get_metrics_no_file(test_metrics_file):
    """Tests the /metrics endpoint when the metrics file does not exist."""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert response.json() == {}


def test_get_metrics_with_file(test_metrics_file):
    """Tests the /metrics endpoint when the metrics file exists."""
    metrics_data = {"lessons": [{"title": "Example", "description": "Test data"}]}
    with open(METRICS_FILE, "w") as f:
        json.dump(metrics_data, f)

    response = client.get("/metrics")
    assert response.status_code == 200
    assert response.json() == metrics_data