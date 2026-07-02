"""통합 결과 요약 — 결과 화면에 필요한 모든 섹션을 한 번에 계산.

기존에는 프론트가 결과 화면에서 API를 16회 호출해(HTTP 왕복 16번 + 적성·능력치 서버 중복
재계산) 특히 모바일에서 느렸다. 이 모듈은 **한 번의 요청**으로 전 섹션을 계산해 반환한다.
개별 엔드포인트는 그대로 유지(하위 호환·부분 갱신용).
"""
from __future__ import annotations

from .academies import recommend_academies
from .achievement import build_achievement
from .ai_track import build_ai_track
from .aptitude import resolve_aptitude
from .careers import recommend_careers
from .cognitive import build_cognitive
from .curriculum import get_stage
from .frameworks import all_frameworks
from .grades import build_grade_plan
from .lifecycle import build_lifecycle
from .models import FrameworksResponse, PathwayResponse, StudentProfile
from .pathway import build_pathway
from .persona import build_persona
from .planner import build_plan
from .projection import build_projection
from .recommender import recommend
from .subjects import recommend_subjects
from .techtree import build_techtree
from .units import build_units
from . import levels


def build_summary(profile: StudentProfile) -> dict:
    """결과 화면 전 섹션을 단일 패스로 계산(무과금·규칙 기반)."""
    aptitude = resolve_aptitude(profile.survey, profile.aptitude, profile.interests)
    weak = [s for s, lv in profile.achievements.items()
            if levels.bucket(lv) in ("weak", "ok")]
    techtree = build_techtree(profile)  # 내부에서 stats 1회 계산 → stat 포함

    return {
        "grade_plan": build_grade_plan(profile.age_years, profile.grade),
        "units": build_units(profile.age_years),
        "study_plan": build_plan(profile),
        "achievement": build_achievement(profile.age_years, profile.achievements, profile.subskills),
        "recommend": recommend(profile),
        "pathway": PathwayResponse(
            aptitude=aptitude, stage=get_stage(profile.age_years).label,
            pathway=build_pathway(profile)),
        "subjects": recommend_subjects(aptitude),
        "ai_track": build_ai_track(profile.age_years),
        "careers": recommend_careers(aptitude, profile.age_years),
        "lifecycle": build_lifecycle(profile.age_years),
        "academies": recommend_academies(profile.age_years, profile.region, weak, profile.budget_max),
        "persona": build_persona(profile),
        "techtree": techtree,
        "cognitive": build_cognitive(profile.behaviors),
        "projection": build_projection(profile),
        "frameworks": FrameworksResponse(frameworks=all_frameworks()),
    }
