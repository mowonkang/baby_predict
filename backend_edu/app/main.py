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

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from . import __version__
from .academies import get_reviews, recommend_academies, submit_review
from .achievement import build_achievement
from .ai_track import build_ai_track
from .aptitude import ACTIVITY_OPTIONS, QUESTIONS, STYLE_OPTIONS, resolve_aptitude
from .careers import recommend_careers
from .curriculum import get_stage
from .diagnostic import grade_answer, items_for
from .grades import GRADES, build_grade_plan
from .guide import build_guide
from .lifecycle import build_lifecycle
from .mastery import (
    level_from_mastery,
    mastery_from_seq,
    p_correct_next,
    percentile,
    recommend_difficulty,
    review_interval_days,
)
from .persona import build_persona
from .planner import build_plan
from .report import build_report
from .stats import build_stats
from .techtree import build_techtree
from .extracurricular import CATEGORIES, EXTRACURRICULARS
from .local import build_local_hub
from . import cognitive, community, levels, subskill, temperament
from .frameworks import all_frameworks
from .projection import build_projection
from .models import (
    AchievementResponse,
    AiTrackResponse,
    CareersResponse,
    CognitiveItemsResponse,
    CognitiveProfile,
    FrameworksResponse,
    ProjectionResponse,
    SubskillOptionsResponse,
    TemperamentItemsResponse,
    TemperamentProfile,
    CommunityCommentSubmit,
    CommunityListResponse,
    CommunityPost,
    CommunityPostSubmit,
    ExtracurricularOption,
    ExtracurricularOptionsResponse,
    LocalHubResponse,
    StatProfile,
    TechTreeResponse,
    GradePlanResponse,
    GuideResponse,
    LifecycleResponse,
    PathwayResponse,
    RecommendationResponse,
    AcademiesResponse,
    DiagnosticItem,
    DiagnosticResponse,
    MasteryRequest,
    MasteryResponse,
    MasterySubject,
    PersonaResponse,
    ReportResponse,
    ReviewsResponse,
    ReviewSubmit,
    StudentProfile,
    StudyPlanResponse,
    SubjectsResponse,
    SyncSave,
    UnitsResponse,
)
from .store import load_profile, save_profile
from .units import build_units
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
    """과목별 성취수준(잘함/보통/부족) → 보완 과목 + 학원·무료/저렴 교육 추천 + 하위스킬 또래비교."""
    return build_achievement(profile.age_years, profile.achievements, profile.subskills)


@app.post("/api/lifecycle", response_model=LifecycleResponse)
def post_lifecycle(profile: StudentProfile) -> LifecycleResponse:
    """전 생애주기 타임라인(영아~대학·진로) + 현재 위치."""
    return build_lifecycle(profile.age_years)


@app.post("/api/units", response_model=UnitsResponse)
def post_units(profile: StudentProfile) -> UnitsResponse:
    """이번 학년 단원 + 단원별 무료강의 링크(칸아카데미·EBS)."""
    return build_units(profile.age_years)


@app.post("/api/plan", response_model=StudyPlanResponse)
def post_plan(profile: StudentProfile) -> StudyPlanResponse:
    """적응형 주간 학습 계획(규칙 기반, 추가 과금 없음) — 시간배분·할일·목표·무료자료·복습."""
    return build_plan(profile)


@app.post("/api/diagnostic", response_model=DiagnosticResponse)
def post_diagnostic(profile: StudentProfile) -> DiagnosticResponse:
    """학년대에 맞는 미니 진단 문항(수학·영어 등). 정답은 노출하지 않음."""
    from .diagnostic import band_for_age
    items = items_for(profile.age_years)
    note = ("" if items else "이 나이대는 미니 진단 대신 놀이·자가체크를 사용해요.")
    return DiagnosticResponse(
        band=band_for_age(profile.age_years),
        items=[DiagnosticItem(id=i.id, subject=i.subject, difficulty=i.difficulty,
                              question=i.question, options=i.options, unit=i.unit,
                              reviewed=i.reviewed) for i in items],
        note=note or "문항은 예시이며 전문가 검수 후 확대 예정입니다.")


@app.post("/api/mastery", response_model=MasteryResponse)
def post_mastery(req: MasteryRequest) -> MasteryResponse:
    """미니 진단 응답 → 과목별 숙련도(BKT). LLM 호출 없음."""
    seqs: dict[str, list[bool]] = {}
    for a in req.answers:
        graded = grade_answer(a.item_id, a.choice)
        if graded is None:
            continue
        subject, correct = graded
        seqs.setdefault(subject, []).append(correct)
    subjects = []
    for subject, seq in seqs.items():
        m = mastery_from_seq(seq)
        subjects.append(MasterySubject(
            subject=subject, mastery=m, level=level_from_mastery(m),
            p_correct_next=p_correct_next(m), answered=len(seq),
            percentile=percentile(m), recommended_difficulty=recommend_difficulty(m),
            review_in_days=review_interval_days(m)))
    subjects.sort(key=lambda s: s.mastery)  # 약한 과목 먼저
    return MasteryResponse(subjects=subjects)


@app.post("/api/report", response_model=ReportResponse)
def post_report(profile: StudentProfile) -> ReportResponse:
    """부모 리포트 — 페르소나·이 학년 할 일·보완·주간 계획 요약(무과금)."""
    return build_report(profile)


@app.post("/api/persona", response_model=PersonaResponse)
def post_persona(profile: StudentProfile) -> PersonaResponse:
    """페르소나(Learner Profile) — 흥미·학습성향·성취 통합 라벨."""
    return build_persona(profile)


@app.get("/api/extracurriculars", response_model=ExtracurricularOptionsResponse)
def get_extracurriculars() -> ExtracurricularOptionsResponse:
    """쉬운 입력용 — 사교육·활동(몬테소리·영어·태권도·미술 등) 계열별 선택지."""
    return ExtracurricularOptionsResponse(
        categories=list(CATEGORIES),
        options=[ExtracurricularOption(id=e.id, label=e.label, category=e.category)
                 for e in EXTRACURRICULARS])


@app.post("/api/stats", response_model=StatProfile)
def post_stats(profile: StudentProfile) -> StatProfile:
    """능력치 스탯(8각형 레이더) — 관심·경험·성취·행동관찰을 규칙으로 합산(무과금)."""
    return build_stats(profile)


@app.get("/api/cognitive-items", response_model=CognitiveItemsResponse)
def get_cognitive_items() -> CognitiveItemsResponse:
    """관찰형 인지 성향 행동 문항(WISC 5영역 착안). 성향을 몰라도 행동으로 답할 수 있어요."""
    return CognitiveItemsResponse(
        scale=cognitive.SCALE, items=cognitive.items(),
        note="관찰 가능한 행동에 빈도로 답하세요. 임상 지능검사·진단이 아닌 참고용입니다.")


@app.post("/api/cognitive", response_model=CognitiveProfile)
def post_cognitive(profile: StudentProfile) -> CognitiveProfile:
    """행동 문항 응답 → 5영역 인지 성향 프로파일(또래 대비 밴드, 진단 아님, 무과금)."""
    return cognitive.build_cognitive(profile.behaviors)


@app.get("/api/temperament-items", response_model=TemperamentItemsResponse)
def get_temperament_items() -> TemperamentItemsResponse:
    """기질 관찰 문항(Rothbart CBQ 3요인 착안: 외향성·정서민감성·의도적조절). 진단 아님."""
    return TemperamentItemsResponse(
        scale=temperament.SCALE, items=temperament.items(),
        note="기질에는 좋고 나쁨이 없어요 — 아이에게 맞는 환경(조화의 적합성)을 찾기 위한 참고입니다.")


@app.post("/api/temperament", response_model=TemperamentProfile)
def post_temperament(profile: StudentProfile) -> TemperamentProfile:
    """행동 응답(tp_*) → 기질 3요인 프로파일 + 유형 + 환경 가이드(무과금, 진단 아님)."""
    return temperament.build_temperament(profile.behaviors)


@app.post("/api/projection", response_model=ProjectionResponse)
def post_projection(profile: StudentProfile) -> ProjectionResponse:
    """예상 능력치 전망 — 성장도표 개념 + Gagné DMGT 촉매 논리(낙관/기본/보수 3밴드, 참고용)."""
    return build_projection(profile)


@app.get("/api/frameworks", response_model=FrameworksResponse)
def get_frameworks() -> FrameworksResponse:
    """본 서비스가 차용한 공신력 평가·발달 체계 목록(투명성 공개)."""
    return FrameworksResponse(frameworks=all_frameworks())


@app.get("/api/subskills", response_model=SubskillOptionsResponse)
def get_subskills(age: int | None = None) -> SubskillOptionsResponse:
    """과목 하위 스킬 목록(수학=연산·개념·응용 등). 나이에 맞는 과목만. 또래 대비 5단계."""
    return SubskillOptionsResponse(
        subjects=subskill.subjects(age), items=subskill.options(age),
        levels=[l["label"] for l in levels.LEVELS5])


@app.get("/api/local-hub", response_model=LocalHubResponse)
def get_local_hub(region: str = "", subject: str = "수학") -> LocalHubResponse:
    """지역·과목 → 실제 학원 목록 + 지도(카카오/네이버) + 맘카페 커뮤니티 딥링크."""
    return build_local_hub(region, subject)


@app.get("/api/community", response_model=CommunityListResponse)
def get_community(region: str = "", topic: str = "") -> CommunityListResponse:
    """지역·주제별 인앱 커뮤니티 글 목록(엄마들 의견 나누기)."""
    return community.list_posts(region, topic)


@app.post("/api/community", response_model=CommunityPost)
def post_community(body: CommunityPostSubmit) -> CommunityPost:
    """커뮤니티 글 작성."""
    return community.create_post(body.region, body.topic, body.title, body.body, body.author)


@app.post("/api/community/{post_id}/comment")
def post_community_comment(post_id: str, body: CommunityCommentSubmit) -> dict:
    """커뮤니티 글에 댓글(의견) 작성."""
    if not community.add_comment(post_id, body.author, body.text):
        raise HTTPException(status_code=404, detail="글을 찾을 수 없습니다.")
    return {"ok": True}


@app.post("/api/community/{post_id}/like")
def post_community_like(post_id: str) -> dict:
    """커뮤니티 글 공감(좋아요)."""
    likes = community.like_post(post_id)
    if likes is None:
        raise HTTPException(status_code=404, detail="글을 찾을 수 없습니다.")
    return {"ok": True, "likes": likes}


@app.post("/api/techtree", response_model=TechTreeResponse)
def post_techtree(profile: StudentProfile) -> TechTreeResponse:
    """사교육 전체 테크트리 + 능력치·나이 기반 추천 루트(스타크래프트식, 무과금)."""
    return build_techtree(profile)


@app.post("/api/academies", response_model=AcademiesResponse)
def post_academies(profile: StudentProfile) -> AcademiesResponse:
    """지역·약점 과목·학년 기반 학원 추천(입점=광고 별도 표기)."""
    from . import levels
    weak = [s for s, lv in profile.achievements.items()
            if levels.bucket(lv) in ("weak", "ok")]
    return recommend_academies(profile.age_years, profile.region, weak, profile.budget_max)


@app.get("/api/academies/{academy_id}/reviews", response_model=ReviewsResponse)
def get_academy_reviews(academy_id: str) -> ReviewsResponse:
    """학원 평점·리뷰(학원/선생님/강의) 조회."""
    res = get_reviews(academy_id)
    if res is None:
        raise HTTPException(status_code=404, detail="학원을 찾을 수 없습니다.")
    return res


@app.post("/api/reviews")
def post_review(body: ReviewSubmit) -> dict:
    """리뷰 작성(서버 저장). 선생님·강의 평 포함."""
    ok = submit_review(body.academy_id, body.rating, body.text, body.target_type, body.target_name)
    if not ok:
        raise HTTPException(status_code=404, detail="학원을 찾을 수 없습니다.")
    return {"ok": True}


@app.post("/api/sync/save")
def post_sync_save(body: SyncSave) -> dict:
    """동기화 코드로 프로필·이력을 서버에 저장(여러 기기 공유)."""
    try:
        save_profile(body.code, body.payload)
    except ValueError:
        raise HTTPException(status_code=400, detail="동기화 코드를 입력하세요.")
    return {"ok": True}


@app.get("/api/sync/{code}")
def get_sync(code: str) -> dict:
    """동기화 코드로 저장된 프로필·이력 조회."""
    data = load_profile(code)
    if data is None:
        raise HTTPException(status_code=404, detail="해당 코드로 저장된 데이터가 없습니다.")
    return {"payload": data}


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
