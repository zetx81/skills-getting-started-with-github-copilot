import pytest
from copy import deepcopy
from fastapi.testclient import TestClient
from src.app import app, activities

@pytest.fixture(autouse=True)
def setup_teardown():
    # Arrange: Save original activities state
    original_activities = deepcopy(activities)
    
    yield
    
    # Teardown: Restore original state to ensure complete test isolation
    activities.clear()
    activities.update(original_activities)


def test_root_redirect():
    # Arrange
    client = TestClient(app)

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities():
    # Arrange
    client = TestClient(app)

    # Act
    response = client.get("/activities")
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data


def test_signup_for_activity_success():
    # Arrange
    client = TestClient(app)
    activity_name = "Basketball Club"
    email = "test_student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    response_data = response.json()

    # Assert
    assert response.status_code == 200
    assert response_data == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]


def test_signup_for_activity_not_found():
    # Arrange
    client = TestClient(app)
    activity_name = "Non-existent Club"
    email = "test_student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    response_data = response.json()

    # Assert
    assert response.status_code == 404
    assert response_data["detail"] == "Activity not found"


def test_signup_for_activity_duplicate():
    # Arrange
    client = TestClient(app)
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # This email is already in the participants list

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    response_data = response.json()

    # Assert
    assert response.status_code == 400
    assert response_data["detail"] == "Student is already signed up for this activity"


def test_signup_for_activity_full():
    # Arrange
    client = TestClient(app)
    activity_name = "Chess Club"
    # Set number of participants to max capability (12)
    activities[activity_name]["participants"] = [f"student{i}@mergington.edu" for i in range(12)]
    email = "new_student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    response_data = response.json()

    # Assert
    assert response.status_code == 400
    assert response_data["detail"] == "This activity is already full"


def test_unregister_from_activity_success():
    # Arrange
    client = TestClient(app)
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Already registered

    # Act
    response = client.post(
        f"/activities/{activity_name}/unregister",
        params={"email": email}
    )
    response_data = response.json()

    # Assert
    assert response.status_code == 200
    assert response_data == {"message": f"Unregistered {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]


def test_unregister_from_activity_not_found():
    # Arrange
    client = TestClient(app)
    activity_name = "Non-existent Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/unregister",
        params={"email": email}
    )
    response_data = response.json()

    # Assert
    assert response.status_code == 404
    assert response_data["detail"] == "Activity not found"


def test_unregister_from_activity_not_registered():
    # Arrange
    client = TestClient(app)
    activity_name = "Chess Club"
    email = "not_registered@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/unregister",
        params={"email": email}
    )
    response_data = response.json()

    # Assert
    assert response.status_code == 400
    assert response_data["detail"] == "Student is not signed up for this activity"
