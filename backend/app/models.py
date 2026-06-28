"""도메인 모델 (Pydantic).

추천 엔진의 입력/출력 데이터 구조를 정의한다.
상세 설계: docs/추천엔진_설계.md
"""
from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

# 기질(성향) 차원 — docs/추천엔진_설계.md §2.1 참조
TEMPERAMENT_DIMENSIONS = ("activity", "regularity", "adaptability", "intensity", "mood")


class Housing(str, Enum):
    APARTMENT = "apartment"
    HOUSE = "house"
    OTHER = "other"


class TemperamentVector(BaseModel):
    """0~1 로 정규화된 기질 벡터."""

    activity: float = Field(0.5, ge=0.0, le=1.0, description="활동성")
    regularity: float = Field(0.5, ge=0.0, le=1.0, description="규칙성")
    adaptability: float = Field(0.5, ge=0.0, le=1.0, description="적응성")
    intensity: float = Field(0.5, ge=0.0, le=1.0, description="반응 강도")
    mood: float = Field(0.5, ge=0.0, le=1.0, description="긍정 기분 경향")

    def as_dict(self) -> dict[str, float]:
        return {dim: getattr(self, dim) for dim in TEMPERAMENT_DIMENSIONS}


class SurveyAnswer(BaseModel):
    """성향 진단 설문 1문항 응답."""

    question_id: str
    # 1~5 리커트 척도
    value: int = Field(..., ge=1, le=5)


class BabyProfile(BaseModel):
    """추천 엔진 입력 프로필."""

    age_months: int = Field(..., ge=0, le=72, description="월령(개월)")
    region: Optional[str] = Field(None, description="거주 지역(예: 서울)")
    housing: Housing = Housing.APARTMENT
    has_siblings: bool = False
    budget_max: Optional[int] = Field(
        None, ge=0, description="아이템당 최대 예산(원). None이면 제한 없음"
    )
    # 성향: 진단 설문 응답 또는 이미 계산된 벡터 중 하나를 제공
    survey: list[SurveyAnswer] = Field(default_factory=list)
    temperament: Optional[TemperamentVector] = None


class RecommendationType(str, Enum):
    NATIONAL_PICK = "national_pick"  # 국민템
    TEMPERAMENT_MATCH = "temperament_match"  # 성향 맞춤
    DEVELOPMENTAL_PLAY = "developmental_play"  # 발달 놀이/교구


class Recommendation(BaseModel):
    item_id: str
    name: str
    category: str
    price: int
    score: float = Field(..., ge=0.0, le=1.0)
    type: RecommendationType
    reasons: list[str]


class RecommendationResponse(BaseModel):
    temperament: TemperamentVector
    age_band: str
    developmental_tasks: list[str]
    recommendations: list[Recommendation]
