"""육성 엔진(능력치 스탯 + 사교육 테크트리) 테스트."""
from app.models import StudentProfile
from app.stats import STAT_AXES, build_stats
from app.techtree import build_techtree


def test_stats_has_eight_axes():
    s = build_stats(StudentProfile(age_years=10))
    assert len(s.axes) == 8
    assert [a.key for a in s.axes] == [k for k, _ in STAT_AXES]
    assert all(5 <= a.value <= 100 for a in s.axes)


def test_science_interest_raises_science_stat():
    base = {a.key: a.value for a in build_stats(StudentProfile(age_years=12)).axes}
    sci = {a.key: a.value for a in build_stats(
        StudentProfile(age_years=12, interests=["act_sci", "act_math"])).axes}
    assert sci["science"] > base["science"]
    assert "탐구" in [a.label for a in build_stats(
        StudentProfile(age_years=12, interests=["act_sci", "act_math"])).axes if a.top]


def test_extracurricular_raises_matching_stat():
    # 태권도 → 신체, 피아노 → 예술
    s = build_stats(StudentProfile(age_years=8, activities=["ex_taekwondo", "ex_music"]))
    d = {a.key: a.value for a in s.axes}
    assert d["physical"] > 40 and d["art"] > 40
    assert "사교육/활동 경험" in s.source_signals


def test_achievement_feeds_stats():
    s = build_stats(StudentProfile(age_years=14, achievements={"수학": "잘함"}))
    d = {a.key: a.value for a in s.axes}
    assert d["logic"] > 40
    assert "과목 성취도" in s.source_signals


def test_cold_start_is_flat_explorer():
    s = build_stats(StudentProfile(age_years=10))
    assert not s.top_axes            # 강점 없음
    assert "탐색형" in s.headline
    assert all(a.value == 40 for a in s.axes)


def test_techtree_tracks_and_route():
    r = build_techtree(StudentProfile(age_years=10, interests=["act_sci"]))
    assert len(r.tracks) == 6
    # 각 트랙은 tier 0~3 노드 보유
    for tr in r.tracks:
        assert [n.tier for n in tr.nodes] == [0, 1, 2, 3]
    # 추천 루트가 있고, 초등(=tier1) 노드가 포함
    assert r.route
    assert any(n.tier == 1 for n in r.route)
    assert all(n.recommended for n in r.route)


def test_techtree_route_matches_age_tier():
    # 고등(17세) → tier 3 노드가 루트에 나와야
    r = build_techtree(StudentProfile(age_years=17, interests=["act_art"]))
    assert any(n.tier == 3 for n in r.route)
    assert "예술" in r.recommended_tracks


def test_techtree_cold_start_has_default_route():
    r = build_techtree(StudentProfile(age_years=6))
    assert r.route                    # 콜드스타트도 기본 루트 제공
    assert r.recommended_tracks
