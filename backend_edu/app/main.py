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
from .aptitude import QUESTIONS, resolve_aptitude
from .curriculum import get_stage
from .models import (
    PathwayResponse,
    RecommendationResponse,
    StudentProfile,
)
from .pathway import build_pathway
from .recommender import recommend

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
    """적성 진단 설문 문항 목록 (흥미 RIASEC + 학습성향)."""
    return {
        "questions": [
            {"id": q.id, "text": q.text, "dimension": q.dimension} for q in QUESTIONS
        ],
        "scale": {"min": 1, "max": 5, "labels": ["전혀 아니다", "보통", "매우 그렇다"]},
    }


@app.post("/api/recommend", response_model=RecommendationResponse)
def post_recommend(profile: StudentProfile) -> RecommendationResponse:
    """프로필(학령·적성 설문·환경)을 받아 커리큘럼 추천을 반환."""
    return recommend(profile)


@app.post("/api/pathway", response_model=PathwayResponse)
def post_pathway(profile: StudentProfile) -> PathwayResponse:
    """프로필을 받아 미취학~대학 교육 path(로드맵)를 반환."""
    aptitude = resolve_aptitude(profile.survey, profile.aptitude)
    stage = get_stage(profile.age_years)
    return PathwayResponse(
        aptitude=aptitude, stage=stage.label, pathway=build_pathway(profile)
    )


# 데모 정적 페이지 (있을 때만 마운트)
if _STATIC_DIR.is_dir():
    @app.get("/")
    def index() -> FileResponse:
        return FileResponse(_STATIC_DIR / "index.html")

    app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")
