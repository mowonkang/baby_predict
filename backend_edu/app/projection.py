"""예상 능력치 전망 — 성장도표(백분위 트래킹) 개념 + Gagné DMGT 촉매 논리 (무과금·규칙 기반).

공신력 근거:
- **성장도표 개념**(WHO·질병관리청 소아 성장도표): 같은 나이 집단 내 백분위 곡선을 따라
  경과를 추적하는 표준 방법. → "현재 밴드 유지"를 보수 시나리오의 기준으로 사용.
- **Gagné DMGT 2.0**: 재능(talent)은 타고난 능력(gifts)이 **개발 과정(활동·투자·진전)**과
  **촉매(개인내적: 동기·자기조절 / 환경적: 부모·지도자·프로그램)**를 거쳐 발달한다.
  → 추천 루트 이행(=개발 투자)을 기본, 촉매 우호를 낙관 시나리오로 모델링.

⚠️ 능력 발달의 개인 예측은 과학적으로 미검증 — 보장이 아닌 '참고 전망 밴드'로만 제시하고
   낙관/기본/보수 3밴드와 근거(drivers)를 함께 공개한다. LLM 호출 없음.
"""
from __future__ import annotations

from .models import ProjectionResponse, StatProjection, StudentProfile
from .stats import build_stats
from .techtree import _STAT_TRACK  # 강점 stat → 추천 트랙 매핑 재사용


def _horizon(age: int) -> tuple[str, int]:
    """다음 학교급 전환 시점 라벨 + 대략 연수."""
    if age < 8:
        return ("초등 진입~저학년(약 2~3년 후)", 3)
    if age < 14:
        return ("중등 진입 시(약 " + str(max(1, 14 - age)) + "년 후)", max(1, 14 - age))
    if age < 17:
        return ("고등 진입 시(약 " + str(max(1, 17 - age)) + "년 후)", max(1, 17 - age))
    return ("고교 졸업·진로 결정 시", 2)


def build_projection(profile: StudentProfile) -> ProjectionResponse:
    stat = build_stats(profile)
    label, years = _horizon(profile.age_years)

    # 추천 루트가 겨냥하는 능력치(=개발 투자가 들어가는 축)
    top_keys = {a.key for a in stat.axes if a.top}
    targeted = {k for k in top_keys if k in _STAT_TRACK}
    # 콜드스타트(강점 없음)면 기본 추천 계열(인성·사고력)의 축을 대상으로
    if not targeted:
        targeted = {"social", "logic"}

    per_year_invest = 4    # 루트 이행 시 연간 성장(투자 효과, 규칙 가정)
    per_year_school = 1.5  # 학교 교육만으로의 자연 성장(가정)
    cap_years = min(years, 4)

    projections: list[StatProjection] = []
    for a in stat.axes:
        invest = a.key in targeted
        base_gain = (per_year_invest if invest else per_year_school) * cap_years
        base = a.value + base_gain
        conservative = a.value + per_year_school * cap_years * 0.5  # 밴드 유지에 가까움
        optimistic = base + 4 + (3 if invest else 0)                # 촉매 우호(지도자·동기)
        clamp = lambda v: int(round(max(5, min(100, v))))
        projections.append(StatProjection(
            key=a.key, label=a.label, now=a.value,
            conservative=clamp(conservative), base=clamp(base), optimistic=clamp(optimistic)))

    # 전망을 움직이는 요인(DMGT 촉매) — 무엇이 낙관 밴드를 만드는지 공개
    drivers = [
        "개발 투자: 추천 루트(테크트리)를 꾸준히 이행 — 재능은 투자 없이는 발달하지 않아요(DMGT).",
        "개인 촉매: 아이의 동기·의도적 조절(기질) — 스스로 하고 싶어하는 분야가 가장 빨리 자랍니다.",
        "환경 촉매: 부모의 지지, 잘 맞는 지도자·프로그램(조화의 적합성).",
        "객관적 이정표: 공인 급수·등급(CEFR·품띠·ABRSM 등)으로 진행을 측정하며 조정하세요.",
    ]

    return ProjectionResponse(horizon_label=label, projections=projections, drivers=drivers)
