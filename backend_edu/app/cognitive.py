"""관찰형 인지 성향 프로파일 (WISC 5영역 착안, 무과금·규칙 기반).

부모가 아이의 '성향'을 몰라도, **관찰 가능한 행동**에 빈도로 답하면(0 거의아니다 ~ 3 거의항상)
아이의 상대적 인지 강·약점을 5영역으로 역추론한다. 여러 신호를 삼각측량해 한 번의 관심 클릭이
결과를 과결정하지 않게 한다.

5영역은 K-WISC-V의 지표에서 착안:
  언어이해(verbal) · 시공간(spatial) · 유동추론(reasoning) · 작업기억(memory) · 처리속도(speed)
점수 프레이밍은 웩슬러의 '평균 100·표준편차 15' 해석을 차용하되, **IQ·진단이 아니라 참고 밴드**로만
제시한다(임상 검사 대체 아님).

근거 리서치: docs/edu/인지프로파일_WISC참고.md
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from .models import CognitiveDomain, CognitiveItem, CognitiveProfile

SCALE = ["거의 아니다", "가끔", "자주", "거의 항상"]  # 0~3

DOMAINS: list[tuple[str, str]] = [
    ("verbal", "언어이해"),
    ("spatial", "시공간"),
    ("reasoning", "유동추론"),
    ("memory", "작업기억"),
    ("speed", "처리속도"),
]
_LABEL = dict(DOMAINS)

_HINT = {
    "verbal": "책읽기·대화·설명하기·글쓰기로 어휘와 표현을 키워요.",
    "spatial": "블록·퍼즐·그리기·지도읽기 등 공간·시각 활동을 늘려요.",
    "reasoning": "패턴찾기·보드게임·'왜?'질문·사고력 문제로 추론을 키워요.",
    "memory": "이야기 순서 말하기·기억게임·여러 단계 심부름으로 작업기억을 키워요.",
    "speed": "시간을 정해 간단한 과제를 끝내는 연습으로 처리속도를 키워요.",
}


@dataclass(frozen=True)
class _Item:
    id: str
    domain: str
    text: str


# 관찰 가능한 행동 문항(영역당 2개). 나이 공통 표현으로 작성(예시·검수 전).
ITEMS: list[_Item] = [
    _Item("cg_v1", "verbal", "새로운 낱말·표현을 빨리 익히고 말이나 글로 잘 표현한다"),
    _Item("cg_v2", "verbal", "이야기·설명을 듣고 요점을 잘 이해하고 자기 말로 다시 설명한다"),
    _Item("cg_s1", "spatial", "블록·퍼즐·그리기 등 공간·시각 활동을 좋아하고 잘한다"),
    _Item("cg_s2", "spatial", "길·구조·모양을 머릿속으로 잘 그리고 방향 감각이 좋다"),
    _Item("cg_r1", "reasoning", "규칙·패턴을 스스로 찾아내고 '왜 그럴까'를 파고든다"),
    _Item("cg_r2", "reasoning", "처음 보는 문제도 이리저리 궁리해서 해결하려 한다"),
    _Item("cg_m1", "memory", "들은 것·본 것을 잘 기억하고 순서대로 말한다"),
    _Item("cg_m2", "memory", "여러 단계의 지시를 한 번에 기억해서 수행한다"),
    _Item("cg_p1", "speed", "간단한 과제를 빠르고 실수 없이 처리한다"),
    _Item("cg_p2", "speed", "정해진 시간 안에 집중해서 끝내는 편이다"),
]
_ITEM_BY_ID = {i.id: i for i in ITEMS}
_DOMAIN_ITEMS: dict[str, list[str]] = {}
for _it in ITEMS:
    _DOMAIN_ITEMS.setdefault(_it.domain, []).append(_it.id)


def items() -> list[CognitiveItem]:
    return [CognitiveItem(id=i.id, domain=i.domain, text=i.text) for i in ITEMS]


def _phi(z: float) -> float:
    """표준정규 CDF."""
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def _band(index: int) -> str:
    if index >= 120:
        return "우수"
    if index >= 110:
        return "평균상"
    if index >= 90:
        return "또래 평균"
    if index >= 80:
        return "평균하"
    return "보완필요"


def _domain_index(scores: list[int]) -> int:
    """문항 점수(0~3) → 참고 지표(평균 100·SD 15 프레이밍).

    응답 평균이 척도 중앙(1.5)이면 100, 최고(3)면 ~+2SD, 최저(0)면 ~-2SD로 매핑.
    """
    if not scores:
        return 100
    p = (sum(scores) / (3.0 * len(scores)))     # 0~1
    index = 100 + (p - 0.5) * 60                # 0.5→100, 1→130, 0→70
    return int(round(max(55, min(145, index))))


def build_cognitive(behaviors: dict[str, int]) -> CognitiveProfile:
    """행동 문항 응답 → 5영역 인지 성향 프로파일."""
    clean = {k: max(0, min(3, int(v))) for k, v in (behaviors or {}).items()
             if k in _ITEM_BY_ID}
    total_answered = len(clean)

    doms: list[CognitiveDomain] = []
    for key, label in DOMAINS:
        sc = [clean[i] for i in _DOMAIN_ITEMS.get(key, []) if i in clean]
        idx = _domain_index(sc)
        pct = int(round(_phi((idx - 100) / 15.0) * 100)) if sc else 50
        doms.append(CognitiveDomain(
            key=key, label=label, index=idx, band=_band(idx),
            percentile=max(1, min(99, pct)), answered=len(sc), hint=_HINT[key]))

    answered_doms = [d for d in doms if d.answered]
    if answered_doms:
        # 상대 강점: 지표 상위 & 100 초과
        ranked = sorted(answered_doms, key=lambda d: d.index, reverse=True)
        strong = [d for d in ranked if d.index > 105][:2]
        skeys = {d.key for d in strong}
        for d in doms:
            d.top = d.key in skeys
        supports = [d for d in sorted(answered_doms, key=lambda d: d.index) if d.index < 95][:2]
        if strong:
            head = "·".join(d.label for d in strong) + " 강점형"
        else:
            head = "고른 발달형"
    else:
        strong, supports, head = [], [], "행동 문항에 답하면 성향이 보여요"

    return CognitiveProfile(
        domains=doms,
        strengths=[d.label for d in strong],
        supports=[d.label for d in supports],
        headline=head,
        answered=total_answered,
    )


# 인지 영역 → 8각 능력치(stats) 기여 매핑 (삼각측량용)
COG_TO_STAT: dict[str, list[tuple[str, float]]] = {
    "verbal":    [("language", 0.6)],
    "spatial":   [("art", 0.4), ("creativity", 0.4), ("logic", 0.2)],
    "reasoning": [("logic", 0.5), ("science", 0.4)],
    "memory":    [("logic", 0.3), ("language", 0.2)],
    "speed":     [("logic", 0.15), ("physical", 0.1)],
}


def stat_contributions(behaviors: dict[str, int]) -> dict[str, float]:
    """행동 프로파일 → 8각 능력치 가산치(지표 100 초과분 × 가중치)."""
    prof = build_cognitive(behaviors)
    out: dict[str, float] = {}
    for d in prof.domains:
        if not d.answered:
            continue
        over = d.index - 100          # -45~+45
        if over <= 0:
            continue
        for stat, w in COG_TO_STAT.get(d.key, []):
            out[stat] = out.get(stat, 0.0) + over * w
    return out
