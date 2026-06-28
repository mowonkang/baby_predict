"""성향(기질) 진단: 설문 → 기질 벡터 변환.

docs/추천엔진_설계.md §2.1~2.2 참조.
각 문항은 하나의 기질 차원에 매핑되며, reverse=True 면 역채점한다.
리커트 1~5 응답을 0~1 로 정규화해 차원별 평균을 낸다.
"""
from __future__ import annotations

from dataclasses import dataclass

from .models import TEMPERAMENT_DIMENSIONS, SurveyAnswer, TemperamentVector


@dataclass(frozen=True)
class Question:
    id: str
    text: str
    dimension: str
    reverse: bool = False


# MVP 진단 설문 (차원별 2문항). 운영 시 검수·문항 확대.
QUESTIONS: list[Question] = [
    Question("q1", "우리 아기는 깨어 있을 때 끊임없이 움직이는 편이다.", "activity"),
    Question("q2", "우리 아기는 가만히 안겨 있는 시간을 좋아한다.", "activity", reverse=True),
    Question("q3", "우리 아기는 수유·수면 시간이 매일 일정한 편이다.", "regularity"),
    Question("q4", "우리 아기는 하루하루 생활 리듬이 들쭉날쭉하다.", "regularity", reverse=True),
    Question("q5", "우리 아기는 새로운 장소·사람에 금방 적응한다.", "adaptability"),
    Question("q6", "우리 아기는 환경이 바뀌면 한참 동안 낯설어한다.", "adaptability", reverse=True),
    Question("q7", "우리 아기는 울거나 웃을 때 반응이 매우 강하고 크다.", "intensity"),
    Question("q8", "우리 아기는 감정 표현이 잔잔하고 조용한 편이다.", "intensity", reverse=True),
    Question("q9", "우리 아기는 평소 기분이 좋고 잘 웃는 편이다.", "mood"),
    Question("q10", "우리 아기는 자주 보채거나 짜증을 내는 편이다.", "mood", reverse=True),
]

_QUESTION_BY_ID = {q.id: q for q in QUESTIONS}


def _normalize(value: int, reverse: bool) -> float:
    """리커트 1~5 → 0~1. reverse 면 뒤집는다."""
    score = (value - 1) / 4.0
    return 1.0 - score if reverse else score


def score_survey(answers: list[SurveyAnswer]) -> TemperamentVector:
    """설문 응답을 기질 벡터로 변환. 응답 없는 차원은 0.5(중립) 유지."""
    sums: dict[str, float] = {d: 0.0 for d in TEMPERAMENT_DIMENSIONS}
    counts: dict[str, int] = {d: 0 for d in TEMPERAMENT_DIMENSIONS}

    for ans in answers:
        q = _QUESTION_BY_ID.get(ans.question_id)
        if q is None:
            continue  # 알 수 없는 문항은 무시
        sums[q.dimension] += _normalize(ans.value, q.reverse)
        counts[q.dimension] += 1

    result: dict[str, float] = {}
    for dim in TEMPERAMENT_DIMENSIONS:
        result[dim] = round(sums[dim] / counts[dim], 4) if counts[dim] else 0.5
    return TemperamentVector(**result)


def resolve_temperament(
    survey: list[SurveyAnswer], explicit: TemperamentVector | None
) -> TemperamentVector:
    """명시 벡터가 있으면 우선, 없으면 설문으로 계산. 둘 다 없으면 중립."""
    if explicit is not None:
        return explicit
    if survey:
        return score_survey(survey)
    return TemperamentVector()  # 전부 0.5
