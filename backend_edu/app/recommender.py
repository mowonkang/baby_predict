"""규칙기반 추천 엔진 (Stage 1).

docs/edu/추천엔진_설계.md §4 Stage 1 + §7 파이프라인 구현.
점수 = 인기도(국민 커리큘럼) + 적성(흥미) 친화도 + 단계 적합도 + 학습성향 적합도.
backend/app/recommender.py 의 점수/설명 패턴을 교육 도메인에 적용.
"""
from __future__ import annotations

from .aptitude import resolve_aptitude
from .catalog import Resource, resources_for_age
from .curriculum import Stage, get_stage
from .models import (
    AptitudeProfile,
    LearningStyle,
    Recommendation,
    RecommendationResponse,
    RecommendationType,
    StudentProfile,
)

# 점수 가중치 (합 = 1.0)
W_POPULARITY = 0.35
W_APTITUDE = 0.30
W_STAGE = 0.20
W_STYLE = 0.15

# RIASEC 차원 → 사람이 읽는 라벨(설명용)
_DIM_LABEL = {
    "realistic": "현실형(R)",
    "investigative": "탐구형(I)",
    "artistic": "예술형(A)",
    "social": "사회형(S)",
    "enterprising": "진취형(E)",
    "conventional": "관습형(C)",
}

# 리소스 형태 → 학습성향 친화 (가중치 -1~1)
#   인강·교재: 자기주도형에 적합(+) / 학원: 관리형(자기주도 낮음)에 적합(-)
#   활동: 협동 선호에 적합(+)
_TYPE_STYLE_AFFINITY: dict[str, dict[str, float]] = {
    "인강": {"self_direction": 0.7},
    "교재": {"self_direction": 0.7},
    "학원": {"self_direction": -0.6},
    "활동": {"collaboration": 0.7},
    "진로": {},
}

# 분석 성향이 높을 때 가산점을 받는 영역
_ANALYTICAL_AREAS = {"수학", "과학", "탐구"}


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def _aptitude_fit(resource: Resource, aptitude: AptitudeProfile) -> float:
    """흥미 친화도 0~1. affinity 없으면 0.5(중립)."""
    if not resource.affinity:
        return 0.5
    interest = aptitude.interest.as_dict()
    total = 0.0
    for dim, weight in resource.affinity.items():
        signal = (interest.get(dim, 0.5) - 0.5) * 2.0  # -1~1
        total += weight * signal
    return _clamp01(0.5 + 0.5 * total)


def _style_fit(resource: Resource, style: LearningStyle) -> float:
    """학습성향 적합도 0~1. 리소스 형태(인강/학원/활동)와 학습성향을 매칭."""
    s = style.as_dict()
    total = 0.0
    for dim, weight in _TYPE_STYLE_AFFINITY.get(resource.resource_type, {}).items():
        signal = (s.get(dim, 0.5) - 0.5) * 2.0
        total += weight * signal
    # 분석 성향이 높고 수·과학·탐구 영역이면 소폭 가산
    if resource.area in _ANALYTICAL_AREAS:
        total += 0.4 * ((s["analytical"] - 0.5) * 2.0)
    return _clamp01(0.5 + 0.5 * total)


def _stage_relevance(resource: Resource, stage: Stage) -> float:
    """단계 적합도: 교과 영역이 해당 단계 핵심 영역이면 1.0, 아니면 0.5."""
    return 1.0 if resource.area in stage.core_areas else 0.5


def _classify(resource: Resource, stage: Stage, fit: float) -> RecommendationType:
    if resource.national_pick:
        return RecommendationType.NATIONAL_PICK
    if resource.affinity and fit >= 0.6:
        return RecommendationType.APTITUDE_MATCH
    return RecommendationType.STAGE_CORE


def _style_reason(resource: Resource, style: LearningStyle) -> str | None:
    """학습성향-리소스 형태 매칭 설명. 적합할 때만 반환."""
    s = style.as_dict()
    rtype = resource.resource_type
    if rtype in ("인강", "교재") and s["self_direction"] >= 0.6:
        return f"자기주도 학습 성향에 맞는 {rtype} 형태"
    if rtype == "학원" and s["self_direction"] <= 0.4:
        return "꾸준한 관리가 도움이 되는 학생에게 맞는 학원형"
    if rtype == "활동" and s["collaboration"] >= 0.6:
        return "협동·토론을 선호하는 학생에게 맞는 활동형"
    if resource.area in _ANALYTICAL_AREAS and s["analytical"] >= 0.6:
        return "원리 분석을 즐기는 성향에 맞는 심화 과정"
    return None


def _reasons(
    resource: Resource, stage: Stage, aptitude: AptitudeProfile, fit: float
) -> list[str]:
    reasons: list[str] = []
    if resource.national_pick:
        reasons.append(
            f"{stage.label} 단계에서 많이 선택되는 인기 커리큘럼 (인기도 {resource.popularity:.0%})"
        )
    if _stage_relevance(resource, stage) >= 1.0:
        comp = stage.competencies[0] if stage.competencies else stage.label
        reasons.append(f"{stage.label} 핵심 역량('{comp}')에 맞는 {resource.area} 과정")
    if resource.affinity and fit >= 0.6:
        interest = aptitude.interest.as_dict()
        best_dim, best_contrib = None, 0.0
        for dim, weight in resource.affinity.items():
            contrib = weight * ((interest.get(dim, 0.5) - 0.5) * 2.0)
            if contrib > best_contrib:
                best_dim, best_contrib = dim, contrib
        if best_dim is not None:
            reasons.append(f"{_DIM_LABEL.get(best_dim, best_dim)} 적성에 잘 맞는 과정")
    style_reason = _style_reason(resource, aptitude.learning_style)
    if style_reason:
        reasons.append(style_reason)
    if not reasons:
        reasons.append(f"{stage.label} 추천 후보 ({resource.resource_type})")
    return reasons


def summarize_study_mode(style: LearningStyle) -> str:
    """학습성향 → 권장 학습 방식 한 줄 요약."""
    parts: list[str] = []
    if style.self_direction >= 0.6:
        parts.append("자기주도형 — 인강·교재 중심 자기학습이 효과적")
    elif style.self_direction <= 0.4:
        parts.append("관리형 — 학원·코칭 등 관리가 동반되면 효과적")
    else:
        parts.append("혼합형 — 자기학습과 관리를 병행 권장")
    if style.collaboration >= 0.6:
        parts.append("토론·협동 활동 병행 추천")
    if style.analytical >= 0.6:
        parts.append("원리 이해 중심 심화 학습 선호")
    return " · ".join(parts)


def recommend(profile: StudentProfile, top_k: int = 8) -> RecommendationResponse:
    """프로필 → 커리큘럼 추천. 콜드스타트(데이터 0)에서도 동작."""
    aptitude = resolve_aptitude(profile.survey, profile.aptitude, profile.interests)
    stage = get_stage(profile.age_years)

    candidates = resources_for_age(profile.age_years)
    if profile.budget_max is not None:
        candidates = [r for r in candidates if r.cost <= profile.budget_max]

    scored: list[Recommendation] = []
    for r in candidates:
        fit = _aptitude_fit(r, aptitude)
        stage_rel = _stage_relevance(r, stage)
        style_fit = _style_fit(r, aptitude.learning_style)
        score = (
            W_POPULARITY * r.popularity
            + W_APTITUDE * fit
            + W_STAGE * stage_rel
            + W_STYLE * style_fit
        )
        scored.append(
            Recommendation(
                resource_id=r.resource_id,
                name=r.name,
                area=r.area,
                cost=r.cost,
                score=round(_clamp01(score), 4),
                type=_classify(r, stage, fit),
                reasons=_reasons(r, stage, aptitude, fit),
            )
        )

    scored.sort(key=lambda x: x.score, reverse=True)
    return RecommendationResponse(
        aptitude=aptitude,
        stage=stage.label,
        stage_competencies=stage.competencies,
        study_mode=summarize_study_mode(aptitude.learning_style),
        recommendations=scored[:top_k],
    )
