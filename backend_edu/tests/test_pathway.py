"""교육 path 생성기 테스트."""
from app.models import AptitudeProfile, InterestVector, StudentProfile
from app.pathway import build_pathway


def _profile(age, **interests):
    return StudentProfile(
        age_years=age, aptitude=AptitudeProfile(interest=InterestVector(**interests))
    )


def test_investigative_track_is_science():
    pw = build_pathway(_profile(11, investigative=0.95, realistic=0.6))
    assert "이공" in pw.recommended_track or "공학" in pw.recommended_track


def test_artistic_track():
    pw = build_pathway(_profile(11, artistic=0.95))
    assert "예술" in pw.recommended_track


def test_enterprising_social_maps_to_business():
    pw = build_pathway(_profile(13, enterprising=0.95, social=0.8))
    assert "경영" in pw.recommended_track


def test_pathway_runs_to_university():
    pw = build_pathway(_profile(11, investigative=0.9))
    stages = [m.stage for m in pw.milestones]
    assert stages[0] == "초등 고학년"  # 현재 단계부터 시작
    assert stages[-1] == "대학"        # 대학까지 이어짐


def test_pathway_has_decision_points():
    pw = build_pathway(_profile(11, investigative=0.9))
    decisions = [m.decision for m in pw.milestones if m.decision]
    assert len(decisions) >= 1  # 중등/고등 등 의사결정 포인트 존재


def test_pathway_milestones_have_focus():
    pw = build_pathway(_profile(14, social=0.9))
    for m in pw.milestones:
        assert m.focus, "각 마일스톤에는 집중 영역이 있어야 한다"


def test_decision_reflects_real_system():
    """중등 이전(초등 고학년) 학생의 path에 실제 제도 기반 의사결정(고교 유형)이 포함된다."""
    pw = build_pathway(_profile(11, investigative=0.9))
    decisions = " ".join(m.decision for m in pw.milestones if m.decision)
    assert "고교" in decisions
    assert "2028" in decisions  # 2028 통합형 수능·내신 5등급제 반영
