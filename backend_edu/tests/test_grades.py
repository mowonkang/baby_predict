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


def test_grade_plan_curriculum_accurate():
    # 2022 개정 교육과정 기반: 초2 곱셈구구, 초3 나눗셈·분수 도입
    assert "곱셈구구" in " ".join(build_grade_plan(8).todo)
    e3 = " ".join(build_grade_plan(9).todo)
    assert ("분수" in e3 or "나눗셈" in e3) and "영어" in e3
    # 중3 이차방정식/이차함수
    assert "이차" in " ".join(build_grade_plan(15).todo)
