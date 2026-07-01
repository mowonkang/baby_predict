"""단계별 학습·준비 가이드 (일반계 인문/자연 기준).

"이 시기에는 무엇을 공부하고, 무엇을 준비해야 하는가"를 명확히 알려주는 것이
핵심 1차 가치다. 진단 없이 나이만으로도 제공된다.
일반계(대학 진학 중심) 표준 경로에 초점을 둔다.
근거: docs/edu/교육현황_리서치.md §1·§3
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .curriculum import get_stage
from .models import GuideResponse


@dataclass(frozen=True)
class StageGuide:
    stage_key: str
    headline: str
    study: list[str] = field(default_factory=list)
    prepare: list[str] = field(default_factory=list)
    tip: str = ""


# 일반계 표준 경로 기준 단계별 가이드
GUIDES: dict[str, StageGuide] = {
    "preschool": StageGuide(
        "preschool",
        "지금은 '공부=재미'와 책 좋아하는 습관을 만들 때예요",
        study=["한글 떼기(놀이로)", "기초 수 개념·세기", "매일 책 읽어주기"],
        prepare=["바른 생활습관·자기조절", "또래와 어울리기", "다양한 체험으로 흥미 넓히기"],
        tip="선행보다 '책 좋아하는 아이' 만들기가 이후 인문계 학습의 가장 큰 자산이에요.",
    ),
    "elem_low": StageGuide(
        "elem_low",
        "공부 습관과 문해력의 기초를 다지는 시기예요",
        study=["국어 읽기·쓰기 기초", "연산 정확도(서두르지 않기)", "영어 소리·노출 시작", "매일 독서 습관"],
        prepare=["스스로 숙제하는 습관", "바른 글씨·받아쓰기", "한글책 다독"],
        tip="이 시기 핵심은 '학습 습관'과 '문해력' 두 가지예요.",
    ),
    "elem_mid": StageGuide(
        "elem_mid",
        "독해력과 사고력을 키워 모든 과목의 토대를 만드는 시기예요",
        study=["국어 독해력", "수학 개념 이해(서술형)", "영어 읽기", "사회·과학 배경지식(독서)"],
        prepare=["일기·독후감으로 글쓰기", "어휘력 늘리기", "발표 경험"],
        tip="사고력·독해는 이후 모든 과목의 바탕이에요. 흥미 탐색도 함께.",
    ),
    "elem_high": StageGuide(
        "elem_high",
        "중등 연결을 위한 '구멍 없는 기본기'를 만드는 시기예요",
        study=["수학 핵심 개념(분수·비례 등)", "국어 비문학 독해", "영어 문법 기초", "꾸준한 독서"],
        prepare=["자기주도 학습 습관", "중등 학습량 적응", "진로·관심 분야 탐색 시작"],
        tip="무리한 선행보다 '구멍 없는 기본기'가 중·고등 성적을 좌우해요.",
    ),
    "middle": StageGuide(
        "middle",
        "내신 관리와 진로 방향 1차 결정의 시기예요 (일반계 진학 준비)",
        study=["국·영·수 내신 충실", "과학·사회 균형 학습", "영어 독해·어휘 확장", "비문학·문학 독해"],
        prepare=["자유학기 진로탐색 적극 활용", "독서·글쓰기로 생기부 기초 역량", "고교 유형(일반고 기준) 선택 준비"],
        tip="중3에 고교 유형·계열 방향을 1차 결정해요. 일반계는 '내신 + 자기주도 습관'이 핵심.",
    ),
    "high": StageGuide(
        "high",
        "내신·수능·학생부의 균형을 잡는 시기예요 (일반계 인문/자연)",
        study=["내신 전 과목 충실(국·영·수·사/과·한국사)", "수능 국어·수학·영어 + 탐구", "비문학·문학 독해 심화"],
        prepare=["학생부(세특·동아리·독서)에 일관된 진로 서사", "수시(학종/교과) 대비 내신 관리", "2028 통합형 수능·내신 5등급제 대비"],
        tip="일반계는 '내신 + 학생부 서사 + 수능 최저'의 균형. 과목 선택은 희망 계열에 맞춰 일관되게.",
    ),
    "university": StageGuide(
        "university",
        "전공·진로를 실제로 펼치는 시기예요",
        study=["전공 기초·심화", "외국어·교양 역량"],
        prepare=["인턴·대외활동으로 진로 구체화", "자격증·포트폴리오"],
        tip="전공 공부와 함께 '실제 경험'으로 진로를 좁혀 가세요.",
    ),
}


def build_guide(age_years: int) -> GuideResponse:
    stage = get_stage(age_years)
    g = GUIDES.get(stage.key, GUIDES["middle"])
    return GuideResponse(
        stage=stage.label, headline=g.headline,
        study=g.study, prepare=g.prepare, tip=g.tip,
    )
