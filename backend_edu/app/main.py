"""FastAPI 진입점 (EduPath).

엔드포인트:
  GET  /health           헬스체크
  GET  /api/survey       적성 진단 설문 문항
  POST /api/recommend    프로필 → 커리큘럼 추천
  POST /api/pathway      프로필 → 교육 path(로드맵)
  GET  /                 데모 UI(정적 페이지)
"""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from . import __version__
from .achievement import build_achievement
from .ai_track import build_ai_track
from .aptitude import ACTIVITY_OPTIONS, QUESTIONS, STYLE_OPTIONS, resolve_aptitude
from .careers import recommend_careers
from .curriculum import get_stage
from .grades import GRADES, build_grade_plan
from .guide import build_guide
from .models import (
    AchievementResponse,
    AiTrackResponse,
    CareersResponse,
    GradePlanResponse,
    GuideResponse,
    PathwayResponse,
    RecommendationResponse,
    StudentProfile,
    SubjectsResponse,
)
from .pathway import build_pathway
from .recommender import recommend
from .subjects import recommend_subjects

app = FastAPI(
    title="EduPath API",
    version=__version__,
    description="학생 적성·학령 기반 커리큘럼 추천 + 교육 path 엔진 (MVP)",
)

_STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": __version__}


@app.get("/api/survey")
def get_survey() -> dict:
    """(레거시) 리커트 적성 진단 설문 문항."""
    return {
        "questions": [
            {"id": q.id, "text": q.text, "dimension": q.dimension} for q in QUESTIONS
        ],
        "scale": {"min": 1, "max": 5, "labels": ["전혀 아니다", "보통", "매우 그렇다"]},
    }


@app.get("/api/activities")
def get_activities() -> dict:
    """쉬운 진단용 — 해당되는 것을 고르는 관심활동·학습성향 옵션."""
    return {
        "interests": [{"id": o.id, "label": o.label} for o in ACTIVITY_OPTIONS],
        "styles": [{"id": o.id, "label": o.label} for o in STYLE_OPTIONS],
    }


@app.post("/api/guide", response_model=GuideResponse)
def post_guide(profile: StudentProfile) -> GuideResponse:
    """이 시기에 무엇을 공부하고 무엇을 준비할지 (일반계 기준, 진단 불필요)."""
    return build_guide(profile.age_years)


@app.get("/api/grades")
def get_grades() -> dict:
    """학년 목록 (유치원~고3)."""
    return {"grades": [{"key": g.key, "label": g.label} for g in GRADES]}


@app.post("/api/grade-plan", response_model=GradePlanResponse)
def post_grade_plan(profile: StudentProfile) -> GradePlanResponse:
    """이 학년에 할 것 + 핵심 과목 (유치원~고3, 인문계 기준)."""
    return build_grade_plan(profile.age_years, profile.grade)


@app.post("/api/achievement", response_model=AchievementResponse)
def post_achievement(profile: StudentProfile) -> AchievementResponse:
    """과목별 성취수준(잘함/보통/부족) → 보완 과목 + 학원·무료/저렴 교육 추천."""
    return build_achievement(profile.age_years, profile.achievements)


@app.post("/api/recommend", response_model=RecommendationResponse)
def post_recommend(profile: StudentProfile) -> RecommendationResponse:
    """프로필(학령·적성 설문·환경)을 받아 커리큘럼 추천을 반환."""
    return recommend(profile)


@app.post("/api/pathway", response_model=PathwayResponse)
def post_pathway(profile: StudentProfile) -> PathwayResponse:
    """프로필을 받아 미취학~대학 교육 path(로드맵)를 반환."""
    aptitude = resolve_aptitude(profile.survey, profile.aptitude, profile.interests)
    stage = get_stage(profile.age_years)
    return PathwayResponse(
        aptitude=aptitude, stage=stage.label, pathway=build_pathway(profile)
    )


@app.post("/api/subjects", response_model=SubjectsResponse)
def post_subjects(profile: StudentProfile) -> SubjectsResponse:
    """프로필을 받아 적성 기반 고교 과목(2022 개정: 공통/일반/진로/융합선택) 추천."""
    aptitude = resolve_aptitude(profile.survey, profile.aptitude, profile.interests)
    return recommend_subjects(aptitude)


@app.post("/api/ai-track", response_model=AiTrackResponse)
def post_ai_track(profile: StudentProfile) -> AiTrackResponse:
    """AI 시대 역량 축 — 이 시기에 키울 AI·디지털 역량(계열 공통, 진단 불필요)."""
    return build_ai_track(profile.age_years)


@app.post("/api/careers", response_model=CareersResponse)
def post_careers(profile: StudentProfile) -> CareersResponse:
    """적성 기반 유망 커리어(로보틱스·공학·화학·바이오·의학·AI 등) 추천 + 준비 커리큘럼."""
    aptitude = resolve_aptitude(profile.survey, profile.aptitude, profile.interests)
    return recommend_careers(aptitude, profile.age_years)


# 데모 정적 페이지 (있을 때만 마운트)
if _STATIC_DIR.is_dir():
    @app.get("/")
    def index() -> FileResponse:
        return FileResponse(_STATIC_DIR / "index.html")

    app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")
