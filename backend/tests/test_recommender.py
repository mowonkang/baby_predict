"""추천 엔진 테스트."""
from app.developmental import get_age_band
from app.models import BabyProfile, RecommendationType, SurveyAnswer, TemperamentVector
from app.recommender import recommend


def test_age_band_boundaries():
    assert get_age_band(0).key == "0-3m"
    assert get_age_band(3).key == "0-3m"
    assert get_age_band(4).key == "4-6m"
    assert get_age_band(12).key == "10-12m"
    assert get_age_band(100).key == "24m+"  # 범위 밖 → 클램프


def test_cold_start_returns_recommendations():
    # 설문/성향 없이도(콜드스타트) 추천이 나와야 한다
    out = recommend(BabyProfile(age_months=10))
    assert len(out.recommendations) > 0
    assert out.age_band == "10~12개월"
    # 점수 내림차순 정렬 확인
    scores = [r.score for r in out.recommendations]
    assert scores == sorted(scores, reverse=True)


def test_only_age_appropriate_items():
    out = recommend(BabyProfile(age_months=2), top_k=50)
    # 2개월에 보행기(P030, 9개월+)는 나오면 안 된다
    ids = {r.item_id for r in out.recommendations}
    assert "P030" not in ids


def test_budget_filter():
    out = recommend(BabyProfile(age_months=10, budget_max=50000), top_k=50)
    assert all(r.price <= 50000 for r in out.recommendations)


def test_high_activity_boosts_active_product():
    """활동성 높은 아기는 푸시워커(P030, activity affinity +0.8) 점수가 더 높다."""
    active = TemperamentVector(activity=1.0)
    calm = TemperamentVector(activity=0.0)
    out_active = recommend(BabyProfile(age_months=12, temperament=active), top_k=50)
    out_calm = recommend(BabyProfile(age_months=12, temperament=calm), top_k=50)

    def score_of(resp, item_id):
        return next(r.score for r in resp.recommendations if r.item_id == item_id)

    assert score_of(out_active, "P030") > score_of(out_calm, "P030")


def test_recommendations_have_reasons_and_valid_type():
    out = recommend(BabyProfile(age_months=12))
    valid = {t.value for t in RecommendationType}
    for r in out.recommendations:
        assert r.reasons, "추천에는 이유가 있어야 한다"
        assert r.type.value in valid
        assert 0.0 <= r.score <= 1.0


def test_survey_drives_temperament_in_response():
    out = recommend(
        BabyProfile(age_months=12, survey=[SurveyAnswer(question_id="q1", value=5),
                                           SurveyAnswer(question_id="q2", value=1)])
    )
    assert out.temperament.activity == 1.0
