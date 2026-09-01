"""
Integration tests for FastAPI endpoints - Multi-step workflows using AAA pattern.
Each test uses seeded app state via seeded_activities fixture.
"""

import pytest


class TestSignupIntegration:
    """Integration tests for signup workflow."""
    
    def test_signup_flow_success_then_duplicate_fails(self, seeded_activities):
        """Test complete signup flow: signup succeeds, then duplicate signup fails."""
        # ARRANGE
        client = seeded_activities
        activity_name = "Chess Club"
        test_email = "integration_student@test.edu"
        
        # Get initial state
        activities_initial = client.get("/activities").json()
        initial_count = len(activities_initial[activity_name]["participants"])
        
        # ACT - Step 1: First signup should succeed
        response_first = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )
        
        # ASSERT - Step 1
        assert response_first.status_code == 200
        assert "Signed up" in response_first.json()["message"]
        
        # ACT - Step 2: Verify participant in list
        activities_after_first = client.get("/activities").json()
        
        # ASSERT - Step 2
        assert len(activities_after_first[activity_name]["participants"]) == initial_count + 1
        assert test_email in activities_after_first[activity_name]["participants"]
        
        # ACT - Step 3: Attempt duplicate signup
        response_duplicate = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )
        
        # ASSERT - Step 3
        assert response_duplicate.status_code == 400
        assert "already signed up" in response_duplicate.json()["detail"]
        
        # Verify participant count unchanged
        activities_after_duplicate = client.get("/activities").json()
        assert len(activities_after_duplicate[activity_name]["participants"]) == initial_count + 1
    
    def test_signup_multiple_different_students(self, seeded_activities):
        """Test that multiple different students can sign up for same activity."""
        # ARRANGE
        client = seeded_activities
        activity_name = "Basketball Team"
        student_emails = [
            "student1@test.edu",
            "student2@test.edu",
            "student3@test.edu"
        ]
        
        activities_initial = client.get("/activities").json()
        initial_count = len(activities_initial[activity_name]["participants"])
        
        # ACT - Sign up each student
        for email in student_emails:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            # ASSERT each signup succeeds
            assert response.status_code == 200
        
        # ACT - Verify all are in list
        activities_final = client.get("/activities").json()
        
        # ASSERT
        assert len(activities_final[activity_name]["participants"]) == initial_count + len(student_emails)
        for email in student_emails:
            assert email in activities_final[activity_name]["participants"]


class TestRemoveIntegration:
    """Integration tests for removal workflow."""
    
    def test_signup_then_remove_participant(self, seeded_activities):
        """Test complete lifecycle: signup then remove participant."""
        # ARRANGE
        client = seeded_activities
        activity_name = "Programming Class"
        test_email = "lifecycle_student@test.edu"
        
        # ACT - Step 1: Sign up
        response_signup = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )
        
        # ASSERT - Step 1
        assert response_signup.status_code == 200
        
        activities_after_signup = client.get("/activities").json()
        signup_count = len(activities_after_signup[activity_name]["participants"])
        assert test_email in activities_after_signup[activity_name]["participants"]
        
        # ACT - Step 2: Remove participant
        response_remove = client.delete(
            f"/activities/{activity_name}/participants/{test_email}"
        )
        
        # ASSERT - Step 2
        assert response_remove.status_code == 200
        assert "Removed" in response_remove.json()["message"]
        
        activities_after_remove = client.get("/activities").json()
        remove_count = len(activities_after_remove[activity_name]["participants"])
        assert remove_count == signup_count - 1
        assert test_email not in activities_after_remove[activity_name]["participants"]
        
        # ACT - Step 3: Try to remove already-removed participant
        response_second_remove = client.delete(
            f"/activities/{activity_name}/participants/{test_email}"
        )
        
        # ASSERT - Step 3
        assert response_second_remove.status_code == 404
        assert "Participant not found" in response_second_remove.json()["detail"]
    
    def test_remove_then_resign_same_student(self, seeded_activities):
        """Test that a student can sign up again after being removed."""
        # ARRANGE
        client = seeded_activities
        activity_name = "Tennis Club"
        test_email = "returnstudent@test.edu"
        
        # ACT - Step 1: First signup
        response_signup1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )
        
        # ASSERT - Step 1
        assert response_signup1.status_code == 200
        
        # ACT - Step 2: Remove
        response_remove = client.delete(
            f"/activities/{activity_name}/participants/{test_email}"
        )
        
        # ASSERT - Step 2
        assert response_remove.status_code == 200
        
        activities_after_remove = client.get("/activities").json()
        assert test_email not in activities_after_remove[activity_name]["participants"]
        
        # ACT - Step 3: Sign up again
        response_signup2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )
        
        # ASSERT - Step 3
        assert response_signup2.status_code == 200
        
        activities_after_resign = client.get("/activities").json()
        assert test_email in activities_after_resign[activity_name]["participants"]


class TestStateIsolation:
    """Tests to verify that modifications to one activity don't affect others."""
    
    def test_signup_one_activity_does_not_affect_others(self, seeded_activities):
        """Test that modifying one activity's participants doesn't affect another."""
        # ARRANGE
        client = seeded_activities
        activity1 = "Art Studio"
        activity2 = "Debate Club"
        test_email = "isolation_student@test.edu"
        
        activities_initial = client.get("/activities").json()
        activity2_initial_count = len(activities_initial[activity2]["participants"])
        activity2_initial_list = activities_initial[activity2]["participants"].copy()
        
        # ACT - Sign up to activity1
        response = client.post(
            f"/activities/{activity1}/signup",
            params={"email": test_email}
        )
        
        # ASSERT
        assert response.status_code == 200
        
        # Verify activity1 was modified
        activities_after = client.get("/activities").json()
        assert test_email in activities_after[activity1]["participants"]
        
        # Verify activity2 was NOT modified
        assert len(activities_after[activity2]["participants"]) == activity2_initial_count
        assert activities_after[activity2]["participants"] == activity2_initial_list
    
    def test_remove_one_activity_does_not_affect_others(self, seeded_activities):
        """Test that removing from one activity doesn't affect another."""
        # ARRANGE
        client = seeded_activities
        activity1 = "Music Band"
        activity2 = "Science Club"
        email_to_remove = "lucas@mergington.edu"  # In Music Band
        
        activities_initial = client.get("/activities").json()
        activity2_initial_count = len(activities_initial[activity2]["participants"])
        activity2_initial_list = activities_initial[activity2]["participants"].copy()
        
        # ACT - Remove from activity1
        response = client.delete(
            f"/activities/{activity1}/participants/{email_to_remove}"
        )
        
        # ASSERT
        assert response.status_code == 200
        
        # Verify activity1 was modified
        activities_after = client.get("/activities").json()
        assert email_to_remove not in activities_after[activity1]["participants"]
        
        # Verify activity2 was NOT modified
        assert len(activities_after[activity2]["participants"]) == activity2_initial_count
        assert activities_after[activity2]["participants"] == activity2_initial_list
