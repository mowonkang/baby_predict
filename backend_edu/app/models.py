"""도메인 모델 (Pydantic).

추천·path 엔진의 입력/출력 구조. 상세 설계: docs/edu/추천엔진_설계.md
"""
from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

# Holland RIASEC 흥미 6유형 — docs/edu/추천엔진_설계.md §2.1
RIASEC_DIMENSIONS = (
    "realistic",      # R 현실형
    "investigative",  # I 탐구형
    "artistic",       # A 예술형
    "social",         # S 사회형
    "enterprising",   # E 진취형
    "conventional",   # C 관습형
)

# 학습성향 보조 차원 — §2.2
LEARNING_STYLE_DIMENSIONS = ("self_direction", "collaboration", "analytical")


class InterestVector(BaseModel):
    """RIASEC 흥미 벡터 (각 0~1)."""

    realistic: float = Field(0.5, ge=0.0, le=1.0)
    investigative: float = Field(0.5, ge=0.0, le=1.0)
    artistic: float = Field(0.5, ge=0.0, le=1.0)
    social: float = Field(0.5, ge=0.0, le=1.0)
    enterprising: float = Field(0.5, ge=0.0, le=1.0)
    conventional: float = Field(0.5, ge=0.0, le=1.0)

    def as_dict(self) -> dict[str, float]:
        return {d: getattr(self, d) for d in RIASEC_DIMENSIONS}

    def top_types(self, n: int = 2) -> list[str]:
        """상위 n개 흥미 유형 키를 점수 내림차순으로 반환."""
        return [k for k, _ in sorted(self.as_dict().items(), key=lambda kv: kv[1], reverse=True)[:n]]


class LearningStyle(BaseModel):
    self_direction: float = Field(0.5, ge=0.0, le=1.0, description="자기주도성")
    collaboration: float = Field(0.5, ge=0.0, le=1.0, description="협동 선호")
    analytical: float = Field(0.5, ge=0.0, le=1.0, description="분석 성향")

    def as_dict(self) -> dict[str, float]:
        return {d: getattr(self, d) for d in LEARNING_STYLE_DIMENSIONS}


class AptitudeProfile(BaseModel):
    """적성 프로필 = 흥미 벡터 + 학습성향."""

    interest: InterestVector = Field(default_factory=InterestVector)
    learning_style: LearningStyle = Field(default_factory=LearningStyle)


class SurveyAnswer(BaseModel):
    """적성 진단 설문 1문항 응답 (리커트 1~5)."""

    question_id: str
    value: int = Field(..., ge=1, le=5)


class StudentProfile(BaseModel):
    """추천·path 엔진 입력 프로필."""

    age_years: int = Field(..., ge=3, le=25, description="만 나이")
    region: Optional[str] = Field(None, description="거주 지역")
    budget_max: Optional[int] = Field(
        None, ge=0, description="리소스당 최대 예산(원). None이면 제한 없음"
    )
    # 적성 입력(택1): 관심활동 선택(interests) / 리커트 설문(survey) / 이미 계산된 프로필(aptitude)
    interests: list[str] = Field(default_factory=list, description="선택한 관심활동·학습성향 옵션 id")
    survey: list[SurveyAnswer] = Field(default_factory=list)
    aptitude: Optional[AptitudeProfile] = None


class RecommendationType(str, Enum):
    NATIONAL_PICK = "national_pick"   # 인기(국민) 커리큘럼
    APTITUDE_MATCH = "aptitude_match"  # 적성 맞춤
    STAGE_CORE = "stage_core"          # 단계 핵심 교과/역량


class Recommendation(BaseModel):
    resource_id: str
    name: str
    area: str
    cost: int
    score: float = Field(..., ge=0.0, le=1.0)
    type: RecommendationType
    reasons: list[str]


class PathwayMilestone(BaseModel):
    stage: str
    focus: list[str]
    activities: list[str]
    decision: Optional[str] = None


class EducationPathway(BaseModel):
    recommended_track: str
    rationale: list[str]
    milestones: list[PathwayMilestone]


class RecommendationResponse(BaseModel):
    aptitude: AptitudeProfile
    stage: str
    stage_competencies: list[str]
    study_mode: str  # 학습성향 기반 권장 학습 방식 요약
    recommendations: list[Recommendation]


class PathwayResponse(BaseModel):
    aptitude: AptitudeProfile
    stage: str
    pathway: EducationPathway


class SubjectPick(BaseModel):
    name: str
    area: str
    course_type: str  # 공통 / 일반선택 / 진로선택 / 융합선택
    reasons: list[str]


class SubjectsResponse(BaseModel):
    aptitude: AptitudeProfile
    note: str
    # course_type → 추천 과목 목록
    groups: dict[str, list[SubjectPick]]


class GuideResponse(BaseModel):
    """이 시기에 '무엇을 공부하고 무엇을 준비할지' (일반계 기준)."""

    stage: str
    headline: str
    study: list[str]    # 이 시기 공부할 것
    prepare: list[str]  # 이 시기 준비할 것
    tip: str


class AiTrackResponse(BaseModel):
    """AI 시대 역량 축 — 이 시기에 키울 AI·디지털 역량(계열 공통)."""

    stage: str
    headline: str
    skills: list[str]  # 이 시기 키울 AI·디지털 역량
    tools: list[str]   # 추천 도구·활동
    tip: str


class CareerPick(BaseModel):
    id: str
    name: str
    field: str
    outlook: str           # 전망 한 줄
    fit_reasons: list[str] # 적합 이유
    prepare_now: list[str] # 이 시기 준비할 것
    key_subjects: list[str]  # 핵심 고교 과목


class CareersResponse(BaseModel):
    note: str
    careers: list[CareerPick]
