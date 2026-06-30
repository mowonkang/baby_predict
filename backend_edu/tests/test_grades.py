"""학년별 가이드 테스트."""
from app.grades import build_grade_plan, core_subjects, grade_for_age


def test_grade_for_age():
    assert grade_for_age(1).key == "i"   # 영아(0~2)
    assert grade_for_age(5).key == "k"
    assert grade_for_age(7).key == "e1"
    assert grade_for_age(9).key == "e3"
    assert grade_for_age(13).key == "m1"
    assert grade_for_age(16).key == "h1"
    assert grade_for_age(18).key == "h3"
    assert grade_for_age(30).key == "h3"  # 클램프


def test_core_subjects_by_grade():
    assert core_subjects(grade_for_age(5)) == ["한글", "기초수", "독서"]
    assert "과학" not in core_subjects(grade_for_age(7))  # 초1
    assert "과학" in core_subjects(grade_for_age(9))       # 초3


def test_grade_plan_each_grade():
    for age in [5, 8, 11, 14, 17]:
        gp = build_grade_plan(age)
        assert gp.todo and gp.subjects and gp.tip


def test_grade_plan_by_key_override():
    gp = build_grade_plan(7, grade_key="h3")
    assert gp.grade == "고3"


def test_high_grade_plan_mentions_naesin_or_suneung():
    gp = build_grade_plan(16)  # 고1
    text = " ".join(gp.todo)
    assert "내신" in text or "수능" in text
