import pytest
import sys
import os
import json
import sqlite3

# Add the project root to the Python path
sys.path.append(os.getcwd())

from src.dashboard.api import (
    app,
    DATABASE_URL,
    TASKS_TABLE_NAME,
    create_tasks_table,
    get_all_tasks,
    get_metrics,
    Task,
)  # Assuming your API code is in api.py

from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def test_app():
    """Create a TestClient for the FastAPI app."""
    return TestClient(app)


@pytest.fixture(scope="module")
def test_db():
    """Sets up and tears down a test database."""
    # Use an in-memory database for testing
    test_db_url = ":memory:"
    conn = sqlite3.connect(test_db_url)
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

    yield cursor, test_db_url

    # Clean up (no cleanup needed for in-memory database)
    conn.close()


@pytest.fixture
def seed_tasks(test_db):
    """Seeds the test database with some tasks."""
    cursor, _ = test_db
    tasks_to_insert = [
        ("Task 1", "pending"),
        ("Task 2", "in progress"),
        ("Task 3", "completed"),
    ]
    cursor.executemany(
        f"INSERT INTO {TASKS_TABLE_NAME} (description, status) VALUES (?, ?)",
        tasks_to_insert,
    )
    cursor.connection.commit()
    # Fetch the inserted tasks to return them.  Important for testing.
    cursor.execute(f"SELECT id, description, status FROM {TASKS_TABLE_NAME}")
    rows = cursor.fetchall()
    tasks = [Task(id=row[0], description=row[1], status=row[2]) for row in rows]
    return tasks


def test_read_tasks_empty_db(test_app, test_db):
    """Test reading tasks when the database is empty."""
    client = test_app
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []


def test_read_tasks_populated_db(test_app, test_db, seed_tasks):
    """Test reading tasks when the database has data."""
    client = test_app
    response = client.get("/tasks")
    assert response.status_code == 200
    # Convert Task objects to dicts for comparison
    expected_tasks = [task.to_dict() for task in seed_tasks]
    assert response.json() == expected_tasks


def test_read_metrics_success(test_app, tmpdir):
    """Test reading metrics when the lessons_learned.json file exists."""
    # Create a temporary file for the test
    metrics_data = {"key1": "value1", "key2": "value2"}
    file_path = tmpdir.join("lessons_learned.json")
    with open(file_path, "w") as f:
        json.dump(metrics_data, f)

    client = TestClient(app)
    response = client.get("/metrics")
    assert response.status_code == 200
    assert response.json() == metrics_data


def test_read_metrics_file_not_found(test_app, tmpdir):
    """Test reading metrics when the lessons_learned.json file does not exist."""
    client = TestClient(app)
    response = client.get("/metrics")
    assert response.status_code == 200
    assert response.json() == {}
    # Check for the warning message in the logs (not directly testable, but good practice).


def test_read_metrics_json_decode_error(test_app, tmpdir):
    """Test reading metrics when the lessons_learned.json file has invalid JSON."""
    file_path = tmpdir.join("lessons_learned.json")
    with open(file_path, "w") as f:
        f.write("this is not valid json")

    client = TestClient(app)
    response = client.get("/metrics")
    assert response.status_code == 500
    assert response.json() == {"detail": "Error decoding metrics file."}