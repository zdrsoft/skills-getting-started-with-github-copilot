"""Tests for the activities API endpoints."""
import pytest


class TestGetActivities:
    """Tests for the GET /activities endpoint."""
    
    def test_get_activities_success(self, client, reset_activities):
        """Test retrieving all activities."""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Soccer Team" in data
    
    def test_activities_have_required_fields(self, client, reset_activities):
        """Test that activities have all required fields."""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)
    
    def test_activities_have_participants(self, client, reset_activities):
        """Test that activities have initial participants."""
        response = client.get("/activities")
        data = response.json()
        
        # Chess Club should have 2 participants
        assert len(data["Chess Club"]["participants"]) == 2
        assert data["Chess Club"]["participants"][0]["email"] == "michael@mergington.edu"


class TestSignup:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_success(self, client, reset_activities):
        """Test successful signup for an activity."""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "participant" in data
        assert data["participant"]["email"] == "newstudent@mergington.edu"
    
    def test_signup_with_username(self, client, reset_activities):
        """Test signup with a username parameter."""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu&username=chess_master"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["participant"]["email"] == "newstudent@mergington.edu"
        assert data["participant"]["username"] == "chess_master"
    
    def test_signup_activity_not_found(self, client, reset_activities):
        """Test signup for non-existent activity."""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_signup_duplicate_email(self, client, reset_activities):
        """Test signup with an email already signed up."""
        response = client.post(
            "/activities/Chess%20Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_activity_full(self, client, reset_activities):
        """Test signup when activity is at max capacity."""
        # Create an activity with 1 max participant and 1 existing participant
        from app import activities
        activities["Small Activity"] = {
            "description": "Tiny activity",
            "schedule": "Some time",
            "max_participants": 1,
            "participants": [{"email": "existing@mergington.edu"}]
        }
        
        response = client.post(
            "/activities/Small%20Activity/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 400
        
        data = response.json()
        assert "Activity is full" in data["detail"]
    
    def test_signup_updates_participant_count(self, client, reset_activities):
        """Test that signup updates the participant count."""
        # Get initial count
        response_before = client.get("/activities")
        initial_count = len(response_before.json()["Chess Club"]["participants"])
        
        # Sign up
        client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        
        # Get updated count
        response_after = client.get("/activities")
        new_count = len(response_after.json()["Chess Club"]["participants"])
        
        assert new_count == initial_count + 1


class TestUnregister:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint."""
    
    def test_unregister_success(self, client, reset_activities):
        """Test successful unregistration from an activity."""
        # First, verify the participant exists
        response_before = client.get("/activities")
        initial_count = len(response_before.json()["Chess Club"]["participants"])
        
        # Unregister
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "Unregistered" in data["message"]
        
        # Verify count decreased
        response_after = client.get("/activities")
        new_count = len(response_after.json()["Chess Club"]["participants"])
        assert new_count == initial_count - 1
    
    def test_unregister_activity_not_found(self, client, reset_activities):
        """Test unregister from non-existent activity."""
        response = client.delete(
            "/activities/Nonexistent%20Activity/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_unregister_participant_not_found(self, client, reset_activities):
        """Test unregister for participant not in the activity."""
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=nonexistent@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert "Participant not found" in data["detail"]
    
    def test_unregister_then_signup_same_participant(self, client, reset_activities):
        """Test that a participant can re-signup after unregistering."""
        email = "michael@mergington.edu"
        activity = "Chess%20Club"
        
        # Unregister
        client.delete(f"/activities/{activity}/unregister?email={email}")
        
        # Verify they can sign up again
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200


class TestRoot:
    """Tests for the GET / endpoint."""
    
    def test_root_redirect(self, client):
        """Test that root redirects to static/index.html."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestIntegration:
    """Integration tests for complete workflows."""
    
    def test_full_signup_workflow(self, client, reset_activities):
        """Test complete signup workflow."""
        email = "integration@mergington.edu"
        username = "integration_user"
        activity = "Programming%20Class"
        
        # Sign up
        response = client.post(
            f"/activities/{activity}/signup?email={email}&username={username}"
        )
        assert response.status_code == 200
        
        # Verify signup
        response_activities = client.get("/activities")
        participants = response_activities.json()["Programming Class"]["participants"]
        
        # Find the new participant
        new_participant = next(
            (p for p in participants if p["email"] == email),
            None
        )
        assert new_participant is not None
        assert new_participant["username"] == username
    
    def test_full_unregister_workflow(self, client, reset_activities):
        """Test complete unregister workflow."""
        email = "integration@mergington.edu"
        activity = "Programming%20Class"
        
        # Sign up first
        client.post(f"/activities/{activity}/signup?email={email}")
        
        # Verify signup
        response = client.get("/activities")
        assert any(
            p["email"] == email
            for p in response.json()["Programming Class"]["participants"]
        )
        
        # Unregister
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == 200
        
        # Verify unregister
        response = client.get("/activities")
        assert not any(
            p["email"] == email
            for p in response.json()["Programming Class"]["participants"]
        )
