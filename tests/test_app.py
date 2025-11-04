import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_root_redirect():
    """Test that root endpoint returns the index page"""
    response = client.get("/")
    assert response.status_code == 200  # Successful response
    assert "text/html" in response.headers["content-type"]  # Should return HTML
    assert "<!DOCTYPE html>" in response.text  # Verify it's returning HTML content

def test_get_activities():
    """Test that activities endpoint returns the list of activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert "Chess Club" in activities
    assert "Programming Class" in activities

def test_signup_for_activity_success():
    """Test successful activity signup"""
    activity_name = "Chess Club"
    email = "test@mergington.edu"
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"

    # Verify the participant was added
    activities = client.get("/activities").json()
    assert email in activities[activity_name]["participants"]

def test_signup_for_activity_already_registered():
    """Test signing up when already registered"""
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # This email is already registered in the initial data
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()

def test_signup_for_nonexistent_activity():
    """Test signing up for an activity that doesn't exist"""
    activity_name = "Nonexistent Club"
    email = "test@mergington.edu"
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_unregister_from_activity_success():
    """Test successful activity unregistration"""
    # First, sign up a test user
    activity_name = "Programming Class"
    email = "test_unregister@mergington.edu"
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Then try to unregister them
    response = client.post(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"

    # Verify the participant was removed
    activities = client.get("/activities").json()
    assert email not in activities[activity_name]["participants"]

def test_unregister_not_registered():
    """Test unregistering when not registered"""
    activity_name = "Art Club"
    email = "notregistered@mergington.edu"
    response = client.post(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 400
    assert "not registered" in response.json()["detail"].lower()

def test_unregister_from_nonexistent_activity():
    """Test unregistering from an activity that doesn't exist"""
    activity_name = "Nonexistent Club"
    email = "test@mergington.edu"
    response = client.post(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()