"""기질 프로파일 — Rothbart CBQ 3요인 착안 (무과금·규칙 기반, 진단 아님).

공신력 근거: Rothbart의 CBQ(Children's Behavior Questionnaire)는 3~7세 아동 기질을
양육자 보고로 평가하는 가장 널리 검증된 척도로, 요인분석에서 3개 광범위 차원이 추출된다
(한국판 타당화: KCI ART002027016):
  · 외향성/서전시(Surgency)      — 접근성·활동수준·자극 선호
  · 부정정서(Negative Affectivity) — 불안·공포·분노/좌절·진정성
  · 의도적 통제(Effortful Control) — 주의집중·자기조절

여기에 Thomas & Chess(NYLS)의 '기질 유형'과 **조화의 적합성(goodness of fit)** 개념을 결합해
"기질에는 좋고 나쁨이 없고, 환경과의 맞춤이 중요하다"는 프레임으로 양육 가이드를 낸다.

문항은 CBQ 원문항이 아닌 **자체 관찰형 예시 문항**이며, 응답 척도는 또래 대비 5단계(0~4)를
공유한다(behaviors dict에 tp_* id로 함께 저장). 임상 기질검사가 아님을 항상 고지한다.
"""
from __future__ import annotations

from dataclasses import dataclass

from .models import TemperamentFactor, TemperamentItem, TemperamentProfile

SCALE = ["또래보다 훨씬 약함", "조금 약함", "또래와 비슷", "조금 강함", "또래보다 강함"]  # 0~4

FACTORS: list[tuple[str, str]] = [
    ("surgency", "외향성·활동성"),
    ("negative_affect", "정서 민감성"),
    ("effortful_control", "의도적 조절"),
]
_LABEL = dict(FACTORS)

# 기질별 환경 맞춤 팁(goodness of fit) — 높음/중간/낮음
_TIPS: dict[str, dict[str, str]] = {
    "surgency": {
        "높음": "에너지를 발산할 활동(신체·그룹수업)을 넣고, 정적인 학습은 짧게 쪼개세요.",
        "중간": "동적·정적 활동을 균형 있게 섞으면 무난하게 적응해요.",
        "낮음": "새 활동은 소그룹·1:1로 천천히 시작하고, 관찰할 시간을 충분히 주세요.",
    },
    "negative_affect": {
        "높음": "변화 예고·루틴 유지로 예측 가능성을 높이고, 감정을 말로 풀어주세요.",
        "중간": "새로운 상황 전 간단한 예고면 충분해요.",
        "낮음": "회복이 빠른 편 — 다양한 도전을 시도해도 좋아요.",
    },
    "effortful_control": {
        "높음": "스스로 계획하는 자기주도 학습이 잘 맞아요. 선택권을 주세요.",
        "중간": "짧은 목표와 체크리스트로 집중 루틴을 만들어 주세요.",
        "낮음": "한 번에 한 과제, 타이머·보상 등 외부 구조로 조절을 도와주세요.",
    },
}


@dataclass(frozen=True)
class _Item:
    id: str
    factor: str
    text: str


# 요인당 2문항 — 관찰 가능한 행동(예시, 검수 전). id는 tp_* (behaviors dict 공유)
ITEMS: list[_Item] = [
    _Item("tp_s1", "surgency", "새로운 사람·장소·활동에 스스럼없이 다가간다"),
    _Item("tp_s2", "surgency", "몸을 움직이는 활동을 좋아하고 에너지가 넘친다"),
    _Item("tp_n1", "negative_affect", "낯설거나 뜻대로 안 되면 불안·짜증을 크게 느낀다"),
    _Item("tp_n2", "negative_affect", "속상한 일이 있으면 달래는 데 시간이 오래 걸린다"),
    _Item("tp_e1", "effortful_control", "하던 일을 끝까지 집중해서 마친다"),
    _Item("tp_e2", "effortful_control", "하고 싶어도 '지금은 안 돼'를 참고 기다릴 수 있다"),
]
_ITEM_BY_ID = {i.id: i for i in ITEMS}
_FACTOR_ITEMS: dict[str, list[str]] = {}
for _it in ITEMS:
    _FACTOR_ITEMS.setdefault(_it.factor, []).append(_it.id)


def items() -> list[TemperamentItem]:
    return [TemperamentItem(id=i.id, factor=i.factor, text=i.text) for i in ITEMS]


def _score(vals: list[int]) -> int:
    """0~4 응답 평균 → 0~100 (중앙 50 = 또래 중간)."""
    if not vals:
        return 50
    return int(round(sum(vals) / (4.0 * len(vals)) * 100))


def _level(score: int) -> str:
    if score >= 65:
        return "높음"
    if score <= 35:
        return "낮음"
    return "중간"


# Thomas & Chess 유형 참조: 순한(easy)·까다로운(difficult)·더딘(slow-to-warm-up) 조합 라벨
def _type_label(s: int, n: int, e: int) -> str:
    hi_s, lo_s = s >= 65, s <= 35
    hi_n, lo_n = n >= 65, n <= 35
    hi_e = e >= 65
    if hi_s and lo_n:
        return "활발·긍정형"
    if hi_s and hi_n:
        return "열정·민감형"
    if lo_s and hi_n:
        return "신중·민감형"
    if lo_s and lo_n:
        return "차분·안정형"
    if hi_e:
        return "조절·집중형"
    return "균형형"


def build_temperament(behaviors: dict[str, int]) -> TemperamentProfile:
    """behaviors(tp_* 응답 0~4) → 기질 3요인 프로파일 + 유형 + 환경 가이드."""
    clean = {k: max(0, min(4, int(v))) for k, v in (behaviors or {}).items()
             if k in _ITEM_BY_ID}

    factors: list[TemperamentFactor] = []
    scores: dict[str, int] = {}
    for key, label in FACTORS:
        vals = [clean[i] for i in _FACTOR_ITEMS[key] if i in clean]
        sc = _score(vals)
        scores[key] = sc
        lv = _level(sc) if vals else "중간"
        factors.append(TemperamentFactor(
            key=key, label=label, level=lv, score=sc,
            parenting_tip=_TIPS[key][lv], answered=len(vals)))

    answered = len(clean)
    if answered:
        t = _type_label(scores["surgency"], scores["negative_affect"], scores["effortful_control"])
        # goodness of fit: 가장 두드러진 요인의 팁을 대표 가이드로
        dominant = max(factors, key=lambda f: abs(f.score - 50))
        fit = f"{dominant.label}이(가) 두드러져요 — {dominant.parenting_tip}"
    else:
        t, fit = "미입력", "기질 문항에 답하면 아이에게 맞는 환경 가이드를 드려요."

    return TemperamentProfile(factors=factors, type_label=t, fit_guide=fit, answered=answered)
