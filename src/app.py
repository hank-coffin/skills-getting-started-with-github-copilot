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
        "instructor": "Avery Collins",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "instructor": "Mason Rivera",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "instructor": "Jordan Hayes",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Sympohonic Band": {
        "description": "Develop ensemble performance skills while rehearsing concert repertoire for school and community showcases.",
        "instructor": "Isla Bennett",
        "schedule": "Mondays and Wednesdays, 3:00 PM - 5:00 PM",
        "max_participants": 33,
        "participants": [
            "nora.hale@mergington.edu",
            "liam.brooks@mergington.edu",
            "tessa.reed@mergington.edu",
            "caleb.nguyen@mergington.edu",
            "maya.voss@mergington.edu",
            "evan.ward@mergington.edu",
            "riley.kim@mergington.edu",
            "zoe.patel@mergington.edu",
            "asher.ford@mergington.edu"
        ]
    },
    "Orchestra": {
        "description": "Perform orchestral works with a focus on tone, blend, and collaborative musicianship across sections.",
        "instructor": "Caleb Foster",
        "schedule": "Tuesdays and Thursdays, 2:00 PM - 4:00 PM",
        "max_participants": 15,
        "participants": [
            "amelia.price@mergington.edu",
            "logan.rivera@mergington.edu",
            "harper.bennett@mergington.edu",
            "owen.carter@mergington.edu",
            "ella.morris@mergington.edu",
            "jackson.ellis@mergington.edu",
            "scarlett.watts@mergington.edu",
            "leo.hughes@mergington.edu",
            "violet.fisher@mergington.edu",
            "mason.graham@mergington.edu",
            "grace.dixon@mergington.edu",
            "henry.ortiz@mergington.edu",
            "chloe.bishop@mergington.edu",
            "isaac.wheeler@mergington.edu",
            "lily.mitchell@mergington.edu"
        ]
    },
    "Jazz Band": {
        "description": "Learn improvisation, rhythm section dynamics, and classic jazz standards in a small-group setting.",
        "instructor": "Naomi Brooks",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
        "max_participants": 22,
        "participants": [
            "noah.holt@mergington.edu",
            "aria.coleman@mergington.edu",
            "ezra.simmons@mergington.edu",
            "ruby.fuller@mergington.edu",
            "adam.choi@mergington.edu",
            "naomi.lowe@mergington.edu"
        ]
    },
    "Acting": {
        "description": "Build stage confidence through scene study, character work, and live performance exercises.",
        "instructor": "Ethan Mercer",
        "schedule": "Mondays and Wednesdays, 2:00 PM - 4:00 PM",
        "max_participants": 27,
        "participants": []
    },
    "Musical": {
        "description": "Combine acting, singing, and choreography to prepare and perform a full musical production.",
        "instructor": "Lila Chapman",
        "schedule": "Tuesdays and Thursdays, 3:00 PM - 5:00 PM",
        "max_participants": 36,
        "participants": []
    },
    "Poetry Jam": {
        "description": "Write, workshop, and perform original poetry with emphasis on spoken-word delivery and expression.",
        "instructor": "Noah Gallagher",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 6:00 PM",
        "max_participants": 19,
        "participants": [
            "sienna.cross@mergington.edu",
            "julian.peck@mergington.edu",
            "leah.mercer@mergington.edu",
            "xavier.knox@mergington.edu"
        ]
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Normalize email for comparison (trimmed + case-insensitive)
    normalized_email = email.strip().lower()

    # Prevent duplicate signups for the same activity
    if any(participant.strip().lower() == normalized_email for participant in activity["participants"]):
        raise HTTPException(status_code=400, detail="Student is already signed up for this activity")

    # Add student
    activity["participants"].append(email.strip())
    return {"message": f"Signed up {email} for {activity_name}"}
