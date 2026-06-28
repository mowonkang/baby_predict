"""적성 진단: 설문 → 흥미(RIASEC) + 학습성향 벡터.

docs/edu/추천엔진_설계.md §2 참조.
backend/app/temperament.py 의 스코어링 패턴을 교육 도메인에 적용.
각 문항은 하나의 차원에 매핑되며 reverse=True 면 역채점. 리커트 1~5 → 0~1.
"""
from __future__ import annotations

from dataclasses import dataclass

from .models import (
    LEARNING_STYLE_DIMENSIONS,
    RIASEC_DIMENSIONS,
    AptitudeProfile,
    InterestVector,
    LearningStyle,
    SurveyAnswer,
)


@dataclass(frozen=True)
class Question:
    id: str
    text: str
    dimension: str
    reverse: bool = False


# 흥미 RIASEC: 유형당 2문항
INTEREST_QUESTIONS: list[Question] = [
    Question("i_r1", "기계·도구를 다루거나 만들고 조립하는 활동을 좋아한다.", "realistic"),
    Question("i_r2", "몸을 쓰는 실습보다 책상에 앉아 있는 게 더 좋다.", "realistic", reverse=True),
    Question("i_i1", "원리를 파고들고 '왜 그럴까'를 탐구하는 것을 즐긴다.", "investigative"),
    Question("i_i2", "수학·과학 문제를 풀 때 흥미를 느낀다.", "investigative"),
    Question("i_a1", "그림·음악·글쓰기 등 창작 활동을 좋아한다.", "artistic"),
    Question("i_a2", "정해진 틀보다 자유롭게 표현하는 것을 선호한다.", "artistic"),
    Question("i_s1", "친구를 돕거나 가르치고 함께하는 활동을 좋아한다.", "social"),
    Question("i_s2", "혼자 하는 일이 여럿이 하는 일보다 편하다.", "social", reverse=True),
    Question("i_e1", "팀을 이끌거나 새로운 일을 기획·설득하는 것을 좋아한다.", "enterprising"),
    Question("i_e2", "경쟁에서 이기고 목표를 달성하는 데 동기부여가 된다.", "enterprising"),
    Question("i_c1", "정리·계획·규칙에 따라 꼼꼼히 처리하는 것을 잘한다.", "conventional"),
    Question("i_c2", "예측 가능하고 체계적인 일을 선호한다.", "conventional"),
]

# 학습성향: 차원당 2문항
STYLE_QUESTIONS: list[Question] = [
    Question("s_sd1", "스스로 계획을 세워 공부하는 편이다.", "self_direction"),
    Question("s_sd2", "누가 챙겨주지 않으면 공부를 잘 안 하게 된다.", "self_direction", reverse=True),
    Question("s_co1", "친구들과 함께 토론하며 배우는 게 효과적이다.", "collaboration"),
    Question("s_co2", "혼자 조용히 공부할 때 가장 집중이 잘 된다.", "collaboration", reverse=True),
    Question("s_an1", "개념을 논리적으로 쪼개어 분석하는 것을 좋아한다.", "analytical"),
    Question("s_an2", "암기보다 원리 이해를 통해 익히는 것을 선호한다.", "analytical"),
]

QUESTIONS: list[Question] = INTEREST_QUESTIONS + STYLE_QUESTIONS
_QUESTION_BY_ID = {q.id: q for q in QUESTIONS}


def _normalize(value: int, reverse: bool) -> float:
    """리커트 1~5 → 0~1. reverse 면 뒤집는다."""
    score = (value - 1) / 4.0
    return 1.0 - score if reverse else score


def _score_dimensions(
    answers: list[SurveyAnswer], dimensions: tuple[str, ...]
) -> dict[str, float]:
    sums = {d: 0.0 for d in dimensions}
    counts = {d: 0 for d in dimensions}
    for ans in answers:
        q = _QUESTION_BY_ID.get(ans.question_id)
        if q is None or q.dimension not in sums:
            continue
        sums[q.dimension] += _normalize(ans.value, q.reverse)
        counts[q.dimension] += 1
    return {
        d: round(sums[d] / counts[d], 4) if counts[d] else 0.5 for d in dimensions
    }


def score_survey(answers: list[SurveyAnswer]) -> AptitudeProfile:
    """설문 응답을 적성 프로필(흥미+학습성향)로 변환. 미응답 차원은 0.5(중립)."""
    interest = _score_dimensions(answers, RIASEC_DIMENSIONS)
    style = _score_dimensions(answers, LEARNING_STYLE_DIMENSIONS)
    return AptitudeProfile(
        interest=InterestVector(**interest), learning_style=LearningStyle(**style)
    )


def resolve_aptitude(
    survey: list[SurveyAnswer], explicit: AptitudeProfile | None
) -> AptitudeProfile:
    """명시 프로필 우선, 없으면 설문 계산, 둘 다 없으면 중립."""
    if explicit is not None:
        return explicit
    if survey:
        return score_survey(survey)
    return AptitudeProfile()
