"""적성 진단 스코어링 테스트."""
from app.aptitude import resolve_aptitude, score_survey
from app.models import AptitudeProfile, InterestVector, SurveyAnswer


def _ans(qid: str, v: int) -> SurveyAnswer:
    return SurveyAnswer(question_id=qid, value=v)


def test_empty_survey_is_neutral():
    p = score_survey([])
    assert p.interest.as_dict() == {k: 0.5 for k in p.interest.as_dict()}
    assert p.learning_style.as_dict() == {k: 0.5 for k in p.learning_style.as_dict()}


def test_high_investigative():
    # i_i1, i_i2 둘 다 정채점 5 → 탐구형 1.0
    p = score_survey([_ans("i_i1", 5), _ans("i_i2", 5)])
    assert p.interest.investigative == 1.0


def test_reverse_question():
    # i_r2 는 역채점. 5 → 0.0, i_r1=5 → 1.0, 평균 0.5
    p = score_survey([_ans("i_r1", 5), _ans("i_r2", 5)])
    assert p.interest.realistic == 0.5


def test_learning_style_self_direction():
    p = score_survey([_ans("s_sd1", 5), _ans("s_sd2", 1)])
    assert p.learning_style.self_direction == 1.0


def test_unknown_question_ignored():
    p = score_survey([_ans("nope", 5), _ans("i_a1", 5), _ans("i_a2", 5)])
    assert p.interest.artistic == 1.0
    assert p.interest.social == 0.5


def test_top_types_ordering():
    vec = InterestVector(investigative=0.9, realistic=0.7, artistic=0.2)
    assert vec.top_types(2) == ["investigative", "realistic"]


def test_resolve_prefers_explicit():
    explicit = AptitudeProfile(interest=InterestVector(artistic=0.95))
    out = resolve_aptitude([_ans("i_i1", 5)], explicit)
    assert out.interest.artistic == 0.95
