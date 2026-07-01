"""적성 진단: 설문 → 흥미(RIASEC) + 학습성향 벡터.

docs/edu/추천엔진_설계.md §2 참조.
backend/app/temperament.py 의 스코어링 패턴을 교육 도메인에 적용.
각 문항은 하나의 차원에 매핑되며 reverse=True 면 역채점. 리커트 1~5 → 0~1.

흥미 6유형(RIASEC)은 교육부·커리어넷의 '직업흥미검사'(공공 무료 검사)와 **동일한 Holland 이론**
기반이므로 결과 호환·연계가 가능하다. 단, 본 결과는 의학·심리 '진단'이 아니라 추천을 위한
'참고용 선호 프로파일'로 한정한다(규제·윤리: docs/edu/교육현황_리서치.md §6).
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


# ── 쉬운 진단(선택형) ─────────────────────────────────────────────
# 1~5 척도가 정량적으로 답하기 어렵다는 피드백 → "해당되는 것 고르기" 방식.
@dataclass(frozen=True)
class ActivityOption:
    id: str
    label: str
    dims: tuple[str, ...]   # RIASEC 흥미 차원 또는 학습성향 차원
    kind: str               # "interest" | "style"


# 관심 활동(복수 선택) → 흥미(RIASEC)
ACTIVITY_OPTIONS: list[ActivityOption] = [
    ActivityOption("act_sci", "🔬 실험하고 원리 파헤치기", ("investigative",), "interest"),
    ActivityOption("act_math", "🧮 수학·논리 문제 풀기", ("investigative", "conventional"), "interest"),
    ActivityOption("act_make", "🛠️ 손으로 만들고 조립·고치기", ("realistic",), "interest"),
    ActivityOption("act_comp", "💻 컴퓨터·코딩·디지털 만들기", ("realistic", "investigative"), "interest"),
    ActivityOption("act_art", "🎨 그림·음악으로 표현하기", ("artistic",), "interest"),
    ActivityOption("act_write", "✍️ 글쓰기·독서·토론", ("artistic", "social"), "interest"),
    ActivityOption("act_help", "🤝 사람 돕고 가르치기", ("social",), "interest"),
    ActivityOption("act_lead", "🗣️ 발표·설득하고 이끌기", ("enterprising",), "interest"),
    ActivityOption("act_plan", "💼 기획·돈 관리·창업 상상", ("enterprising", "conventional"), "interest"),
    ActivityOption("act_org", "📋 정리·계획·꼼꼼한 작업", ("conventional",), "interest"),
    ActivityOption("act_social", "🌍 사회·역사·세상 일에 관심", ("social", "investigative"), "interest"),
    ActivityOption("act_body", "⚽ 운동·몸으로 하는 활동", ("realistic",), "interest"),
]

# 학습성향(해당되면 선택)
STYLE_OPTIONS: list[ActivityOption] = [
    ActivityOption("sty_self", "스스로 계획을 세워 공부하는 편", ("self_direction",), "style"),
    ActivityOption("sty_collab", "혼자보다 친구들과 함께 할 때 더 잘함", ("collaboration",), "style"),
    ActivityOption("sty_analytic", "암기보다 원리를 이해하는 걸 좋아함", ("analytical",), "style"),
]

_OPTION_BY_ID = {o.id: o for o in ACTIVITY_OPTIONS + STYLE_OPTIONS}


def score_activities(selected_ids: list[str]) -> AptitudeProfile:
    """선택한 관심활동·학습성향 → 적성 프로필. 선택 안 한 차원은 0.5(중립)."""
    interest_counts: dict[str, int] = {d: 0 for d in RIASEC_DIMENSIONS}
    style_hit: dict[str, bool] = {d: False for d in LEARNING_STYLE_DIMENSIONS}
    for sid in selected_ids:
        opt = _OPTION_BY_ID.get(sid)
        if opt is None:
            continue
        if opt.kind == "interest":
            for d in opt.dims:
                if d in interest_counts:
                    interest_counts[d] += 1
        else:
            for d in opt.dims:
                if d in style_hit:
                    style_hit[d] = True

    max_count = max(interest_counts.values())
    interest = {
        d: round(0.5 + 0.5 * (c / max_count), 4) if max_count else 0.5
        for d, c in interest_counts.items()
    }
    style = {d: (0.85 if hit else 0.5) for d, hit in style_hit.items()}
    return AptitudeProfile(
        interest=InterestVector(**interest), learning_style=LearningStyle(**style)
    )


def resolve_aptitude(
    survey: list[SurveyAnswer],
    explicit: AptitudeProfile | None,
    interests: list[str] | None = None,
) -> AptitudeProfile:
    """우선순위: 명시 프로필 > 리커트 설문 > 관심활동 선택 > 중립."""
    if explicit is not None:
        return explicit
    if survey:
        return score_survey(survey)
    if interests:
        return score_activities(interests)
    return AptitudeProfile()
