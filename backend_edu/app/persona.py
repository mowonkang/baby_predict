"""페르소나(Learner Profile) 요약.

적성(흥미 RIASEC + 학습성향)과 성취 수준을 통합해 '해석 가능한 페르소나'와 라벨을 만든다.
LLM 없이 규칙 기반. 향후 BKT 숙련도·행동 로그를 벡터에 합쳐 정밀화한다.
근거: docs/edu/성장성_및_예측모델.md §3.2
"""
from __future__ import annotations

from .aptitude import resolve_aptitude
from .models import PersonaResponse, StudentProfile
from .recommender import summarize_study_mode

_RIASEC_KO = {
    "realistic": "현실형", "investigative": "탐구형", "artistic": "예술형",
    "social": "사회형", "enterprising": "진취형", "conventional": "관습형",
}
from . import levels


def build_persona(profile: StudentProfile) -> PersonaResponse:
    apt = resolve_aptitude(profile.survey, profile.aptitude, profile.interests)
    interest = apt.interest.as_dict()
    top = apt.interest.top_types(2)

    # 흥미 라벨(뚜렷하지 않으면 탐색형)
    if interest[top[0]] > 0.5:
        interest_label = _RIASEC_KO.get(top[0], top[0])
    else:
        interest_label = "탐색형"

    # 학습성향 라벨
    sd = apt.learning_style.self_direction
    style_label = "자기주도형" if sd >= 0.6 else "관리필요형" if sd <= 0.4 else "혼합형"

    persona_label = f"{interest_label}·{style_label} 학습자"
    subject_levels = {s: levels.coarse(lv) for s, lv in profile.achievements.items()}

    note = ("뚜렷한 강점이 아직 드러나지 않았어요 — 관심 활동·미니 진단을 더하면 페르소나가 선명해집니다."
            if interest_label == "탐색형"
            else f"{interest_label} 흥미 + {style_label} 성향을 반영해 학습·진로를 맞춤화합니다.")

    return PersonaResponse(
        interest=apt.interest, learning_style=apt.learning_style,
        top_interests=[_RIASEC_KO.get(t, t) for t in top],
        persona_label=persona_label, study_mode=summarize_study_mode(apt.learning_style),
        subject_levels=subject_levels, note=note,
    )
