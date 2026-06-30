"""학원 추천 + 리뷰 테스트."""
from app.academies import get_reviews, recommend_academies, submit_review


def test_recommend_by_weak_subject():
    res = recommend_academies(12, "서울 강남", ["수학"], None)
    all_picks = res.sponsored + res.organic
    assert all_picks
    assert all("수학" in p.subjects for p in all_picks)


def test_sponsored_separated_and_labeled():
    res = recommend_academies(15, None, ["국어"], None)
    for p in res.sponsored:
        assert p.sponsored and any("입점" in r for r in p.reasons)
    for p in res.organic:
        assert not p.sponsored


def test_region_filter_includes_online():
    res = recommend_academies(15, "부산 해운대", ["수학"], None)
    regions = {p.region for p in res.sponsored + res.organic}
    # 부산 지역 또는 온라인만
    assert all(("부산" in r) or (r == "온라인") for r in regions)


def test_budget_filter():
    res = recommend_academies(15, None, ["국어", "영어", "수학"], 50000)
    assert all(p.price <= 50000 for p in res.sponsored + res.organic)


def test_reviews_read_and_submit():
    before = get_reviews("A001")
    assert before and before.count >= 1
    assert submit_review("A001", 5, "테스트 리뷰입니다", "강의", "고등반")
    after = get_reviews("A001")
    assert after.count == before.count + 1
    assert any("테스트 리뷰" in r.text for r in after.reviews)


def test_submit_unknown_academy():
    assert submit_review("ZZZ", 5, "x", "학원", "") is False
