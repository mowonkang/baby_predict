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

    age_years: int = Field(..., ge=0, le=25, description="만 나이(0세 영아부터)")
    grade: Optional[str] = Field(None, description="학년 키(e3, m1 등). 없으면 나이로 추론")
    region: Optional[str] = Field(None, description="거주 지역")
    budget_max: Optional[int] = Field(
        None, ge=0, description="리소스당 최대 예산(원). None이면 제한 없음"
    )
    # 적성 입력(택1): 관심활동 선택(interests) / 리커트 설문(survey) / 이미 계산된 프로필(aptitude)
    interests: list[str] = Field(default_factory=list, description="선택한 관심활동·학습성향 옵션 id")
    survey: list[SurveyAnswer] = Field(default_factory=list)
    aptitude: Optional[AptitudeProfile] = None
    # 과목별 현재 수준(잘함/보통/부족) — 보완 추천용
    achievements: dict[str, str] = Field(default_factory=dict)
    # 주당 학습 가능 시간(시간). 없으면 학교급 기본값 사용
    weekly_hours: Optional[int] = Field(None, ge=0, le=80)
    # 경험했거나 관심 있는 사교육·활동 옵션 id(몬테소리·영어·태권도 등) — 능력치·테크트리용
    activities: list[str] = Field(default_factory=list, description="선택한 사교육·활동 경험/관심 옵션 id")


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


class GradePlanResponse(BaseModel):
    """이 학년에 할 것 (유치원~고3, 인문계 기준)."""

    grade: str
    level: str
    subjects: list[str]   # 핵심 과목(성취도 입력 대상)
    todo: list[str]       # 이 학년에 할 것
    tip: str
    source: str = "2022 개정 교육과정 / 누리과정"
    updated: str = "2026-06"


class Unit(BaseModel):
    subject: str
    name: str          # 단원명
    provider: str
    cost: str
    url: str


class UnitsResponse(BaseModel):
    grade: str
    units: list[Unit]
    source: str = "2022 개정 교육과정"
    updated: str = "2026-06"


class SyncSave(BaseModel):
    code: str          # 동기화 코드(사용자 지정)
    payload: dict      # 프로필·이력 등


class AcademyPick(BaseModel):
    id: str
    name: str
    type: str          # 학원 / 인강 / 공부방
    subjects: list[str]
    region: str        # 지역(온라인 포함)
    price: int         # 월 비용(원), 0=무료/문의
    rating: float      # 평점(0~5)
    review_count: int
    sponsored: bool    # 입점(스폰서) 여부
    reasons: list[str]
    url: str = ""


class AcademiesResponse(BaseModel):
    region: str
    weak_subjects: list[str]
    note: str
    sponsored: list[AcademyPick]  # 입점(광고) — 별도 표기
    organic: list[AcademyPick]    # 일반 추천(평점·매칭 순)


class Review(BaseModel):
    target_type: str   # 학원 / 선생님 / 강의
    target_name: str
    rating: int        # 1~5
    text: str
    date: str = ""


class ReviewsResponse(BaseModel):
    academy_id: str
    academy_name: str
    avg_rating: float
    count: int
    reviews: list[Review]


class ReviewSubmit(BaseModel):
    academy_id: str
    rating: int = Field(..., ge=1, le=5)
    text: str = Field(..., min_length=1, max_length=500)
    target_type: str = "학원"   # 학원/선생님/강의
    target_name: str = ""


class StudySession(BaseModel):
    subject: str
    level: str          # 부족/보통/잘함/기본
    weekly_hours: float
    focus: str          # 이번 주 할 일
    goal: str           # 미니 목표
    resource: EduOption # 무료/저렴 우선 자료


class StudyPlanResponse(BaseModel):
    """적응형 주간 학습 계획 (규칙 기반, LLM 호출 없음)."""

    grade: str
    mode: str                 # academic / developmental
    total_weekly_hours: float
    sessions: list[StudySession]
    review: list[str]         # 복습(망각 방지) 항목
    tips: list[str]
    source: str = "2022 개정 교육과정 기반 규칙 엔진"
    updated: str = "2026-06"


class DiagnosticItem(BaseModel):
    id: str
    subject: str
    difficulty: str
    question: str
    options: list[str]
    unit: str = ""            # 정답은 노출하지 않음
    reviewed: bool = False    # 전문가 검수 여부


class DiagnosticResponse(BaseModel):
    band: Optional[str]
    items: list[DiagnosticItem]
    note: str = ""


class MasteryAnswer(BaseModel):
    item_id: str
    choice: int


class MasteryRequest(BaseModel):
    answers: list[MasteryAnswer]


class MasterySubject(BaseModel):
    subject: str
    mastery: float            # 숙련 확률(0~1)
    level: str                # 부족/보통/잘함
    p_correct_next: float     # 다음 정답 확률
    answered: int
    percentile: int = 50            # 또래 대비 추정 백분위(IRT, 참고)
    recommended_difficulty: str = "중"  # 적정 난이도(상/중/하)
    review_in_days: int = 7         # 다음 복습까지 일수(분산복습)


class MasteryResponse(BaseModel):
    subjects: list[MasterySubject]
    note: str = "BKT(베이지안 지식추적) 기반 추정 — LLM 호출 없음."


class PersonaResponse(BaseModel):
    interest: InterestVector
    learning_style: LearningStyle
    top_interests: list[str]
    persona_label: str        # 예: "탐구형·자기주도 학습자"
    study_mode: str
    subject_levels: dict[str, str]
    note: str


class ReportSection(BaseModel):
    title: str
    lines: list[str]


class ReportResponse(BaseModel):
    """부모 리포트 — 페르소나·할 일·보완·계획 요약."""

    grade: str
    persona_label: str
    sections: list[ReportSection]
    note: str = "본 리포트는 참고용이며 예시 데이터가 포함될 수 있습니다."


class EduOption(BaseModel):
    name: str
    provider: str
    cost: str   # "무료" / "저렴" / "유료 약 N원" 등
    note: str
    url: str = ""  # 실제 링크(있으면)


class SubjectPlan(BaseModel):
    subject: str
    level: str    # 부족 / 보통
    action: str
    paid: list[EduOption]  # 학원/인강(유료)
    free: list[EduOption]  # 무료/저렴 대안


class AchievementResponse(BaseModel):
    grade: str
    note: str
    weak: list[SubjectPlan]  # 보완 필요 과목
    strong: list[str]        # 양호 과목


class LifecycleStage(BaseModel):
    label: str
    age_label: str
    headline: str
    focus: list[str]
    current: bool


class LifecycleResponse(BaseModel):
    current_label: str
    stages: list[LifecycleStage]


# ── 육성 엔진(프린세스 메이커식): 능력치 스탯 + 사교육 테크트리 ──────────
class StatAxis(BaseModel):
    """능력치 1축 (게임처럼 0~100)."""

    key: str          # language / logic / science ...
    label: str        # 언어 / 수리·논리 ...
    value: int = Field(..., ge=0, le=100)
    level: str        # 새싹 / 성장 / 우수 / 탁월
    top: bool = False  # 상위(강점) 축 여부


class StatProfile(BaseModel):
    """8각형 능력치 프로필 (레이더 차트용)."""

    axes: list[StatAxis]
    top_axes: list[str]        # 강점 축 라벨(상위 2~3)
    growth_axes: list[str]     # 보강 축 라벨(하위 1~2)
    headline: str              # 한 줄 요약(예: "탐구·언어형 새싹")
    overall: int = 40          # 종합 능력치(축 평균, 0~100)
    overall_level: str = "새싹"  # 종합 레벨 라벨
    title: str = "탐색가"       # 육성 타이틀(프린세스메이커식 캐릭터 정체성)
    note: str = "입력(관심활동·경험·성취)을 규칙 기반으로 합산한 참고용 능력치 — LLM 호출 없음."
    source_signals: list[str] = Field(default_factory=list)  # 어떤 입력이 반영됐는지


class TechNode(BaseModel):
    """테크트리 노드 = 하나의 사교육/활동 단계 (스타크래프트 테크 유닛처럼)."""

    id: str
    label: str
    tier: int              # 0=유아, 1=초등, 2=중등, 3=고등/진로
    age_hint: str          # "5~7세" 등
    stat: str              # 주로 키우는 능력치 key
    requires: list[str] = Field(default_factory=list)  # 선행 노드 id
    cost_band: str = "중"   # 대략 비용대(무료/저/중/고)
    free_alt: str = ""     # 무료·저가 대안 한 줄
    recommended: bool = False  # 추천 루트에 포함?
    reason: str = ""       # 추천 이유(추천 노드일 때)
    done: bool = False     # 이미 경험한 단계(입력한 활동 반영)


class TechTrack(BaseModel):
    """능력치 계열별 테크트리(어학·사고력·예술·체육·기초인성 등)."""

    key: str
    label: str
    stat: str              # 이 트랙이 키우는 대표 능력치 key
    nodes: list[TechNode]  # tier 순 정렬
    recommended: bool = False  # 이 트랙 자체가 추천 계열인지


class TechTreeResponse(BaseModel):
    """사교육 전체 테크트리 + 추천 루트."""

    stat: StatProfile
    tracks: list[TechTrack]        # 전체 계열 트리
    route: list[TechNode]          # 추천 루트(현재 나이·경험 기준 다음 스텝, tier 순)
    recommended_tracks: list[str]  # 강점 기반 추천 계열 라벨
    done_count: int = 0            # 이미 경험한 단계 수(입력 활동 반영)
    budget_conscious: bool = False  # 예산 빠듯 → 무료·저가 대안 우선 권장
    note: str = "능력치·나이·경험을 규칙으로 매칭한 추천 루트 — 예시 포함, LLM 호출 없음."


class ExtracurricularOption(BaseModel):
    """쉬운 입력용 사교육/활동 선택지."""

    id: str
    label: str
    category: str   # 어학 / 사고력 / 예술 / 체육 / 기초·인성


class ExtracurricularOptionsResponse(BaseModel):
    categories: list[str]
    options: list[ExtracurricularOption]
