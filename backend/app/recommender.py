"""규칙기반 추천 엔진 (Stage 1).

docs/추천엔진_설계.md §4 Stage 1 + §6 파이프라인 구현.
점수 = 인기도(국민템) + 기질 친화도 + 발달 적합도의 가중합.
설명가능성(reasons)을 함께 생성한다.
"""
from __future__ import annotations

from .catalog import Product, products_for_age
from .developmental import AgeBand, get_age_band
from .models import (
    BabyProfile,
    Recommendation,
    RecommendationResponse,
    RecommendationType,
    TemperamentVector,
)
from .temperament import resolve_temperament

# 점수 가중치 (합 = 1.0)
W_POPULARITY = 0.40
W_TEMPERAMENT = 0.35
W_DEVELOPMENT = 0.25

# 기질 차원 → 사람이 읽는 라벨(설명용)
_DIM_LABEL = {
    "activity": "활동성",
    "regularity": "규칙성",
    "adaptability": "적응성",
    "intensity": "반응 강도",
    "mood": "기분",
}


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def _temperament_fit(product: Product, temperament: TemperamentVector) -> float:
    """기질 친화도 0~1. affinity 없으면 0.5(중립)."""
    if not product.affinity:
        return 0.5
    temp = temperament.as_dict()
    total = 0.0
    for dim, weight in product.affinity.items():
        # (값-0.5)*2 → -1~1. 가중치와 곱해 합산.
        signal = (temp.get(dim, 0.5) - 0.5) * 2.0
        total += weight * signal
    # total 범위를 대략 -1~1 로 보고 0~1 로 매핑
    return _clamp01(0.5 + 0.5 * total)


def _dev_relevance(product: Product, band: AgeBand) -> float:
    """발달 적합도: 카테고리가 해당 월령 발달 단계와 맞으면 1.0, 아니면 0.5."""
    if product.category in band.item_categories:
        return 1.0
    if product.play_category and product.play_category in band.play_categories:
        return 1.0
    return 0.5


def _classify(product: Product, band: AgeBand) -> RecommendationType:
    if product.play_category and product.play_category in band.play_categories:
        return RecommendationType.DEVELOPMENTAL_PLAY
    if product.national_pick:
        return RecommendationType.NATIONAL_PICK
    return RecommendationType.TEMPERAMENT_MATCH


def _reasons(
    product: Product, band: AgeBand, temperament: TemperamentVector, fit: float
) -> list[str]:
    reasons: list[str] = []
    if product.national_pick:
        reasons.append(
            f"{band.label} 또래에서 많이 선택된 국민템 (인기도 {product.popularity:.0%})"
        )
    # 발달 적합성
    if _dev_relevance(product, band) >= 1.0:
        task = band.tasks[0] if band.tasks else band.label
        reasons.append(f"{band.label} 발달 단계('{task}')에 맞는 {product.category} 용품")
    # 기질 친화성 — 가장 강하게 기여한 차원 설명
    if product.affinity and fit >= 0.6:
        temp = temperament.as_dict()
        best_dim, best_contrib = None, 0.0
        for dim, weight in product.affinity.items():
            contrib = weight * ((temp.get(dim, 0.5) - 0.5) * 2.0)
            if contrib > best_contrib:
                best_dim, best_contrib = dim, contrib
        if best_dim is not None:
            label = _DIM_LABEL.get(best_dim, best_dim)
            high = product.affinity[best_dim] > 0
            tone = "높은" if high else "낮은(순한)"
            reasons.append(f"{label} {tone} 아기에게 잘 맞는 제품")
    if not reasons:
        reasons.append(f"{band.label} 추천 후보")
    return reasons


def recommend(profile: BabyProfile, top_k: int = 8) -> RecommendationResponse:
    """프로필 → 추천 응답. 콜드스타트(데이터 0) 상태에서도 동작."""
    temperament = resolve_temperament(profile.survey, profile.temperament)
    band = get_age_band(profile.age_months)

    candidates = products_for_age(profile.age_months)
    # 예산 필터
    if profile.budget_max is not None:
        candidates = [p for p in candidates if p.price <= profile.budget_max]

    scored: list[Recommendation] = []
    for p in candidates:
        fit = _temperament_fit(p, temperament)
        dev = _dev_relevance(p, band)
        score = (
            W_POPULARITY * p.popularity
            + W_TEMPERAMENT * fit
            + W_DEVELOPMENT * dev
        )
        scored.append(
            Recommendation(
                item_id=p.item_id,
                name=p.name,
                category=p.category,
                price=p.price,
                score=round(_clamp01(score), 4),
                type=_classify(p, band),
                reasons=_reasons(p, band, temperament, fit),
            )
        )

    scored.sort(key=lambda r: r.score, reverse=True)
    return RecommendationResponse(
        temperament=temperament,
        age_band=band.label,
        developmental_tasks=band.tasks,
        recommendations=scored[:top_k],
    )
