"""학령 단계 매핑 테이블 (지식 기반).

docs/edu/추천엔진_설계.md §5 의 표를 코드 데이터로 옮긴 것.
backend/app/developmental.py 의 AgeBand 패턴을 교육 단계에 적용.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Stage:
    key: str
    label: str
    min_age: int
    max_age: int  # 포함(inclusive)
    competencies: list[str] = field(default_factory=list)  # 핵심 역량/과업
    core_areas: list[str] = field(default_factory=list)    # 핵심 교과 영역
    activity_types: list[str] = field(default_factory=list)  # 추천 활동 유형


# 만 나이 오름차순. max_age 포함 경계.
STAGES: list[Stage] = [
    Stage("preschool", "미취학", 3, 6,
          competencies=["기초 언어·수 개념", "놀이 학습"],
          core_areas=["한글", "기초수", "예체능"],
          activity_types=["놀이", "체험"]),
    Stage("elem_low", "초등 저학년", 7, 8,
          competencies=["문해력", "기초 연산", "학습 습관"],
          core_areas=["국어", "수학", "영어"],
          activity_types=["독서", "사고력"]),
    Stage("elem_mid", "초등 중학년", 9, 10,
          competencies=["사고력 확장", "흥미 탐색"],
          core_areas=["국어", "수학", "영어", "과학", "사회"],
          activity_types=["탐구", "예체능"]),
    Stage("elem_high", "초등 고학년", 11, 12,
          competencies=["심화·선행 판단", "진로 탐색"],
          core_areas=["국어", "수학", "영어"],
          activity_types=["사고력", "대회"]),
    Stage("middle", "중등", 13, 15,
          competencies=["교과 심화", "고입·계열 준비"],
          core_areas=["국어", "수학", "영어", "과학", "사회"],
          activity_types=["탐구대회", "동아리"]),
    Stage("high", "고등", 16, 18,
          competencies=["내신·수능", "입시 전략"],
          core_areas=["국어", "수학", "영어", "탐구"],
          activity_types=["연구", "세특활동"]),
    Stage("university", "대학", 19, 25,
          competencies=["전공·진로 실현"],
          core_areas=["전공", "교양"],
          activity_types=["인턴", "연구"]),
]


def get_stage(age_years: int) -> Stage:
    """만 나이에 해당하는 학령 단계 반환. 범위 밖은 양끝으로 클램프."""
    if age_years <= STAGES[0].max_age:
        return STAGES[0]
    for stage in STAGES:
        if stage.min_age <= age_years <= stage.max_age:
            return stage
    return STAGES[-1]


def stages_from(stage_key: str) -> list[Stage]:
    """주어진 단계부터 마지막(대학)까지의 단계 리스트 (path 생성용)."""
    keys = [s.key for s in STAGES]
    if stage_key not in keys:
        return list(STAGES)
    return STAGES[keys.index(stage_key):]
