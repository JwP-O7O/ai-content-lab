import pytest
from fastapi.testclient import TestClient
from src.playground.api import app, DATABASE_URL, LESSONS_LEARNED_FILE
import sqlite3
import json
import os
import sys

# Add the project root to sys.path to resolve imports
sys.path.append(os.getcwd())

# Fixture to create a test client
@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client

# Fixture to set up and tear down the database for testing
@pytest.fixture
def test_db():
    # Use an in-memory database for testing
    test_db_url = "file:memory?mode=memory&cache=shared"
    conn = sqlite3.connect(test_db_url, uri=True)
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
    yield conn, cursor
    conn.close()

# Fixture to set up a test lessons_learned.json file
@pytest.fixture
def test_lessons_learned_file(tmpdir):
    file_path = tmpdir.join("lessons_learned.json")
    lessons_learned_data = {"metric1": 10, "metric2": 20}
    with open(file_path, "w") as f:
        json.dump(lessons_learned_data, f)
    yield file_path
    # Teardown: Remove the file (handled by tmpdir)

# --- Test Cases ---

def test_read_tasks_empty(client, test_db):
    conn, cursor = test_db
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []


def test_read_tasks_populated(client, test_db):
    conn, cursor = test_db
    # Insert some test data
    cursor.execute("INSERT INTO tasks (description, status) VALUES ('task1', 'open')")
    cursor.execute("INSERT INTO tasks (description, status) VALUES ('task2', 'in progress')")
    conn.commit()

    response = client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["description"] == "task1"
    assert data[1]["description"] == "task2"


def test_read_metrics_success(client, test_lessons_learned_file):
    # Overwrite the constant to point to the test file
    from src.playground.api import LESSONS_LEARNED_FILE as CONST_LESSONS_LEARNED_FILE
    CONST_LESSONS_LEARNED_FILE = str(test_lessons_learned_file)  # Ensure it is a string
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert data == {"metric1": 10, "metric2": 20}

def test_read_metrics_file_not_found(client, monkeypatch):
    # Simulate file not found by patching the load_lessons_learned function
    def mock_load_lessons_learned():
        return {}
    
    monkeypatch.setattr("src.playground.api.load_lessons_learned", mock_load_lessons_learned)
    response = client.get("/metrics")
    assert response.status_code == 200
    assert response.json() == {}

def test_database_error_handling(client, monkeypatch):
    # Simulate a database error in get_all_tasks
    def mock_get_all_tasks():
        raise sqlite3.Error("Simulated database error")
    
    monkeypatch.setattr("src.playground.api.get_all_tasks", mock_get_all_tasks)
    response = client.get("/tasks")
    assert response.status_code == 500
    assert response.json() == {"detail": "Failed to retrieve tasks"}