"""Access checks for the fee-enquiry API.

Run from backend/:

    pytest ../docs/qa/test_access.py
"""

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from starlette.testclient import TestClient

from app.api.auth.auth import router as auth_router
from app.api.transaction.transaction import router as transaction_router
from app.main import http_exception_handler, validation_exception_handler

NORTH = "merchant.north@fakebank.local"
NORTH_PASSWORD = "LocalNorth#2026"
EAST_REFS = {
    "NSP-SHORT-0001",
    "CDG-FEEHIKE-0001",
    "CDG-FEEHIKE-0002",
    "CDG-FAIL-0001",
}


def client() -> TestClient:
    application = FastAPI()
    application.include_router(auth_router, prefix="/api/v1")
    application.include_router(transaction_router, prefix="/api/v1")
    application.add_exception_handler(HTTPException, http_exception_handler)
    application.add_exception_handler(RequestValidationError, validation_exception_handler)
    return TestClient(application)


def test_login_rejects_wrong_password() -> None:
    response = client().post(
        "/api/v1/auth/login",
        json={"email": NORTH, "password": "wrong-password"},
    )

    assert response.status_code == 401
    body = response.json()
    assert body["status"] == "error"
    assert body["data"]["message"] == "Invalid email or password"
    assert "access_token" not in response.text


def test_merchant_cannot_list_another_merchants_transactions() -> None:
    with client() as api:
        login = api.post(
            "/api/v1/auth/login",
            json={"email": NORTH, "password": NORTH_PASSWORD},
        )
        assert login.status_code == 200
        token = login.json()["data"]["access_token"]

        refs: set[str] = set()
        page = 1
        while True:
            listed = api.get(
                "/api/v1/transactions",
                params={"page": page, "page_size": 100},
                headers={"Authorization": f"Bearer {token}"},
            )
            assert listed.status_code == 200
            data = listed.json()["data"]
            refs.update(item["txn_ref"] for item in data["items"])
            if page * data["page_size"] >= data["total"]:
                break
            page += 1

    assert "NSP-FX-0001" in refs
    assert refs.isdisjoint(EAST_REFS)
