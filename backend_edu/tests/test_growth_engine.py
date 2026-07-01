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


def test_stats_overall_and_title():
    s = build_stats(StudentProfile(age_years=12, interests=["act_sci", "act_math"]))
    assert 5 <= s.overall <= 100
    assert s.title == "논리 전략가" or s.title == "꼬마 과학자"  # 상위축 기반
    # 콜드스타트 타이틀은 탐색가
    assert build_stats(StudentProfile(age_years=10)).title == "탐색가"


def test_techtree_marks_done_from_activities():
    # 사고력수학(think tier1) 경험 → think0·think1 done 표시
    r = build_techtree(StudentProfile(age_years=10, interests=["act_math"],
                                      activities=["ex_thinkmath"]))
    think = next(t for t in r.tracks if t.key == "think")
    done = [n for n in think.nodes if n.done]
    assert {n.tier for n in done} == {0, 1}
    assert r.done_count >= 2


def test_techtree_route_advances_past_done():
    # 이미 think tier1 경험한 초등(=나이 tier1) → 루트는 tier2부터
    r = build_techtree(StudentProfile(age_years=10, interests=["act_math"],
                                      activities=["ex_thinkmath"]))
    think_route = [n for n in r.route if n.id.startswith("think")]
    assert think_route and min(n.tier for n in think_route) == 2
    assert all(not n.done for n in r.route)  # 경험한 단계는 루트에 안 넣음


def test_techtree_budget_conscious():
    r = build_techtree(StudentProfile(age_years=10, interests=["act_math"], budget_max=100000))
    assert r.budget_conscious
    assert any("예산 절약" in n.reason for n in r.route)
    r2 = build_techtree(StudentProfile(age_years=10, interests=["act_math"]))
    assert not r2.budget_conscious
