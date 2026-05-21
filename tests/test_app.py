import copy
import pytest
from starlette.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore the in-memory activities dict to its seed state after every test."""
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


# ---------------------------------------------------------------------------
# GET /activities
# ---------------------------------------------------------------------------

def test_get_activities_returns_200():
    response = client.get("/activities")
    assert response.status_code == 200


def test_get_activities_returns_all_nine():
    response = client.get("/activities")
    assert len(response.json()) == 9


def test_get_activities_contains_expected_fields():
    chess = client.get("/activities").json()["Chess Club"]
    for field in ("description", "instructor", "schedule", "max_participants", "participants", "waitlist"):
        assert field in chess


# ---------------------------------------------------------------------------
# GET / redirect
# ---------------------------------------------------------------------------

def test_root_redirects_to_static():
    response = client.get("/", follow_redirects=False)
    assert response.status_code in (301, 302, 307, 308)
    assert "/static/index.html" in response.headers["location"]


# ---------------------------------------------------------------------------
# POST /activities/{name}/signup — happy paths
# ---------------------------------------------------------------------------

def test_signup_adds_participant():
    client.post("/activities/Acting/signup?email=new@mergington.edu")
    assert "new@mergington.edu" in activities["Acting"]["participants"]


def test_signup_response_contains_email_and_activity():
    result = client.post("/activities/Acting/signup?email=test@mergington.edu").json()
    assert "test@mergington.edu" in result["message"]
    assert "Acting" in result["message"]


def test_signup_trims_whitespace_before_storing():
    client.post("/activities/Acting/signup?email=  trim@mergington.edu  ")
    assert "trim@mergington.edu" in activities["Acting"]["participants"]
    assert "  trim@mergington.edu  " not in activities["Acting"]["participants"]


# ---------------------------------------------------------------------------
# POST /activities/{name}/signup — waitlist
# ---------------------------------------------------------------------------

def test_signup_full_activity_goes_to_waitlist():
    activities["Acting"]["participants"] = [f"s{i}@mergington.edu" for i in range(27)]
    response = client.post("/activities/Acting/signup?email=waitlisted@mergington.edu")
    assert response.status_code == 200
    data = response.json()
    assert data["waitlist_position"] == 1
    assert "waitlisted@mergington.edu" in activities["Acting"]["waitlist"]


def test_signup_waitlist_position_increments():
    activities["Acting"]["participants"] = [f"s{i}@mergington.edu" for i in range(27)]
    activities["Acting"]["waitlist"] = ["first@mergington.edu"]
    response = client.post("/activities/Acting/signup?email=second@mergington.edu")
    assert response.json()["waitlist_position"] == 2


# ---------------------------------------------------------------------------
# POST /activities/{name}/signup — errors
# ---------------------------------------------------------------------------

def test_signup_unknown_activity_returns_404():
    response = client.post("/activities/Underwater Basket Weaving/signup?email=a@b.com")
    assert response.status_code == 404


def test_signup_duplicate_returns_400():
    client.post("/activities/Acting/signup?email=dup@mergington.edu")
    response = client.post("/activities/Acting/signup?email=dup@mergington.edu")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_signup_duplicate_case_insensitive():
    client.post("/activities/Acting/signup?email=DUP@Mergington.edu")
    response = client.post("/activities/Acting/signup?email=dup@mergington.edu")
    assert response.status_code == 400


def test_signup_duplicate_ignores_whitespace():
    client.post("/activities/Acting/signup?email=spaced@mergington.edu")
    response = client.post("/activities/Acting/signup?email=  spaced@mergington.edu  ")
    assert response.status_code == 400


def test_signup_duplicate_on_waitlist_returns_400():
    activities["Acting"]["participants"] = [f"s{i}@mergington.edu" for i in range(27)]
    client.post("/activities/Acting/signup?email=wl@mergington.edu")
    response = client.post("/activities/Acting/signup?email=wl@mergington.edu")
    assert response.status_code == 400
    assert "waitlist" in response.json()["detail"]


def test_signup_activity_and_waitlist_full_returns_400():
    activities["Acting"]["participants"] = [f"s{i}@mergington.edu" for i in range(27)]
    activities["Acting"]["waitlist"] = [f"w{i}@mergington.edu" for i in range(5)]
    response = client.post("/activities/Acting/signup?email=toolate@mergington.edu")
    assert response.status_code == 400
    assert "full" in response.json()["detail"].lower()


# ---------------------------------------------------------------------------
# DELETE /activities/{name}/signup — happy paths
# ---------------------------------------------------------------------------

def test_remove_participant():
    response = client.delete("/activities/Chess Club/signup?email=michael@mergington.edu")
    assert response.status_code == 200
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]


def test_remove_returns_message():
    result = client.delete("/activities/Chess Club/signup?email=michael@mergington.edu").json()
    assert "michael@mergington.edu" in result["message"]
    assert "Chess Club" in result["message"]


def test_remove_auditioned_participant():
    response = client.delete("/activities/Orchestra/signup?email=amelia.price@mergington.edu")
    assert response.status_code == 200
    assert "amelia.price@mergington.edu" not in activities["Orchestra"]["auditioned"]


def test_remove_is_case_insensitive():
    response = client.delete("/activities/Chess Club/signup?email=MICHAEL@MERGINGTON.EDU")
    assert response.status_code == 200
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]


# ---------------------------------------------------------------------------
# DELETE /activities/{name}/signup — errors
# ---------------------------------------------------------------------------

def test_remove_unknown_activity_returns_404():
    response = client.delete("/activities/Nonexistent/signup?email=a@b.com")
    assert response.status_code == 404


def test_remove_nonexistent_participant_returns_404():
    response = client.delete("/activities/Chess Club/signup?email=nobody@mergington.edu")
    assert response.status_code == 404
