"""또래 대비 상대 비교(측정형) 5단계 척도 — 성취·하위스킬 공통.

기존 '잘함/보통/부족'은 상대 기준이 없어 주관적이었다. 사용자가 **또래 평균 대비 어디**인지
(상위 10%·상위 30%·평균·하위 30%·하위 10%)를 골라 더 객관적·측정형으로 입력하게 한다.

구(舊) 3단계 값(잘함/보통/부족)과 진단(BKT) 출력도 그대로 받아 정규화한다(하위 호환).
"""
from __future__ import annotations

# key, 라벨, 또래 앵커, 대략 백분위, 3분류 버킷
LEVELS5: list[dict] = [
    {"key": "top10", "label": "최상위", "anchor": "상위 10%", "pct": 92, "bucket": "good"},
    {"key": "top30", "label": "우수",   "anchor": "상위 30%", "pct": 73, "bucket": "good"},
    {"key": "mid",   "label": "평균",   "anchor": "또래 평균", "pct": 50, "bucket": "ok"},
    {"key": "low30", "label": "부족",   "anchor": "하위 30%", "pct": 27, "bucket": "weak"},
    {"key": "low10", "label": "매우 부족", "anchor": "하위 10%", "pct": 8, "bucket": "weak"},
]
_BY_KEY = {l["key"]: l for l in LEVELS5}

# 라벨·구값·별칭 → key
_ALIAS: dict[str, str] = {
    "최상위": "top10", "우수": "top30", "평균": "mid", "부족": "low30", "매우 부족": "low10",
    "매우부족": "low10",
    # 구 3단계 / 진단 출력 / 영문
    "잘함": "top30", "상": "top30", "good": "top30",
    "보통": "mid", "중": "mid", "ok": "mid",
    "하": "low30", "weak": "low30",
}
_COARSE = {"good": "잘함", "ok": "보통", "weak": "부족"}


def to_key(v: str | None) -> str | None:
    s = str(v or "").strip()
    if s in _BY_KEY:
        return s
    return _ALIAS.get(s)


def bucket(v: str | None) -> str:
    k = to_key(v)
    return _BY_KEY[k]["bucket"] if k else "ok"


def percentile(v: str | None) -> int:
    k = to_key(v)
    return _BY_KEY[k]["pct"] if k else 50


def label(v: str | None) -> str:
    k = to_key(v)
    return _BY_KEY[k]["label"] if k else "평균"


def anchor(v: str | None) -> str:
    k = to_key(v)
    return _BY_KEY[k]["anchor"] if k else "또래 평균"


def coarse(v: str | None) -> str:
    """3분류(잘함/보통/부족)로 축약 — 다운스트림 호환용."""
    return _COARSE[bucket(v)]
