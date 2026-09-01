"""
Pytest configuration and shared fixtures for FastAPI tests.
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


def create_fresh_activities():
    """Create a fresh copy of activities for test isolation."""
    return {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball training and matches",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Tennis lessons and tournament preparation",
            "schedule": "Saturdays, 10:00 AM - 11:30 AM",
            "max_participants": 10,
            "participants": ["sophia@mergington.edu"]
        },
        "Art Studio": {
            "description": "Painting, drawing, and sculpture techniques",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["isabella@mergington.edu", "noah@mergington.edu"]
        },
        "Music Band": {
            "description": "Learn instruments and perform in concerts",
            "schedule": "Tuesdays and Fridays, 4:00 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["lucas@mergington.edu"]
        },
        "Debate Club": {
            "description": "Develop argumentation and public speaking skills",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["ava@mergington.edu", "ryan@mergington.edu"]
        },
        "Science Club": {
            "description": "Explore STEM topics through experiments and projects",
            "schedule": "Mondays, 4:00 PM - 5:30 PM",
            "max_participants": 22,
            "participants": ["chloe@mergington.edu"]
        }
    }


@pytest.fixture
def app_client():
    """
    Fixture: Returns TestClient with fresh app state for isolated unit tests.
    Each test gets a clean copy of activities to ensure test isolation.
    """
    # Replace global activities with fresh copy
    activities.clear()
    activities.update(create_fresh_activities())
    
    # Return TestClient
    return TestClient(app)


@pytest.fixture
def seeded_activities():
    """
    Fixture: Returns TestClient with pre-seeded test data for integration tests.
    State is restored after test completes (setup/teardown pattern).
    """
    # Setup: Store original state
    original_activities = {k: v.copy() if isinstance(v, dict) else v 
                          for k, v in activities.items()}
    
    # Reset to fresh state
    activities.clear()
    activities.update(create_fresh_activities())
    
    # Create and yield client
    client = TestClient(app)
    yield client
    
    # Teardown: Restore original state
    activities.clear()
    activities.update(original_activities)
