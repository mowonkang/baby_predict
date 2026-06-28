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
    # 흥미 12 + 학습성향 6 = 18문항
    assert len(body["questions"]) == 18
    assert body["scale"]["max"] == 5


def test_recommend_endpoint():
    payload = {
        "age_years": 14,
        "survey": [
            {"question_id": "i_i1", "value": 5},
            {"question_id": "i_i2", "value": 5},
        ],
        "budget_max": 200000,
    }
    res = client.post("/api/recommend", json=payload)
    assert res.status_code == 200
    body = res.json()
    assert body["stage"] == "중등"
    assert body["aptitude"]["interest"]["investigative"] == 1.0
    assert isinstance(body["study_mode"], str) and body["study_mode"]
    assert len(body["recommendations"]) > 0
    assert all(r["cost"] <= 200000 for r in body["recommendations"])


def test_pathway_endpoint():
    payload = {
        "age_years": 11,
        "survey": [
            {"question_id": "i_i1", "value": 5},
            {"question_id": "i_i2", "value": 5},
            {"question_id": "i_r1", "value": 5},
        ],
    }
    res = client.post("/api/pathway", json=payload)
    assert res.status_code == 200
    body = res.json()
    assert "이공" in body["pathway"]["recommended_track"] or "공학" in body["pathway"]["recommended_track"]
    assert body["pathway"]["milestones"][-1]["stage"] == "대학"


def test_recommend_validation_error():
    # 만 나이 범위 초과 → 422
    res = client.post("/api/recommend", json={"age_years": 999})
    assert res.status_code == 422
