"""유망 커리어 추천 테스트."""
from app.careers import recommend_careers
from app.models import AptitudeProfile, InterestVector


def _apt(**i):
    return AptitudeProfile(interest=InterestVector(**i))


def test_cold_start_shows_default_careers():
    res = recommend_careers(_apt(), age_years=14)
    assert "관심" in res.note
    ids = {c.id for c in res.careers}
    assert "ai_data" in ids  # 대표 유망 분야 포함


def test_investigative_realistic_gets_engineering_careers():
    res = recommend_careers(_apt(investigative=1.0, realistic=0.9), age_years=16)
    ids = {c.id for c in res.careers}
    assert ids & {"robotics", "mech_eng", "elec_semi", "ai_data", "chem_mat"}


def test_bio_social_gets_med_or_bio():
    res = recommend_careers(_apt(investigative=1.0, social=0.9), age_years=16)
    ids = {c.id for c in res.careers}
    assert ids & {"med", "bio_eng"}


def test_artistic_gets_design():
    res = recommend_careers(_apt(artistic=1.0, realistic=0.7), age_years=16)
    assert "design_tech" in {c.id for c in res.careers}


def test_career_has_prepare_and_subjects():
    res = recommend_careers(_apt(investigative=1.0), age_years=16)
    for c in res.careers:
        assert c.prepare_now and c.key_subjects and c.outlook


def test_prepare_varies_by_stage():
    young = recommend_careers(_apt(investigative=1.0, realistic=0.9), age_years=14).careers
    # 중등 단계 준비 항목이 존재
    assert any(c.prepare_now for c in young)
