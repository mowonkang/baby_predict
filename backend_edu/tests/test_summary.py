"""통합 요약(/api/summary)·GZip·리포트 확장 테스트."""
from fastapi.testclient import TestClient

from app.main import app
from app.models import StudentProfile
from app.report import build_report

client = TestClient(app)

_KEYS = {"grade_plan", "units", "study_plan", "achievement", "recommend", "pathway",
         "subjects", "ai_track", "careers", "lifecycle", "academies", "persona",
         "techtree", "cognitive", "projection", "frameworks"}


def test_summary_returns_all_sections():
    r = client.post("/api/summary", json={
        "age_years": 10, "interests": ["act_sci", "act_math"],
        "achievements": {"수학": "부족"},
        "behaviors": {"cg_r1": 4, "tp_s1": 4, "tp_s2": 4},
        "subskills": {"수학:연산": "부족"}})
    assert r.status_code == 200
    d = r.json()
    assert _KEYS <= set(d.keys())
    # 개별 엔드포인트와 동일한 형태(스팟체크)
    assert d["grade_plan"]["grade"] and d["techtree"]["stat"]["axes"]
    assert d["achievement"]["subskill_detail"]          # 하위스킬 반영
    assert d["persona"]["temperament_label"]            # 기질 결합
    assert d["projection"]["projections"] and d["frameworks"]["frameworks"]


def test_summary_cold_start_safe():
    r = client.post("/api/summary", json={"age_years": 5})
    assert r.status_code == 200
    assert _KEYS <= set(r.json().keys())


def test_gzip_enabled_for_large_responses():
    r = client.post("/api/summary", json={"age_years": 10},
                    headers={"Accept-Encoding": "gzip"})
    assert r.headers.get("content-encoding") == "gzip"


def test_report_includes_new_sections():
    rep = build_report(StudentProfile(
        age_years=10, interests=["act_sci", "act_math"],
        achievements={"수학": "잘함"},
        behaviors={"tp_s1": 4, "tp_s2": 4, "tp_e1": 3, "tp_e2": 3}))
    titles = " ".join(s.title for s in rep.sections)
    assert "기질" in titles and "능력치" in titles and "예상 전망" in titles
    # 전망 섹션에 정직 고지 포함
    proj_sec = next(s for s in rep.sections if "예상 전망" in s.title)
    assert any("보장" in l for l in proj_sec.lines)


def test_report_skips_temperament_when_not_answered():
    rep = build_report(StudentProfile(age_years=10, interests=["act_math"]))
    titles = " ".join(s.title for s in rep.sections)
    assert "기질" not in titles
