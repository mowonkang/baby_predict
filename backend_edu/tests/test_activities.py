"""쉬운 진단(선택형) + 일반계 기본 트랙 테스트."""
from app.aptitude import resolve_aptitude, score_activities
from app.models import StudentProfile
from app.pathway import build_pathway


def test_no_selection_is_neutral():
    p = score_activities([])
    assert all(abs(v - 0.5) < 1e-6 for v in p.interest.as_dict().values())


def test_science_activities_raise_investigative():
    p = score_activities(["act_sci", "act_math"])
    assert p.interest.investigative == 1.0
    assert p.interest.artistic == 0.5  # 미선택은 중립


def test_style_flag_sets_self_direction():
    p = score_activities(["sty_self"])
    assert p.learning_style.self_direction >= 0.8


def test_unknown_id_ignored():
    p = score_activities(["nope", "act_art"])
    assert p.interest.artistic == 1.0


def test_resolve_uses_interests():
    out = resolve_aptitude([], None, ["act_art"])
    assert out.interest.artistic == 1.0


def test_cold_start_pathway_is_general():
    """관심사 미선택 → 일반계 기본 트랙."""
    pw = build_pathway(StudentProfile(age_years=14))
    assert "일반계" in pw.recommended_track


def test_selected_interest_pathway_is_specific():
    pw = build_pathway(StudentProfile(age_years=14, interests=["act_sci", "act_math", "act_comp"]))
    assert "일반계" not in pw.recommended_track  # 이공계열로 좁혀짐
