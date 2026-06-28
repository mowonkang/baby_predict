"""성향 진단 스코어링 테스트."""
from app.models import SurveyAnswer, TemperamentVector
from app.temperament import resolve_temperament, score_survey


def _ans(qid: str, v: int) -> SurveyAnswer:
    return SurveyAnswer(question_id=qid, value=v)


def test_empty_survey_is_neutral():
    vec = score_survey([])
    assert vec.activity == 0.5
    assert vec.as_dict() == {k: 0.5 for k in vec.as_dict()}


def test_high_activity_scoring():
    # q1(정채점)=5, q2(역채점)=1  → 둘 다 활동성 1.0 신호
    vec = score_survey([_ans("q1", 5), _ans("q2", 1)])
    assert vec.activity == 1.0


def test_low_activity_scoring():
    vec = score_survey([_ans("q1", 1), _ans("q2", 5)])
    assert vec.activity == 0.0


def test_reverse_question_balances():
    # q1=5 (1.0), q2=5 (역채점→0.0) → 평균 0.5
    vec = score_survey([_ans("q1", 5), _ans("q2", 5)])
    assert vec.activity == 0.5


def test_unknown_question_ignored():
    vec = score_survey([_ans("nope", 5), _ans("q9", 5)])
    assert vec.mood == 1.0  # q9 만 반영
    assert vec.activity == 0.5  # 미응답 차원은 중립


def test_resolve_prefers_explicit():
    explicit = TemperamentVector(activity=0.9)
    out = resolve_temperament([_ans("q1", 1)], explicit)
    assert out.activity == 0.9
