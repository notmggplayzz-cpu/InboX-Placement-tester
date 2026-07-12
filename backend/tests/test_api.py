import pytest
from app.database.models import GmailAccount, TestCampaign, TestStatusEnum
from datetime import datetime


def test_health_check(test_client):
    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root(test_client):
    response = test_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_list_accounts_empty(test_client):
    response = test_client.get("/api/accounts")
    assert response.status_code == 200
    assert response.json() == []


def test_list_tests_empty(test_client):
    response = test_client.get("/api/tests")
    assert response.status_code == 200
    assert response.json() == []


def test_create_test(test_client, test_db):
    payload = {
        "campaign_name": "Test Campaign",
        "subject": "Test Subject",
        "html_body": "<html><body>Test</body></html>",
        "plain_text_body": "Test",
        "sender_email": "test@example.com",
    }

    response = test_client.post("/api/tests", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["campaign_name"] == "Test Campaign"
    assert data["status"] == TestStatusEnum.DRAFT
    assert data["id"] is not None


def test_get_test(test_client, test_db):
    payload = {
        "campaign_name": "Test Campaign",
        "subject": "Test Subject",
        "html_body": "<html><body>Test</body></html>",
        "sender_email": "test@example.com",
    }

    create_response = test_client.post("/api/tests", json=payload)
    test_id = create_response.json()["id"]

    response = test_client.get(f"/api/tests/{test_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_id
    assert data["campaign_name"] == "Test Campaign"


def test_delete_test(test_client, test_db):
    payload = {
        "campaign_name": "Test Campaign",
        "subject": "Test Subject",
        "html_body": "<html><body>Test</body></html>",
        "sender_email": "test@example.com",
    }

    create_response = test_client.post("/api/tests", json=payload)
    test_id = create_response.json()["id"]

    delete_response = test_client.delete(f"/api/tests/{test_id}")
    assert delete_response.status_code == 200

    get_response = test_client.get(f"/api/tests/{test_id}")
    assert get_response.status_code == 404


def test_list_tests_with_filter(test_client):
    payloads = [
        {
            "campaign_name": "Campaign 1",
            "subject": "Test 1",
            "html_body": "<html></html>",
            "sender_email": "test@example.com",
        },
        {
            "campaign_name": "Campaign 2",
            "subject": "Test 2",
            "html_body": "<html></html>",
            "sender_email": "test@example.com",
        },
    ]

    for payload in payloads:
        test_client.post("/api/tests", json=payload)

    response = test_client.get("/api/tests?limit=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
