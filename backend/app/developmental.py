"""월령별 발달 매핑 테이블 (지식 기반).

docs/추천엔진_설계.md §5 의 표를 코드 데이터로 옮긴 것.
운영 시에는 전문가 검수 + 공공 데이터(kidshub 등)로 확장한다.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class AgeBand:
    key: str
    label: str
    min_months: int
    max_months: int  # 포함(inclusive)
    tasks: list[str] = field(default_factory=list)
    item_categories: list[str] = field(default_factory=list)
    play_categories: list[str] = field(default_factory=list)


# 월령 오름차순. max_months 는 포함 경계.
AGE_BANDS: list[AgeBand] = [
    AgeBand(
        key="0-3m", label="0~3개월", min_months=0, max_months=3,
        tasks=["수면·수유 안정", "시각 자극(흑백)"],
        item_categories=["수유", "수면"],
        play_categories=["시각자극"],
    ),
    AgeBand(
        key="4-6m", label="4~6개월", min_months=4, max_months=6,
        tasks=["뒤집기", "이앓이 시작"],
        item_categories=["이앓이", "안전"],
        play_categories=["촉감놀이", "청각자극"],
    ),
    AgeBand(
        key="7-9m", label="7~9개월", min_months=7, max_months=9,
        tasks=["앉기·기기", "손가락 잡기"],
        item_categories=["이유식", "안전"],
        play_categories=["대근육", "소근육"],
    ),
    AgeBand(
        key="10-12m", label="10~12개월", min_months=10, max_months=12,
        tasks=["잡고 서기", "첫걸음 준비"],
        item_categories=["보행", "안전"],
        play_categories=["대근육", "소근육"],
    ),
    AgeBand(
        key="13-18m", label="13~18개월", min_months=13, max_months=18,
        tasks=["걷기", "단어 시작"],
        item_categories=["외출", "식기"],
        play_categories=["대근육", "언어"],
    ),
    AgeBand(
        key="19-24m", label="19~24개월", min_months=19, max_months=24,
        tasks=["뛰기", "두 단어 문장"],
        item_categories=["식기", "안전"],
        play_categories=["대근육", "역할놀이"],
    ),
    AgeBand(
        key="24m+", label="24개월 이상", min_months=25, max_months=72,
        tasks=["사회성", "상상놀이"],
        item_categories=["학습"],
        play_categories=["창의", "역할놀이"],
    ),
]


def get_age_band(age_months: int) -> AgeBand:
    """월령에 해당하는 발달 단계를 반환. 범위를 벗어나면 양끝으로 클램프."""
    if age_months <= AGE_BANDS[0].max_months:
        return AGE_BANDS[0]
    for band in AGE_BANDS:
        if band.min_months <= age_months <= band.max_months:
            return band
    return AGE_BANDS[-1]
