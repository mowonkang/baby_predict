"""AI 시대 역량 축.

계열·진로와 무관하게 모든 학생에게 적용되는 '하나의 축' — 이 시기에 키울
AI·디지털 역량을 단계별로 제시한다. 진단 없이 나이만으로 제공.

핵심 관점(근거: 에듀테크/AI 동향, docs/edu/교육현황_리서치.md §5):
AI 시대일수록 ① 문해력·수학 기본기 ② 비판적 사고 ③ AI를 '도구'로 다루는 능력이 중요.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .curriculum import get_stage
from .models import AiTrackResponse

_TIP = "AI 시대일수록 ①문해력·수학 기본기 ②비판적 사고(AI 답을 의심하기) ③AI를 '도구'로 쓰는 힘이 핵심이에요."


@dataclass(frozen=True)
class AiStage:
    stage_key: str
    headline: str
    skills: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)


AI_STAGES: dict[str, AiStage] = {
    "preschool": AiStage(
        "preschool", "지금은 '화면'보다 '경험'으로 호기심을 키울 때",
        skills=["디지털 기기 사용 균형·절제", "관찰·질문하는 호기심"],
        tools=["교육용 앱은 짧게(부모와 함께)", "블록·만들기 놀이"],
    ),
    "elem_low": AiStage(
        "elem_low", "컴퓨터와 친해지고 코딩의 첫발을 떼는 시기",
        skills=["타자·기본 기기 사용", "블록코딩 입문(스크래치·엔트리)"],
        tools=["스크래치/엔트리", "안전한 검색 습관"],
    ),
    "elem_mid": AiStage(
        "elem_mid", "디지털로 만들어 보고, 정보를 가려내는 힘을 기르는 시기",
        skills=["블록코딩 프로젝트(게임·애니)", "정보 검색·진위 판별(디지털 리터러시)"],
        tools=["생성형 AI로 그림·이야기 체험(부모 지도)", "코딩 보드(마이크로비트 등)"],
    ),
    "elem_high": AiStage(
        "elem_high", "텍스트 코딩과 데이터·AI 윤리의 기초를 잡는 시기",
        skills=["파이썬 입문(텍스트 코딩)", "데이터·표 개념", "AI 윤리·저작권 기초"],
        tools=["파이썬 기초 강의", "엔트리 AI 블록"],
    ),
    "middle": AiStage(
        "middle", "코딩·데이터·생성형 AI 활용법을 익히는 시기",
        skills=["파이썬 기초", "데이터 다루기(표·그래프)", "생성형 AI 활용·한계 이해(프롬프트)"],
        tools=["정보 교과 충실", "AI 도구로 학습 보조(검증하며)"],
    ),
    "high": AiStage(
        "high", "전공+AI 융합과 'AI로 생산성 높이기'를 실천하는 시기",
        skills=["AI·데이터 활용 프로젝트(세특 연계)", "통계·미적분 기반 이해", "도메인+AI 융합(예: 과학+AI)"],
        tools=["파이썬/데이터 분석", "AI 도구로 자료조사·정리(출처 검증)"],
    ),
    "university": AiStage(
        "university", "전공과 AI를 결합해 실전 결과물을 만드는 시기",
        skills=["전공+AI 융합 프로젝트", "실전 데이터·모델 활용"],
        tools=["오픈소스·포트폴리오", "도메인 특화 AI 도구"],
    ),
}


def build_ai_track(age_years: int) -> AiTrackResponse:
    stage = get_stage(age_years)
    a = AI_STAGES.get(stage.key, AI_STAGES["middle"])
    return AiTrackResponse(
        stage=stage.label, headline=a.headline, skills=a.skills, tools=a.tools, tip=_TIP
    )
