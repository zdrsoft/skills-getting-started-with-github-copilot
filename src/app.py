"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
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

    # Sports activities
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

    # Artistic activities
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

    # Intellectual activities
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


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str, username: str = None):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Helper to check if email already exists in participants
    def email_exists(email, participants):
        for p in participants:
            if isinstance(p, dict):
                if p.get("email") == email:
                    return True
            elif p == email:
                return True
        return False

    # Validate student is not already signed up
    if email_exists(email, activity["participants"]):
        raise HTTPException(status_code=400, detail="Student is already signed up")

    # Optional: enforce max participants
    if len(activity["participants"]) >= activity.get("max_participants", 0):
        raise HTTPException(status_code=400, detail="Activity is full")

    # Add student as object with email and optional username
    participant_entry = {"email": email}
    if username:
        participant_entry["username"] = username
    activity["participants"].append(participant_entry)
    return {"message": f"Signed up {email} for {activity_name}", "participant": participant_entry}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Find and remove the participant
    for i, participant in enumerate(activity["participants"]):
        if isinstance(participant, dict):
            if participant.get("email") == email:
                activity["participants"].pop(i)
                return {"message": f"Unregistered {email} from {activity_name}"}
        elif participant == email:
            activity["participants"].pop(i)
            return {"message": f"Unregistered {email} from {activity_name}"}

    raise HTTPException(status_code=404, detail="Participant not found")
