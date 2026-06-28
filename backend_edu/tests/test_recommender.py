"""추천 엔진 테스트."""
from app.curriculum import get_stage
from app.models import (
    AptitudeProfile,
    InterestVector,
    RecommendationType,
    StudentProfile,
)
from app.recommender import recommend


def test_stage_boundaries():
    assert get_stage(5).key == "preschool"
    assert get_stage(7).key == "elem_low"
    assert get_stage(11).key == "elem_high"
    assert get_stage(14).key == "middle"
    assert get_stage(17).key == "high"
    assert get_stage(30).key == "university"  # 범위 밖 → 클램프


def test_cold_start_returns_recommendations():
    out = recommend(StudentProfile(age_years=11))
    assert len(out.recommendations) > 0
    assert out.stage == "초등 고학년"
    scores = [r.score for r in out.recommendations]
    assert scores == sorted(scores, reverse=True)


def test_only_age_appropriate_resources():
    out = recommend(StudentProfile(age_years=6), top_k=50)
    ids = {r.resource_id for r in out.recommendations}
    # 고등 수학 관리형(R030, 16세+)은 6세에게 나오면 안 된다
    assert "R030" not in ids


def test_budget_filter():
    out = recommend(StudentProfile(age_years=14, budget_max=130000), top_k=50)
    assert all(r.cost <= 130000 for r in out.recommendations)


def test_investigative_boosts_science():
    """탐구형 높은 학생은 과학 실험 키트(R014, investigative affinity)가 더 높다."""
    sci = AptitudeProfile(interest=InterestVector(investigative=1.0))
    non = AptitudeProfile(interest=InterestVector(investigative=0.0))
    out_sci = recommend(StudentProfile(age_years=11, aptitude=sci), top_k=50)
    out_non = recommend(StudentProfile(age_years=11, aptitude=non), top_k=50)

    def score_of(resp, rid):
        return next(r.score for r in resp.recommendations if r.resource_id == rid)

    assert score_of(out_sci, "R014") > score_of(out_non, "R014")


def test_reasons_and_valid_type():
    out = recommend(StudentProfile(age_years=14))
    valid = {t.value for t in RecommendationType}
    for r in out.recommendations:
        assert r.reasons
        assert r.type.value in valid
        assert 0.0 <= r.score <= 1.0


def test_free_resource_included():
    # R001(무료, 미취학 한글) 가 예산 0 필터에서 포함돼야 한다
    out = recommend(StudentProfile(age_years=5, budget_max=0), top_k=50)
    assert any(r.cost == 0 for r in out.recommendations)


def _style_profile(**style):
    from app.models import LearningStyle
    return AptitudeProfile(learning_style=LearningStyle(**style))


def test_self_directed_boosts_online_lecture():
    """자기주도 성향이 높으면 인강(R020) 점수가 더 높다."""
    hi = _style_profile(self_direction=1.0)
    lo = _style_profile(self_direction=0.0)
    out_hi = recommend(StudentProfile(age_years=14, aptitude=hi), top_k=50)
    out_lo = recommend(StudentProfile(age_years=14, aptitude=lo), top_k=50)

    def score_of(resp, rid):
        return next(r.score for r in resp.recommendations if r.resource_id == rid)

    assert score_of(out_hi, "R020") > score_of(out_lo, "R020")


def test_managed_style_boosts_academy():
    """자기주도가 낮은(관리형) 학생은 학원(R021) 점수가 더 높다."""
    managed = _style_profile(self_direction=0.0)
    independent = _style_profile(self_direction=1.0)
    out_m = recommend(StudentProfile(age_years=14, aptitude=managed), top_k=50)
    out_i = recommend(StudentProfile(age_years=14, aptitude=independent), top_k=50)

    def score_of(resp, rid):
        return next(r.score for r in resp.recommendations if r.resource_id == rid)

    assert score_of(out_m, "R021") > score_of(out_i, "R021")


def test_study_mode_summary():
    out_sd = recommend(StudentProfile(age_years=14, aptitude=_style_profile(self_direction=1.0)))
    assert "자기주도" in out_sd.study_mode
    out_mg = recommend(StudentProfile(age_years=14, aptitude=_style_profile(self_direction=0.0)))
    assert "관리" in out_mg.study_mode
