"""관찰형 인지 성향(WISC 착안) + 성취 하위스킬 또래비교 테스트."""
from app.cognitive import build_cognitive, items, stat_contributions
from app.models import StudentProfile
from app.stats import build_stats
from app.subskill import build_subskill_detail, options


def test_cognitive_items_cover_five_domains():
    doms = {i.domain for i in items()}
    assert doms == {"verbal", "spatial", "reasoning", "memory", "speed"}
    assert len(items()) == 10


def test_cognitive_strong_domain_high_index():
    beh = {"cg_v1": 3, "cg_v2": 3, "cg_p1": 0, "cg_p2": 0}
    p = build_cognitive(beh)
    d = {x.key: x for x in p.domains}
    assert d["verbal"].index >= 120 and d["verbal"].band in ("우수", "평균상")
    assert d["speed"].index <= 80 and d["speed"].percentile < d["verbal"].percentile
    assert "언어이해" in p.strengths and "처리속도" in p.supports


def test_cognitive_cold_start():
    p = build_cognitive({})
    assert p.answered == 0 and not p.strengths
    # 미응답 영역은 중립(index 100 근처, 백분위 50)
    assert all(x.answered == 0 for x in p.domains)


def test_cognitive_percentile_monotonic_with_index():
    p = build_cognitive({"cg_r1": 3, "cg_r2": 3, "cg_m1": 1, "cg_m2": 1})
    d = {x.key: x for x in p.domains}
    assert d["reasoning"].percentile > d["memory"].percentile


def test_behaviors_feed_stats_without_interest_click():
    """성향 클릭 없이 행동 관찰만으로 능력치가 형성돼야(과결정 방지·삼각측량)."""
    base = {a.key: a.value for a in build_stats(StudentProfile(age_years=10)).axes}
    beh = {"cg_v1": 3, "cg_v2": 3, "cg_r1": 3, "cg_r2": 3}
    s = build_stats(StudentProfile(age_years=10, behaviors=beh))
    d = {a.key: a.value for a in s.axes}
    assert d["language"] > base["language"] and d["logic"] > base["logic"]
    assert "행동 관찰(인지 성향)" in s.source_signals


def test_stat_contributions_only_above_average():
    # 낮은 응답은 가산 없음(음수 기여 방지)
    assert stat_contributions({"cg_p1": 0, "cg_p2": 0}) == {}
    assert stat_contributions({"cg_v1": 3, "cg_v2": 3}).get("language", 0) > 0


def test_subskill_options_and_detail():
    opts = options()
    assert any(o.id == "수학:연산" for o in opts)
    detail = build_subskill_detail({"수학:연산": "부족", "수학:응용": "잘함"})
    by = {d.name: d for d in detail}
    assert by["연산"].weak and "하위" in by["연산"].peer_band and by["연산"].percentile < 50
    assert not by["응용"].weak and by["응용"].percentile >= 50
    # 부족이 먼저 정렬
    assert detail[0].weak


def test_subskill_ignores_unknown():
    assert build_subskill_detail({"없음:없음": "부족", "수학:연산": "보통"}) \
        and len(build_subskill_detail({"없음:없음": "부족"})) == 0
