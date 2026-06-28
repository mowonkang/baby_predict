"""API 통합 테스트 (FastAPI TestClient)."""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_survey_endpoint():
    res = client.get("/api/survey")
    assert res.status_code == 200
    body = res.json()
    assert len(body["questions"]) == 10
    assert body["scale"]["max"] == 5


def test_recommend_endpoint():
    payload = {
        "age_months": 10,
        "survey": [
            {"question_id": "q1", "value": 5},
            {"question_id": "q2", "value": 1},
        ],
        "budget_max": 100000,
    }
    res = client.post("/api/recommend", json=payload)
    assert res.status_code == 200
    body = res.json()
    assert body["age_band"] == "10~12개월"
    assert body["temperament"]["activity"] == 1.0
    assert len(body["recommendations"]) > 0
    assert all(r["price"] <= 100000 for r in body["recommendations"])


def test_recommend_validation_error():
    # 월령 범위 초과 → 422
    res = client.post("/api/recommend", json={"age_months": 999})
    assert res.status_code == 422
