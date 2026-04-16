"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Dict
import json
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# Persistent activity storage
activities_file = current_dir / "activities.json"


class Activity(BaseModel):
    description: str
    schedule: str
    max_participants: int
    participants: list[str]


def load_activities() -> Dict[str, Activity]:
    if not activities_file.exists():
        raise RuntimeError("Activity storage file is missing")

    with activities_file.open("r", encoding="utf-8") as file:
        raw_data = json.load(file)

    return {name: Activity(**activity) for name, activity in raw_data.items()}


def save_activities(data: Dict[str, Activity]):
    with activities_file.open("w", encoding="utf-8") as file:
        json.dump({name: activity.dict() for name, activity in data.items()}, file, indent=2)


activities = load_activities()


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities", response_model=Dict[str, Activity])
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

    # Validate student is not already signed up
    if email in activity.participants:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )

    # Add student and save
    activity.participants.append(email)
    save_activities(activities)
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is signed up
    if email not in activity.participants:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )

    # Remove student and save
    activity.participants.remove(email)
    save_activities(activities)
    return {"message": f"Unregistered {email} from {activity_name}"}
