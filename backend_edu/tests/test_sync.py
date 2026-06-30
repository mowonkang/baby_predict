"""동기화 코드 서버 저장 테스트."""
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_sync_save_and_load():
    payload = {"name": "테스트아이", "history": [{"date": "2026-06-30", "ach": {"수학": "부족"}}]}
    r = client.post("/api/sync/save", json={"code": "pytest-code-123", "payload": payload})
    assert r.status_code == 200 and r.json()["ok"]
    r2 = client.get("/api/sync/pytest-code-123")
    assert r2.status_code == 200
    assert r2.json()["payload"]["name"] == "테스트아이"


def test_sync_unknown_code_404():
    r = client.get("/api/sync/no-such-code-xyz")
    assert r.status_code == 404


def test_sync_empty_code_400():
    r = client.post("/api/sync/save", json={"code": "  ", "payload": {}})
    assert r.status_code == 400
