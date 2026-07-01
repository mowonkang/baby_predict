"""능력치 스탯 엔진 (프린세스 메이커식 8각형 레이더).

각 사람의 입력(관심활동 RIASEC + 학습성향 + 사교육/활동 경험 + 과목 성취)을
**규칙 기반**으로 합산해 8개 능력치(0~100)를 만든다. LLM 호출 없음(무과금).

설계: docs/edu/육성엔진_설계.md §2
"""
from __future__ import annotations

from .aptitude import resolve_aptitude
from .extracurricular import get as get_extra
from .models import StatAxis, StatProfile, StudentProfile

# 8개 능력치 축 (key, 라벨) — 8각형 레이더
STAT_AXES: list[tuple[str, str]] = [
    ("language", "언어"),
    ("logic", "수리·논리"),
    ("science", "탐구"),
    ("art", "예술"),
    ("physical", "신체"),
    ("social", "사회성"),
    ("leadership", "리더십"),
    ("creativity", "창의"),
]
_STAT_KEYS = [k for k, _ in STAT_AXES]
_STAT_LABEL = dict(STAT_AXES)

BASE = 40          # 기본치(모든 축 40에서 시작)
_MIN, _MAX = 5, 100

# RIASEC 흥미 차원 → 능력치 기여 (dim: [(stat, weight)])
_INTEREST_MAP: dict[str, list[tuple[str, float]]] = {
    "realistic":     [("physical", 34), ("logic", 20)],
    "investigative": [("science", 40), ("logic", 26)],
    "artistic":      [("art", 40), ("creativity", 30)],
    "social":        [("social", 40), ("language", 22)],
    "enterprising":  [("leadership", 40), ("social", 24)],
    "conventional":  [("logic", 30), ("language", 20)],
}

# 학습성향 → 능력치 기여
_STYLE_MAP: dict[str, list[tuple[str, float]]] = {
    "self_direction": [("leadership", 14)],
    "collaboration":  [("social", 16)],
    "analytical":     [("logic", 16), ("science", 12)],
}

# 과목 성취 → 능력치(잘함일수록 가산)
_SUBJECT_STAT: dict[str, str] = {
    "수학": "logic", "과학": "science", "국어": "language",
    "영어": "language", "사회": "social", "예술": "art", "체육": "physical",
}
_LEVEL_GAIN = {"잘함": 14, "상": 14, "보통": 5, "중": 5, "부족": 0, "하": 0}

# 활동 1개당 능력치 가중치 스케일(사교육 stat_weights × 이 값)
_EXTRA_SCALE = 16


def _level_label(v: int) -> str:
    if v >= 80:
        return "탁월"
    if v >= 65:
        return "우수"
    if v >= 50:
        return "성장"
    return "새싹"


# 최상위 능력치 → 육성 타이틀(프린세스메이커식 캐릭터 정체성)
_TITLE_BY_STAT: dict[str, str] = {
    "language": "이야기꾼 언어가",
    "logic": "논리 전략가",
    "science": "꼬마 과학자",
    "art": "예술가",
    "physical": "운동 챔피언",
    "social": "친화형 조력가",
    "leadership": "타고난 리더",
    "creativity": "창의 발명가",
}


def build_stats(profile: StudentProfile) -> StatProfile:
    """입력 프로필 → 8각형 능력치. 규칙 기반 합산 후 5~100으로 클램프."""
    scores: dict[str, float] = {k: float(BASE) for k in _STAT_KEYS}
    signals: list[str] = []

    apt = resolve_aptitude(profile.survey, profile.aptitude, profile.interests)

    # 1) 흥미(RIASEC): 중립(0.5) 초과분만 반영 → 뚜렷한 관심일수록 크게
    interest = apt.interest.as_dict()
    interest_used = False
    for dim, val in interest.items():
        gain = max(0.0, val - 0.5) * 2.0  # 0~1
        if gain <= 0:
            continue
        interest_used = True
        for stat, w in _INTEREST_MAP.get(dim, []):
            scores[stat] += gain * w
    if interest_used:
        signals.append("관심활동/적성")

    # 2) 학습성향
    style = apt.learning_style.as_dict()
    for dim, val in style.items():
        gain = max(0.0, val - 0.5) * 2.0
        for stat, w in _STYLE_MAP.get(dim, []):
            scores[stat] += gain * w

    # 3) 사교육/활동 경험·관심
    if profile.activities:
        for aid in profile.activities:
            ex = get_extra(aid)
            if ex is None:
                continue
            for stat, w in ex.stat_weights.items():
                if stat in scores:
                    scores[stat] += w * _EXTRA_SCALE
        signals.append("사교육/활동 경험")

    # 4) 과목 성취
    if profile.achievements:
        used = False
        for subj, lv in profile.achievements.items():
            stat = _SUBJECT_STAT.get(str(subj).strip())
            if not stat:
                continue
            scores[stat] += _LEVEL_GAIN.get(str(lv).strip(), 0)
            used = True
        if used:
            signals.append("과목 성취도")

    # 클램프 + 라벨링
    axes: list[StatAxis] = []
    for k in _STAT_KEYS:
        v = int(round(max(_MIN, min(_MAX, scores[k]))))
        axes.append(StatAxis(key=k, label=_STAT_LABEL[k], value=v, level=_level_label(v)))

    ranked = sorted(axes, key=lambda a: a.value, reverse=True)
    # 강점: 상위 축 중 BASE 초과한 것만(콜드스타트면 강점 없음)
    top = [a for a in ranked if a.value > BASE][:3]
    top_keys = {a.key for a in top}
    for a in axes:
        a.top = a.key in top_keys
    growth = [a for a in sorted(axes, key=lambda a: a.value) if a.value < 55][:2]

    if top:
        head = "·".join(a.label for a in top[:2]) + "형"
        if not signals:
            head = "탐색형"
    else:
        head = "탐색형(입력을 더하면 뚜렷해져요)"

    overall = int(round(sum(a.value for a in axes) / len(axes)))
    title = _TITLE_BY_STAT.get(top[0].key, "탐색가") if top else "탐색가"

    note = ("아직 입력이 적어 능력치가 평평해요 — 관심활동·사교육 경험·미니 진단을 더하면 뚜렷해집니다."
            if not top else
            "입력(관심·경험·성취)을 규칙 기반으로 합산한 참고용 능력치 — LLM 호출 없음.")

    return StatProfile(
        axes=axes,
        top_axes=[a.label for a in top],
        growth_axes=[a.label for a in growth],
        headline=head,
        overall=overall,
        overall_level=_level_label(overall),
        title=title,
        note=note,
        source_signals=signals,
    )
