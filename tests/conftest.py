"""Pytest configuration and fixtures for API tests."""
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from fastapi.testclient import TestClient
from app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test."""
    from app import activities
    
    # Store original state
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": [{"email": "michael@mergington.edu"}, {"email": "daniel@mergington.edu"}]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": [{"email": "emma@mergington.edu"}, {"email": "sophia@mergington.edu"}]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": [{"email": "john@mergington.edu"}, {"email": "olivia@mergington.edu"}]
        },
        "Soccer Team": {
            "description": "Competitive soccer training and matches",
            "schedule": "Mondays, Wednesdays, 4:00 PM - 6:00 PM",
            "max_participants": 22,
            "participants": [{"email": "liam@mergington.edu"}, {"email": "noah@mergington.edu"}]
        },
        "Basketball Team": {
            "description": "Team practices and interschool tournaments",
            "schedule": "Tuesdays, Thursdays, 5:00 PM - 7:00 PM",
            "max_participants": 15,
            "participants": [{"email": "mia@mergington.edu"}, {"email": "lucas@mergington.edu"}]
        },
        "Art Club": {
            "description": "Drawing, painting, and portfolio development",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": [{"email": "ava@mergington.edu"}, {"email": "isabella@mergington.edu"}]
        },
        "Drama Club": {
            "description": "Acting workshops and stage productions",
            "schedule": "Fridays, 4:00 PM - 6:30 PM",
            "max_participants": 25,
            "participants": [{"email": "charlotte@mergington.edu"}, {"email": "amelia@mergington.edu"}]
        },
        "Debate Team": {
            "description": "Competitive debating, research, and public speaking",
            "schedule": "Tuesdays, 6:00 PM - 7:30 PM",
            "max_participants": 18,
            "participants": [{"email": "oliver@mergington.edu"}, {"email": "ethan@mergington.edu"}]
        },
        "Science Club": {
            "description": "Hands-on experiments and science fair projects",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": [{"email": "sophia2@mergington.edu"}, {"email": "jack@mergington.edu"}]
        }
    }
    
    yield
    
    # Reset to original state after test
    activities.clear()
    activities.update(original_activities)
