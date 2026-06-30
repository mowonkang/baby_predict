"""성취도 기반 보완·교육 추천 테스트."""
from app.achievement import build_achievement


def test_weak_subject_recommended():
    res = build_achievement(14, {"수학": "부족", "영어": "보통", "국어": "잘함"})
    weak_subjects = {w.subject for w in res.weak}
    assert "수학" in weak_subjects and "영어" in weak_subjects
    assert "국어" in res.strong


def test_weak_sorted_before_ok():
    res = build_achievement(14, {"영어": "보통", "수학": "부족"})
    assert res.weak[0].level == "부족"  # 부족이 먼저


def test_free_options_present_and_emphasized():
    res = build_achievement(14, {"수학": "부족"})
    math = res.weak[0]
    assert math.free  # 무료/저렴 옵션 존재
    assert any("무료" in o.cost for o in math.free)
    assert "무료" in res.note or "저렴" in res.note


def test_paid_options_present():
    res = build_achievement(14, {"수학": "부족"})
    assert res.weak[0].paid  # 학원/인강 후보(또는 비교 안내)


def test_level_aliases():
    res = build_achievement(14, {"수학": "하", "영어": "상"})
    assert res.weak and res.weak[0].subject == "수학"
    assert "영어" in res.strong


def test_all_good_note():
    res = build_achievement(14, {"수학": "잘함", "영어": "잘함"})
    assert not res.weak
    assert "강점" in res.note


def test_free_options_have_links():
    res = build_achievement(14, {"수학": "부족"})
    assert any(o.url.startswith("http") for o in res.weak[0].free)


def test_infant_uses_childcare_resource():
    res = build_achievement(1, {"애착·정서": "부족"})
    assert any("아이사랑" in o.name for o in res.weak[0].free)


def test_free_resources_vary_by_school_level():
    """같은 수학이라도 초등 vs 고등 무료자원이 달라야 한다."""
    elem = build_achievement(9, {"수학": "부족"}).weak[0].free   # 초3
    high = build_achievement(17, {"수학": "부족"}).weak[0].free  # 고2
    elem_names = {o.name for o in elem}
    high_names = {o.name for o in high}
    assert "똑똑! 수학탐험대" in elem_names    # 초등 전용
    assert "EBSi 고교" in high_names          # 고등 전용
    assert elem_names != high_names
