"""규칙기반 추천 엔진 (Stage 1).

docs/edu/추천엔진_설계.md §4 Stage 1 + §7 파이프라인 구현.
점수 = 인기도(국민 커리큘럼) + 적성(흥미) 친화도 + 단계 적합도.
backend/app/recommender.py 의 점수/설명 패턴을 교육 도메인에 적용.
"""
from __future__ import annotations

from .aptitude import resolve_aptitude
from .catalog import Resource, resources_for_age
from .curriculum import Stage, get_stage
from .models import (
    AptitudeProfile,
    Recommendation,
    RecommendationResponse,
    RecommendationType,
    StudentProfile,
)

# 점수 가중치 (합 = 1.0) — 아기 트랙과 동일 패턴
W_POPULARITY = 0.40
W_APTITUDE = 0.35
W_STAGE = 0.25

# RIASEC 차원 → 사람이 읽는 라벨(설명용)
_DIM_LABEL = {
    "realistic": "현실형(R)",
    "investigative": "탐구형(I)",
    "artistic": "예술형(A)",
    "social": "사회형(S)",
    "enterprising": "진취형(E)",
    "conventional": "관습형(C)",
}


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


def _stage_relevance(resource: Resource, stage: Stage) -> float:
    """단계 적합도: 교과 영역이 해당 단계 핵심 영역이면 1.0, 아니면 0.5."""
    return 1.0 if resource.area in stage.core_areas else 0.5


def _classify(resource: Resource, stage: Stage, fit: float) -> RecommendationType:
    if resource.national_pick:
        return RecommendationType.NATIONAL_PICK
    if resource.affinity and fit >= 0.6:
        return RecommendationType.APTITUDE_MATCH
    return RecommendationType.STAGE_CORE


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
    if not reasons:
        reasons.append(f"{stage.label} 추천 후보 ({resource.resource_type})")
    return reasons


def recommend(profile: StudentProfile, top_k: int = 8) -> RecommendationResponse:
    """프로필 → 커리큘럼 추천. 콜드스타트(데이터 0)에서도 동작."""
    aptitude = resolve_aptitude(profile.survey, profile.aptitude)
    stage = get_stage(profile.age_years)

    candidates = resources_for_age(profile.age_years)
    if profile.budget_max is not None:
        candidates = [r for r in candidates if r.cost <= profile.budget_max]

    scored: list[Recommendation] = []
    for r in candidates:
        fit = _aptitude_fit(r, aptitude)
        stage_rel = _stage_relevance(r, stage)
        score = W_POPULARITY * r.popularity + W_APTITUDE * fit + W_STAGE * stage_rel
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
        recommendations=scored[:top_k],
    )
