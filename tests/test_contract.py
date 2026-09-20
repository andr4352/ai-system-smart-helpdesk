import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.prediction import choose_route

def test_routes_and_validation(monkeypatch, tmp_path):
    monkeypatch.setenv("API_KEY", "test-key")
    monkeypatch.setenv("DB_PATH", str(tmp_path / "audit.db"))
    with TestClient(app) as client:
        headers = {"X-API-Key": "test-key"}
        assert client.get("/health").status_code == 401
        assert client.get("/health", headers=headers).status_code == 503
        valid = {"item_id": "TKT-42", "text": "Не могу войти в личный кабинет"}
        assert client.post("/api/v1/predict", json=valid, headers=headers).status_code == 503
        for patch in ({"text": " " * 20}, {"text": 123}, {"extra": 1}):
            assert client.post("/api/v1/predict", json=valid | patch, headers=headers).status_code == 422
        assert client.get("/metrics", headers=headers).status_code == 200
        class FakeModel:
            loaded = True
            version = "test"
            def predict(self, text):
                return "ACCOUNT", 0.9
        app.state.model = FakeModel()
        response = client.post("/api/v1/predict", json=valid, headers=headers)
        assert response.status_code == 200
        assert response.json()["route"] == "IT"
        assert client.get("/health", headers=headers).status_code == 200

@pytest.mark.parametrize("category,confidence,expected", [
    ("ACCOUNT", 0.79, ("OPERATOR", True)),
    ("ACCOUNT", 0.8, ("IT", False)),
    ("OTHER", 0.99, ("OPERATOR", True)),
])
def test_manual_review(category, confidence, expected):
    assert choose_route(category, confidence) == expected
