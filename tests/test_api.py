from fastapi.testclient import TestClient

from vouch.api.app import app

client = TestClient(app)


def test_health_says_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_search_echoes_the_company():
    response = client.get("/search", params={"company": "Company 3"})

    assert response.status_code == 200
    assert response.json()["company"] == "Company 3"


def test_profile_returns_the_requested_id():
    response = client.get("/profiles/42")

    assert response.status_code == 200
    assert response.json()["id"] == 42


def test_send_referral_request_creates_a_pending_request():
    body = {"to_user_id": 7, "company_id": 3, "message": "Could you refer me?"}
    response = client.post("/referral-requests", json=body)

    assert response.status_code == 201
    assert response.json()["status"] == "pending"


def test_send_referral_request_rejects_a_missing_field():
    response = client.post("/referral-requests", json={"to_user_id": 7})

    assert response.status_code == 422
