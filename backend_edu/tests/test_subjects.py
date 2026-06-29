"""고교 과목 추천(2022 개정 구조) 테스트."""
from app.models import AptitudeProfile, InterestVector
from app.subjects import CAREER, COMMON, recommend_subjects


def _apt(**interests):
    return AptitudeProfile(interest=InterestVector(**interests))


def test_common_always_included():
    res = recommend_subjects(_apt())
    assert len(res.groups[COMMON]) >= 1
    assert all(p.course_type == COMMON for p in res.groups[COMMON])


def test_cold_start_has_fallback_general():
    res = recommend_subjects(_apt())  # 전부 중립
    assert "진단" in res.note
    # 콜드스타트엔 진로선택이 비고, 일반선택 기본 추천이 있어야
    assert len(res.groups["일반선택"]) >= 1


def test_investigative_gets_science_career_subjects():
    res = recommend_subjects(_apt(investigative=1.0, realistic=0.8))
    career_names = {p.name for p in res.groups[CAREER]}
    # 탐구/현실형 → 과학·수학 진로선택이 포함돼야
    assert career_names & {"역학과 에너지", "미적분Ⅱ", "기하", "인공지능 기초", "전자기와 양자"}


def test_artistic_gets_art_subjects():
    res = recommend_subjects(_apt(artistic=1.0))
    names = {p.name for grp in res.groups.values() for p in grp}
    assert names & {"음악 연주와 창작", "미술 창작", "미술", "음악"}


def test_enterprising_gets_economy_subjects():
    res = recommend_subjects(_apt(enterprising=1.0, conventional=0.7))
    career = {p.name for p in res.groups[CAREER]}
    assert career & {"경제", "법과 사회", "경제 수학", "국제관계의 이해"}


def test_picks_have_reasons():
    res = recommend_subjects(_apt(investigative=1.0))
    for grp in res.groups.values():
        for p in grp:
            assert p.reasons
