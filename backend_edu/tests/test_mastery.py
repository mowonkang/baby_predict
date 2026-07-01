"""BKT 숙련추적 + 미니 진단 + 페르소나 테스트."""
from app.diagnostic import grade_answer, items_for
from app.mastery import bkt_update, level_from_mastery, mastery_from_seq, p_correct_next
from app.models import StudentProfile
from app.persona import build_persona


def test_bkt_correct_raises_mastery():
    assert bkt_update(0.3, True) > 0.3
    assert bkt_update(0.3, False) < bkt_update(0.3, True)


def test_all_correct_high_mastery():
    m = mastery_from_seq([True, True, True, True])
    assert m >= 0.75 and level_from_mastery(m) == "잘함"


def test_all_wrong_low_mastery():
    m = mastery_from_seq([False, False, False])
    assert level_from_mastery(m) == "부족"


def test_p_correct_next_monotone():
    assert p_correct_next(0.9) > p_correct_next(0.2)


def test_diagnostic_items_by_band():
    elem = items_for(9)   # 초3
    high = items_for(17)  # 고2
    assert elem and high
    assert all(it.band == "초등" for it in elem)
    assert all(it.band == "고등" for it in high)
    assert not items_for(2)  # 영아 → 없음


def test_grade_answer():
    assert grade_answer("m_e1", 1) == ("수학", True)   # 24/6=4 (index1)
    assert grade_answer("m_e1", 0) == ("수학", False)
    assert grade_answer("nope", 0) is None


def test_persona_label():
    p = build_persona(StudentProfile(age_years=14, interests=["act_sci", "act_math", "sty_self"]))
    assert "탐구형" in p.persona_label
    assert "자기주도" in p.persona_label


def test_persona_cold_start_is_explorer():
    p = build_persona(StudentProfile(age_years=14))
    assert "탐색형" in p.persona_label


def test_irt_percentile_and_difficulty():
    from app.mastery import percentile, recommend_difficulty, review_interval_days
    hi = mastery_from_seq([True, True, True])
    lo = mastery_from_seq([False, False, False])
    assert percentile(hi) > percentile(lo)
    assert recommend_difficulty(hi) == "상" and recommend_difficulty(lo) == "하"
    # 숙련 낮으면 복습 더 빨리
    assert review_interval_days(lo) < review_interval_days(hi)


def test_report_builder():
    from app.report import build_report
    r = build_report(StudentProfile(age_years=14, interests=["act_sci", "act_math"],
                                    achievements={"수학": "부족", "국어": "잘함"}, weekly_hours=8))
    assert r.grade == "중2" and r.sections
    titles = " ".join(s.title for s in r.sections)
    assert "요약" in titles and "보완" in titles
