import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.base import Base
from app.backend.deps import get_db
import uuid

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

def test_create_draft(client):
    """Test creating a draft"""
    draft_data = {
        "owner": "test_user",
        "payload": {"key": "value", "number": 42}
    }
    
    response = client.post("/v1/drafts", json=draft_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["owner"] == "test_user"
    assert data["payload"] == {"key": "value", "number": 42}
    assert "id" in data
    assert "updated_at" in data

def test_list_drafts(client):
    """Test listing drafts"""
    draft_data = {"owner": "test_user", "payload": {"test": True}}
    client.post("/v1/drafts", json=draft_data)
    
    response = client.get("/v1/drafts")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

def test_get_draft(client):
    """Test getting a specific draft"""
    draft_data = {"owner": "test_user", "payload": {"test": True}}
    create_response = client.post("/v1/drafts", json=draft_data)
    draft_id = create_response.json()["id"]
    
    response = client.get(f"/v1/drafts/{draft_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == draft_id
    assert data["owner"] == "test_user"

def test_update_draft(client):
    """Test updating a draft"""
    draft_data = {"owner": "test_user", "payload": {"test": True}}
    create_response = client.post("/v1/drafts", json=draft_data)
    draft_id = create_response.json()["id"]
    
    update_data = {"owner": "updated_user", "payload": {"updated": True}}
    response = client.put(f"/v1/drafts/{draft_id}", json=update_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["owner"] == "updated_user"
    assert data["payload"] == {"updated": True}

def test_delete_draft(client):
    """Test deleting a draft"""
    draft_data = {"owner": "test_user", "payload": {"test": True}}
    create_response = client.post("/v1/drafts", json=draft_data)
    draft_id = create_response.json()["id"]
    
    response = client.delete(f"/v1/drafts/{draft_id}")
    assert response.status_code == 204
    
    get_response = client.get(f"/v1/drafts/{draft_id}")
    assert get_response.status_code == 404

def test_get_nonexistent_draft(client):
    """Test getting a draft that doesn't exist"""
    fake_id = str(uuid.uuid4())
    response = client.get(f"/v1/drafts/{fake_id}")
    assert response.status_code == 404

def test_update_nonexistent_draft(client):
    """Test updating a draft that doesn't exist"""
    fake_id = str(uuid.uuid4())
    update_data = {"owner": "test", "payload": {}}
    response = client.put(f"/v1/drafts/{fake_id}", json=update_data)
    assert response.status_code == 404

def test_delete_nonexistent_draft(client):
    """Test deleting a draft that doesn't exist"""
    fake_id = str(uuid.uuid4())
    response = client.delete(f"/v1/drafts/{fake_id}")
    assert response.status_code == 404
