"""적응형 학습 계획기 테스트 (규칙 기반)."""
from app.models import StudentProfile
from app.planner import build_plan


def test_weak_subject_gets_more_time():
    p = StudentProfile(age_years=14, achievements={"수학": "부족", "영어": "잘함"}, weekly_hours=10)
    plan = build_plan(p)
    by = {s.subject: s for s in plan.sessions}
    assert by["수학"].weekly_hours > by["영어"].weekly_hours  # 약점에 더 배분
    assert plan.mode == "academic"


def test_total_matches_weekly_hours():
    p = StudentProfile(age_years=12, achievements={"수학": "보통", "국어": "보통"}, weekly_hours=8)
    plan = build_plan(p)
    assert abs(plan.total_weekly_hours - 8) <= 1.0  # 반올림 오차 허용


def test_strong_subject_in_review():
    p = StudentProfile(age_years=15, achievements={"수학": "잘함"})
    plan = build_plan(p)
    assert any("수학" in r for r in plan.review)


def test_default_subjects_when_no_achievements():
    p = StudentProfile(age_years=9)  # 초3, 성취 미입력
    plan = build_plan(p)
    assert plan.sessions and all(s.level == "기본" for s in plan.sessions)


def test_sessions_have_free_resource():
    p = StudentProfile(age_years=16, achievements={"수학": "부족"})
    plan = build_plan(p)
    s = plan.sessions[0]
    assert s.resource and s.resource.url  # 무료 자료 링크 포함


def test_developmental_mode_for_infant_and_preschool():
    assert build_plan(StudentProfile(age_years=1)).mode == "developmental"
    assert build_plan(StudentProfile(age_years=5)).mode == "developmental"
