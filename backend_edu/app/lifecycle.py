"""전 생애주기 연속 타임라인 (영아 ~ 대학·진로).

'아이의 전 생애 주기'를 하나의 흐름으로 보여준다 — 0~2세 발달부터 진로까지.
나이를 넣으면 '지금 어디인지' 표시하고 앞으로의 단계를 미리 보여준다.
영유아(0~3) 발달은 baby 트랙(backend/)과 연속되는 지점이다.
근거: docs/edu/생애주기_가이드.md
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .models import LifecycleResponse, LifecycleStage


@dataclass(frozen=True)
class LifeStage:
    label: str
    age_label: str
    min_age: int
    max_age: int
    headline: str
    focus: list[str] = field(default_factory=list)


LIFE_STAGES: list[LifeStage] = [
    LifeStage("영아", "0~2세", 0, 2, "애착·언어·놀이로 평생 학습의 토대",
              ["애착·정서", "언어 자극", "대근육 놀이", "발달검진"]),
    LifeStage("유아(유치원)", "3~6세", 3, 6, "책 좋아하는 습관 + 한글·수 놀이",
              ["한글", "기초수", "독서 습관"]),
    LifeStage("초등 저학년", "7~8세", 7, 8, "문해력·연산·학습 습관 만들기",
              ["국어", "수학", "독서"]),
    LifeStage("초등 중학년", "9~10세", 9, 10, "독해·사고력 확장, 흥미 탐색",
              ["국·영·수", "과학·사회"]),
    LifeStage("초등 고학년", "11~12세", 11, 12, "구멍 없는 기본기(중등 연결)",
              ["국·영·수 심화", "진로 탐색"]),
    LifeStage("중등", "13~15세", 13, 15, "내신 + 자유학기 진로탐색·계열 방향",
              ["국·영·수·과·사 내신", "고교 선택"]),
    LifeStage("고등", "16~18세", 16, 18, "내신+학생부+수능(고교학점제)",
              ["내신·수능", "과목 설계", "학생부"]),
    LifeStage("대학·진로", "19세~", 19, 99, "전공·진로 실현, 유망 커리어 준비",
              ["전공", "진로/커리어"]),
]


def build_lifecycle(age_years: int) -> LifecycleResponse:
    # 현재 단계 인덱스(범위 클램프)
    cur = 0
    for i, s in enumerate(LIFE_STAGES):
        if s.min_age <= age_years <= s.max_age:
            cur = i
            break
    else:
        cur = len(LIFE_STAGES) - 1 if age_years > LIFE_STAGES[-1].max_age else 0

    stages = [
        LifecycleStage(label=s.label, age_label=s.age_label, headline=s.headline,
                       focus=s.focus, current=(i == cur))
        for i, s in enumerate(LIFE_STAGES)
    ]
    return LifecycleResponse(current_label=LIFE_STAGES[cur].label, stages=stages)
