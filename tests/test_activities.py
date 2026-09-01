"""
Unit tests for FastAPI endpoints - using AAA (Arrange-Act-Assert) pattern.
Each test uses fresh app state via app_client fixture.
"""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint."""
    
    def test_get_activities_returns_all_activities(self, app_client):
        """Test that GET /activities returns all 9 pre-populated activities."""
        # ARRANGE
        expected_activity_count = 9
        expected_keys = {"description", "schedule", "max_participants", "participants"}
        
        # ACT
        response = app_client.get("/activities")
        data = response.json()
        
        # ASSERT
        assert response.status_code == 200
        assert len(data) == expected_activity_count
        
        # Verify each activity has required keys
        for activity_name, activity_details in data.items():
            assert isinstance(activity_name, str)
            assert set(activity_details.keys()) == expected_keys
            assert isinstance(activity_details["participants"], list)
    
    def test_get_activities_contains_chess_club(self, app_client):
        """Test that Chess Club activity is present with correct initial state."""
        # ARRANGE
        expected_name = "Chess Club"
        expected_participant_count = 2
        
        # ACT
        response = app_client.get("/activities")
        data = response.json()
        
        # ASSERT
        assert expected_name in data
        assert len(data[expected_name]["participants"]) == expected_participant_count
        assert "michael@mergington.edu" in data[expected_name]["participants"]
        assert "daniel@mergington.edu" in data[expected_name]["participants"]


class TestRootRedirect:
    """Tests for GET / endpoint."""
    
    def test_root_redirects_to_static_index(self, app_client):
        """Test that GET / redirects to /static/index.html."""
        # ARRANGE
        expected_status = 307
        expected_location = "/static/index.html"
        
        # ACT
        response = app_client.get("/", follow_redirects=False)
        
        # ASSERT
        assert response.status_code == expected_status
        assert response.headers.get("location") == expected_location


class TestSignupHappyPath:
    """Tests for POST /activities/{activity_name}/signup - Happy paths."""
    
    def test_signup_valid_new_student_succeeds(self, app_client):
        """Test successful signup for a student not yet registered."""
        # ARRANGE
        activity_name = "Chess Club"
        test_email = "newstudent@test.edu"
        
        # ACT
        response = app_client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )
        
        # ASSERT
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert test_email in response.json()["message"]
    
    def test_signup_adds_participant_to_activity(self, app_client):
        """Test that signup actually adds participant to the activity list."""
        # ARRANGE
        activity_name = "Programming Class"
        test_email = "newstudent@test.edu"
        
        activities_before = app_client.get("/activities").json()
        participant_count_before = len(activities_before[activity_name]["participants"])
        
        # ACT
        response = app_client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )
        
        # ASSERT
        assert response.status_code == 200
        
        activities_after = app_client.get("/activities").json()
        participant_count_after = len(activities_after[activity_name]["participants"])
        
        assert participant_count_after == participant_count_before + 1
        assert test_email in activities_after[activity_name]["participants"]


class TestSignupErrorCases:
    """Tests for POST /activities/{activity_name}/signup - Error cases."""
    
    def test_signup_duplicate_fails_with_400(self, app_client):
        """Test that attempting to signup twice returns 400 error."""
        # ARRANGE
        activity_name = "Chess Club"
        test_email = "michael@mergington.edu"  # Already registered
        
        # ACT
        response = app_client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )
        
        # ASSERT
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_invalid_activity_fails_with_404(self, app_client):
        """Test that signup for non-existent activity returns 404 error."""
        # ARRANGE
        activity_name = "Nonexistent Activity"
        test_email = "test@test.edu"
        
        # ACT
        response = app_client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )
        
        # ASSERT
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_with_url_encoded_activity_name(self, app_client):
        """Test signup with URL-encoded activity name (spaces, special chars)."""
        # ARRANGE
        activity_name = "Chess Club"  # Has space
        test_email = "urltest@test.edu"
        
        # ACT - URL encoding handled by client
        response = app_client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )
        
        # ASSERT
        assert response.status_code == 200
        
        activities = app_client.get("/activities").json()
        assert test_email in activities[activity_name]["participants"]
    
    def test_signup_with_special_chars_in_email(self, app_client):
        """Test signup with special characters in email address."""
        # ARRANGE
        activity_name = "Tennis Club"
        test_email = "user+test@example.edu"  # Email with plus sign
        
        # ACT
        response = app_client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )
        
        # ASSERT
        assert response.status_code == 200
        
        activities = app_client.get("/activities").json()
        assert test_email in activities[activity_name]["participants"]


class TestRemoveParticipantHappyPath:
    """Tests for DELETE /activities/{activity_name}/participants/{email} - Happy paths."""
    
    def test_remove_existing_participant_succeeds(self, app_client):
        """Test successful removal of an existing participant."""
        # ARRANGE
        activity_name = "Chess Club"
        email_to_remove = "michael@mergington.edu"
        
        # ACT
        response = app_client.delete(
            f"/activities/{activity_name}/participants/{email_to_remove}"
        )
        
        # ASSERT
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]
        assert email_to_remove in response.json()["message"]
    
    def test_remove_participant_from_activity_list(self, app_client):
        """Test that remove actually removes participant from the activity list."""
        # ARRANGE
        activity_name = "Programming Class"
        email_to_remove = "emma@mergington.edu"
        
        activities_before = app_client.get("/activities").json()
        participant_count_before = len(activities_before[activity_name]["participants"])
        
        # ACT
        response = app_client.delete(
            f"/activities/{activity_name}/participants/{email_to_remove}"
        )
        
        # ASSERT
        assert response.status_code == 200
        
        activities_after = app_client.get("/activities").json()
        participant_count_after = len(activities_after[activity_name]["participants"])
        
        assert participant_count_after == participant_count_before - 1
        assert email_to_remove not in activities_after[activity_name]["participants"]


class TestRemoveParticipantErrorCases:
    """Tests for DELETE /activities/{activity_name}/participants/{email} - Error cases."""
    
    def test_remove_nonexistent_participant_fails_with_404(self, app_client):
        """Test that removing non-existent participant returns 404 error."""
        # ARRANGE
        activity_name = "Chess Club"
        email_to_remove = "nonexistent@test.edu"
        
        # ACT
        response = app_client.delete(
            f"/activities/{activity_name}/participants/{email_to_remove}"
        )
        
        # ASSERT
        assert response.status_code == 404
        assert "Participant not found" in response.json()["detail"]
    
    def test_remove_from_nonexistent_activity_fails_with_404(self, app_client):
        """Test that removing from non-existent activity returns 404 error."""
        # ARRANGE
        activity_name = "Nonexistent Activity"
        email_to_remove = "test@test.edu"
        
        # ACT
        response = app_client.delete(
            f"/activities/{activity_name}/participants/{email_to_remove}"
        )
        
        # ASSERT
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_remove_with_url_encoded_activity_name(self, app_client):
        """Test removal with URL-encoded activity name."""
        # ARRANGE
        activity_name = "Art Studio"  # Has space
        email_to_remove = "isabella@mergington.edu"
        
        # ACT
        response = app_client.delete(
            f"/activities/{activity_name}/participants/{email_to_remove}"
        )
        
        # ASSERT
        assert response.status_code == 200
        
        activities = app_client.get("/activities").json()
        assert email_to_remove not in activities[activity_name]["participants"]
    
    def test_remove_with_special_chars_in_email(self, app_client):
        """Test removal with special characters in email address."""
        # ARRANGE
        activity_name = "Science Club"
        test_email = "special+char@test.edu"
        
        # First, add the participant
        app_client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )
        
        # ACT - Now remove it
        response = app_client.delete(
            f"/activities/{activity_name}/participants/{test_email}"
        )
        
        # ASSERT
        assert response.status_code == 200
        
        activities = app_client.get("/activities").json()
        assert test_email not in activities[activity_name]["participants"]
