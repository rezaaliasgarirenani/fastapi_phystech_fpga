"""API tests based on FastAPI TestClient."""

import os
from collections.abc import Generator

os.environ["DATABASE_URL"] = "sqlite://"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


TEST_ENGINE = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=TEST_ENGINE)


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    """Create an isolated in-memory database for each test."""
    Base.metadata.create_all(bind=TEST_ENGINE)

    def override_get_db() -> Generator[Session, None, None]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=TEST_ENGINE)


def auth_headers(client: TestClient) -> dict[str, str]:
    """Register a user and return authorization headers."""
    user_payload = {
        "email": "student@example.com",
        "full_name": "Student User",
        "password": "strong-password",
    }
    register_response = client.post("/auth/register", json=user_payload)
    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        data={"username": user_payload["email"], "password": user_payload["password"]},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def create_vendor(client: TestClient, headers: dict[str, str], name: str = "Microchip") -> int:
    """Create a vendor and return its id."""
    response = client.post(
        "/vendors/",
        headers=headers,
        json={"name": name, "country": "United States", "website": "https://example.com"},
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_register_login_and_me(client: TestClient) -> None:
    headers = auth_headers(client)

    response = client.get("/auth/me", headers=headers)

    assert response.status_code == 200
    assert response.json()["email"] == "student@example.com"


def test_vendor_and_device_crud(client: TestClient) -> None:
    headers = auth_headers(client)
    vendor_id = create_vendor(client, headers)

    vendor_list = client.get("/vendors/")
    assert vendor_list.status_code == 200
    assert vendor_list.json()[0]["name"] == "Microchip"

    vendor_update = client.patch(
        f"/vendors/{vendor_id}",
        headers=headers,
        json={"website": "https://www.microchip.com"},
    )
    assert vendor_update.status_code == 200
    assert vendor_update.json()["website"] == "https://www.microchip.com"

    device_payload = {
        "vendor_id": vendor_id,
        "name": "RTG4",
        "family": "RTG4",
        "logic_cells": 150000,
        "tid_krad": 100.0,
        "max_power_w": 4.5,
        "temp_min_c": -55,
        "temp_max_c": 125,
        "package": "Ceramic CGA",
        "is_space_grade": True,
    }
    device_response = client.post("/fpga-devices/", headers=headers, json=device_payload)
    assert device_response.status_code == 201
    device_id = device_response.json()["id"]

    read_device = client.get(f"/fpga-devices/{device_id}")
    assert read_device.status_code == 200
    assert read_device.json()["vendor"]["id"] == vendor_id

    patch_device = client.patch(
        f"/fpga-devices/{device_id}",
        headers=headers,
        json={"max_power_w": 4.2},
    )
    assert patch_device.status_code == 200
    assert patch_device.json()["max_power_w"] == 4.2

    delete_device = client.delete(f"/fpga-devices/{device_id}", headers=headers)
    assert delete_device.status_code == 204


def test_mission_recommendation_business_logic(client: TestClient) -> None:
    headers = auth_headers(client)
    vendor_id = create_vendor(client, headers)

    matching_device = {
        "vendor_id": vendor_id,
        "name": "RTG4",
        "family": "RTG4",
        "logic_cells": 150000,
        "tid_krad": 100.0,
        "max_power_w": 4.5,
        "temp_min_c": -55,
        "temp_max_c": 125,
        "package": "Ceramic CGA",
        "is_space_grade": True,
    }
    high_power_device = {
        **matching_device,
        "name": "High Power Prototype",
        "logic_cells": 300000,
        "max_power_w": 20.0,
    }
    assert client.post("/fpga-devices/", headers=headers, json=matching_device).status_code == 201
    assert client.post("/fpga-devices/", headers=headers, json=high_power_device).status_code == 201

    mission_payload = {
        "name": "LEO Imaging Mission",
        "orbit": "LEO",
        "description": "Educational mission example.",
        "required_tid_krad": 50.0,
        "min_logic_cells": 100000,
        "max_power_w": 8.0,
        "required_temp_min_c": -40,
        "required_temp_max_c": 85,
    }
    mission_response = client.post("/missions/", headers=headers, json=mission_payload)
    assert mission_response.status_code == 201
    mission_id = mission_response.json()["id"]

    recommendation = client.get(f"/recommendations/mission/{mission_id}", headers=headers)

    assert recommendation.status_code == 200
    results = recommendation.json()
    assert len(results) == 1
    assert results[0]["device"]["name"] == "RTG4"
    assert results[0]["score"] > 0

