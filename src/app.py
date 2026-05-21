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
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
        "waitlist": []
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "instructor": "Mason Rivera",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"],
        "waitlist": []
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "instructor": "Jordan Hayes",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"],
        "waitlist": []
    },
    "Symphonic Band": {
        "description": "Develop ensemble performance skills while rehearsing concert repertoire for school and community showcases.",
        "instructor": "Isla Bennett",
        "schedule": "Mondays and Wednesdays, 3:00 PM - 5:00 PM",
        "requires_audition": True,
        "max_participants": 33,
        "auditioned": [
            "nora.hale@mergington.edu",
            "liam.brooks@mergington.edu",
            "tessa.reed@mergington.edu",
            "caleb.nguyen@mergington.edu"
        ],
        "participants": [
            "maya.voss@mergington.edu",
            "evan.ward@mergington.edu",
            "riley.kim@mergington.edu",
            "zoe.patel@mergington.edu",
            "asher.ford@mergington.edu"
        ],
        "waitlist": []
    },
    "Orchestra": {
        "description": "Perform orchestral works with a focus on tone, blend, and collaborative musicianship across sections.",
        "instructor": "Caleb Foster",
        "schedule": "Tuesdays and Thursdays, 2:00 PM - 4:00 PM",
        "requires_audition": True,
        "max_participants": 15,
        "auditioned": [
            "amelia.price@mergington.edu",
            "logan.rivera@mergington.edu",
            "harper.bennett@mergington.edu",
            "owen.carter@mergington.edu",
            "ella.morris@mergington.edu",
            "jackson.ellis@mergington.edu",
            "scarlett.watts@mergington.edu"
        ],
        "participants": [
            "leo.hughes@mergington.edu",
            "violet.fisher@mergington.edu",
            "mason.graham@mergington.edu",
            "grace.dixon@mergington.edu",
            "henry.ortiz@mergington.edu",
            "chloe.bishop@mergington.edu",
            "isaac.wheeler@mergington.edu",
            "lily.mitchell@mergington.edu"
        ],
        "waitlist": [
            "ryan.nash@mergington.edu",
            "clara.woods@mergington.edu"
        ]
    },
    "Jazz Band": {
        "description": "Learn improvisation, rhythm section dynamics, and classic jazz standards in a small-group setting.",
        "instructor": "Naomi Brooks",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
        "requires_audition": True,
        "max_participants": 22,
        "auditioned": [
            "noah.holt@mergington.edu",
            "aria.coleman@mergington.edu",
            "ezra.simmons@mergington.edu"
        ],
        "participants": [
            "ruby.fuller@mergington.edu",
            "adam.choi@mergington.edu",
            "naomi.lowe@mergington.edu"
        ],
        "waitlist": []
    },
    "Acting": {
        "description": "Build stage confidence through scene study, character work, and live performance exercises.",
        "instructor": "Ethan Mercer",
        "schedule": "Mondays and Wednesdays, 2:00 PM - 4:00 PM",
        "max_participants": 27,
        "participants": [],
        "waitlist": []
    },
    "Musical": {
        "description": "Combine acting, singing, and choreography to prepare and perform a full musical production.",
        "instructor": "Lila Chapman",
        "schedule": "Tuesdays and Thursdays, 3:00 PM - 5:00 PM",
        "max_participants": 36,
        "participants": [],
        "waitlist": []
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
        ],
        "waitlist": []
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.delete("/activities/{activity_name}/signup")
def remove_from_activity(activity_name: str, email: str):
    """Remove a student from an activity"""
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    activity = activities[activity_name]
    normalized_email = email.strip().lower()

    for lst in (activity["participants"], activity.get("auditioned", [])):
        for i, p in enumerate(lst):
            if p.strip().lower() == normalized_email:
                lst.pop(i)
                return {"message": f"Removed {email} from {activity_name}"}

    raise HTTPException(status_code=404, detail="Participant not found in activity")


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]
    waitlist = activity.setdefault("waitlist", [])
    max_waitlist_size = 5

    # Normalize email for comparison (trimmed + case-insensitive)
    normalized_email = email.strip().lower()

    # Prevent duplicate signups for the same activity
    if any(participant.strip().lower() == normalized_email for participant in activity["participants"]):
        raise HTTPException(status_code=400, detail="Student is already signed up for this activity")

    # Prevent duplicate waitlist entries
    if any(waitlisted.strip().lower() == normalized_email for waitlisted in waitlist):
        raise HTTPException(status_code=400, detail="Student is already on the waitlist for this activity")

    cleaned_email = email.strip()

    # If space is available, add as participant
    if len(activity["participants"]) < activity["max_participants"]:
        activity["participants"].append(cleaned_email)
        return {"message": f"Signed up {cleaned_email} for {activity_name}"}

    # If class is full but waitlist has room, add to waitlist
    if len(waitlist) < max_waitlist_size:
        waitlist.append(cleaned_email)
        return {
            "message": f"{activity_name} is full. Added {cleaned_email} to waitlist at position {len(waitlist)}.",
            "waitlist_position": len(waitlist)
        }

    # Both class and waitlist are full
    raise HTTPException(status_code=400, detail="Activity and waitlist are full")
