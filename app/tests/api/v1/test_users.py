import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.models.user import User
from app.core.security import create_access_token

client = TestClient(app)


def test_get_current_user_info_unauthenticated(db: Session):
    """
    Test that an unauthenticated user cannot access the /me endpoint
    """
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_get_current_user_info_authenticated(db: Session, test_user: User):
    """
    Test that an authenticated user can access the /me endpoint
    """
    access_token = create_access_token(data={"sub": test_user.id, "email": test_user.email})
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/api/v1/users/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == test_user.email
