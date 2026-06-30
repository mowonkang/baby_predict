"""학년별 단원 + 무료강의 링크 테스트."""
from app.units import build_units


def test_units_for_elementary_math_link_khan():
    res = build_units(9)  # 초3
    assert res.grade == "초3"
    math = [u for u in res.units if u.subject == "수학"]
    assert math and any("나눗셈" in u.name or "분수" in u.name for u in math)
    assert all(u.url.startswith("http") for u in res.units)
    assert any("khanacademy" in u.url for u in math)  # 초등 수학 → 칸아카데미


def test_units_for_middle_math_link_ebs():
    res = build_units(15)  # 중3
    math = [u for u in res.units if u.subject == "수학"]
    assert any("이차방정식" in u.name for u in math)
    assert any("ebs" in u.url.lower() for u in math)


def test_units_include_english_from_grade3():
    res = build_units(9)  # 초3 — 영어 시작
    assert any(u.subject == "영어" for u in res.units)
    res1 = build_units(7)  # 초1 — 정규 영어 없음
    assert not any(u.subject == "영어" for u in res1.units)


def test_units_have_source():
    res = build_units(9)
    assert res.source and res.updated
