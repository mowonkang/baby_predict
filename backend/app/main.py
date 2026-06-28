"""FastAPI 진입점.

엔드포인트:
  GET  /health           헬스체크
  GET  /api/survey       성향 진단 설문 문항
  POST /api/recommend    프로필 → 추천 결과
  GET  /                 데모 UI(정적 페이지)
"""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from . import __version__
from .models import BabyProfile, RecommendationResponse
from .recommender import recommend
from .temperament import QUESTIONS

app = FastAPI(
    title="baby_predict API",
    version=__version__,
    description="아기 성향·월령 기반 용품 추천 엔진 (MVP)",
)

_STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": __version__}


@app.get("/api/survey")
def get_survey() -> dict:
    """성향 진단 설문 문항 목록."""
    return {
        "questions": [
            {"id": q.id, "text": q.text, "dimension": q.dimension} for q in QUESTIONS
        ],
        "scale": {"min": 1, "max": 5, "labels": ["전혀 아니다", "보통", "매우 그렇다"]},
    }


@app.post("/api/recommend", response_model=RecommendationResponse)
def post_recommend(profile: BabyProfile) -> RecommendationResponse:
    """프로필(월령·성향 설문·환경)을 받아 추천 결과를 반환."""
    return recommend(profile)


# 데모 정적 페이지 (있을 때만 마운트)
if _STATIC_DIR.is_dir():
    @app.get("/")
    def index() -> FileResponse:
        return FileResponse(_STATIC_DIR / "index.html")

    app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")
