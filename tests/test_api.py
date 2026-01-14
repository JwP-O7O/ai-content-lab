import pytest
import sys
import os
import sqlite3
from fastapi.testclient import TestClient
from typing import List, Dict, Union
import json
from unittest.mock import patch

# Add the project root to the Python path
sys.path.append(os.getcwd())
from src.playground.api import app, DATABASE_URL, LESSONS_LEARNED_FILE  # Import the app and constants

# Create a test client
client = TestClient(app)


# --- Helper Functions and Fixtures ---
@pytest.fixture(scope="function")
def test_db():
    """Creates a temporary database and cleans up after the test."""
    test_db_url = "test_phoenix_os.db"
    conn = sqlite3.connect(test_db_url)
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

    yield test_db_url  # Provide the test database URL

    conn.close()
    os.remove(test_db_url)  # Clean up the test database


@pytest.fixture(scope="function")
def populate_test_db(test_db):
    """Populates the test database with some data."""
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    tasks = [
        ("Task 1", "Open"),
        ("Task 2", "In Progress"),
    ]
    cursor.executemany("INSERT INTO tasks (description, status) VALUES (?, ?)", tasks)
    conn.commit()
    conn.close()
    return


@pytest.fixture(scope="function")
def create_lessons_learned_file(tmp_path):
    """Creates a temporary lessons_learned.json file."""
    data = {"metric1": 10, "metric2": 20}
    file_path = tmp_path / LESSONS_LEARNED_FILE
    with open(file_path, "w") as f:
        json.dump(data, f)
    return file_path


# --- Test Cases ---
def test_read_tasks_empty_db(test_db):
    """Tests the /tasks endpoint when the database is empty."""
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []


def test_read_tasks_populated_db(test_db, populate_test_db):
    """Tests the /tasks endpoint when the database is populated."""
    response = client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert {"description": "Task 1", "status": "Open"} in [
        {k: v for k, v in item.items() if k != 'id'} for item in data]
    assert {"description": "Task 2", "status": "In Progress"} in [
        {k: v for k, v in item.items() if k != 'id'} for item in data]


def test_read_metrics_file_exists(create_lessons_learned_file):
    """Tests the /metrics endpoint when lessons_learned.json exists."""
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert data == {"metric1": 10, "metric2": 20}


def test_read_metrics_file_not_found():
    """Tests the /metrics endpoint when lessons_learned.json does not exist."""
    with patch("src.playground.api.load_lessons_learned") as mock_load:
        mock_load.return_value = {}  # Simulate file not found
        response = client.get("/metrics")
        assert response.status_code == 200
        assert response.json() == {}