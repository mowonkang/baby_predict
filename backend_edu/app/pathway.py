"""교육 path 생성기 (신규 핵심 기능).

docs/edu/추천엔진_설계.md §6 구현.
적성(RIASEC 상위 유형) → 진로 계열 path 템플릿 → 현재 단계부터 대학까지 마일스톤 생성.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .curriculum import Stage, get_stage, stages_from
from .models import (
    AptitudeProfile,
    EducationPathway,
    PathwayMilestone,
    StudentProfile,
)
from .aptitude import resolve_aptitude


@dataclass(frozen=True)
class TrackTemplate:
    name: str  # 진로 계열
    # 단계 key → 집중 영역(없으면 단계 핵심 영역으로 폴백)
    focus_by_stage: dict[str, list[str]] = field(default_factory=dict)
    # 단계 key → 핵심 활동
    activities_by_stage: dict[str, list[str]] = field(default_factory=dict)


# 단계별 표준 의사결정 포인트 (계열 공통)
# 실제 제도 반영: 자유학기(중1 진로탐색)·고교학점제(고1 과목선택)·2028 통합형 수능/내신 5등급제.
# 근거: docs/edu/교육현황_리서치.md
_DECISION_BY_STAGE: dict[str, str] = {
    "elem_high": "선행/심화 범위와 진로 탐색 방향 설정 (중1 자유학기 진로탐색 대비)",
    "middle": "고교 유형(일반/특목/자사/특성화) 선택 — 2028 통합형 수능·내신 5등급제 고려",
    "high": "고교학점제 선택과목·세특, 수시(학종/교과)/정시 전략 및 세부 전공 확정",
}

# RIASEC 우세 유형 → 진로 계열 트랙
_TRACKS: dict[str, TrackTemplate] = {
    "investigative": TrackTemplate(
        name="이공/자연·공학 계열",
        focus_by_stage={
            "preschool": ["수·과학 호기심", "탐구 놀이"],
            "elem_low": ["기초 연산", "독서"],
            "elem_mid": ["수학 사고력", "과학 탐구"],
            "elem_high": ["수학 심화", "코딩 입문"],
            "middle": ["수학·과학 심화"],
            "high": ["이과 내신·수능 수학/과학", "탐구 연구활동"],
            "university": ["공학/자연계열 진학"],
        },
        activities_by_stage={
            "elem_mid": ["과학 실험 키트"], "elem_high": ["수학 경시 준비"],
            "middle": ["과학 탐구대회"], "high": ["R&E·연구 활동"],
        },
    ),
    "realistic": TrackTemplate(
        name="공학·기술 계열",
        focus_by_stage={
            "elem_mid": ["만들기·코딩"], "elem_high": ["로봇·SW 기초"],
            "middle": ["수학·과학 + SW"], "high": ["공학 전공 기초", "프로젝트 활동"],
            "university": ["공학/기술계열 진학"],
        },
        activities_by_stage={
            "elem_high": ["코딩·로봇 교실"], "middle": ["코딩 경진대회"],
            "high": ["메이커·프로젝트"],
        },
    ),
    "artistic": TrackTemplate(
        name="예술·디자인 계열",
        focus_by_stage={
            "preschool": ["미술·음악 체험"],
            "elem_mid": ["창작 기초", "악기/미술"],
            "elem_high": ["전공 흥미 탐색", "실기 기초"],
            "middle": ["실기 역량", "예중/예고 검토"],
            "high": ["전공 실기·포트폴리오", "수능 최저 관리"],
            "university": ["예술/디자인계열 진학"],
        },
        activities_by_stage={
            "elem_mid": ["미술·음악 클래스"], "middle": ["실기 학원·공모전"],
            "high": ["포트폴리오·입시 실기"],
        },
    ),
    "social": TrackTemplate(
        name="교육·사회·인문 계열",
        focus_by_stage={
            "elem_mid": ["독서·토론", "글쓰기"],
            "elem_high": ["국어·영어 역량", "리더십"],
            "middle": ["국어·사회 심화", "동아리 활동"],
            "high": ["사회탐구·논술", "봉사·세특"],
            "university": ["교육/사회/인문계열 진학"],
        },
        activities_by_stage={
            "elem_high": ["토론·리더십 클럽"], "middle": ["학생회·동아리"],
            "high": ["봉사·사회참여 활동"],
        },
    ),
    "enterprising": TrackTemplate(
        name="경영·상경 계열",
        focus_by_stage={
            "elem_high": ["수학·영어", "리더십"],
            "middle": ["수학·사회", "기획·발표"],
            "high": ["사회탐구·경제", "대외활동"],
            "university": ["경영/경제계열 진학"],
        },
        activities_by_stage={
            "elem_high": ["리더십 클럽"], "middle": ["창업·경제 캠프"],
            "high": ["경영·창업 대외활동"],
        },
    ),
    "conventional": TrackTemplate(
        name="상경·행정·회계 계열",
        focus_by_stage={
            "elem_high": ["수학·정리력"],
            "middle": ["수학·사회", "꼼꼼한 학습관리"],
            "high": ["사회탐구·경제·수학", "정량 역량"],
            "university": ["상경/행정계열 진학"],
        },
        activities_by_stage={
            "middle": ["경제·회계 기초"], "high": ["통계·데이터 활동"],
        },
    ),
}

# 일반계 기본(default) 트랙 — 뚜렷한 강점이 드러나기 전/콜드스타트의 표준 경로(인문·자연 미정).
_GENERAL_TRACK = TrackTemplate(
    name="일반계 (인문·자연 탐색 중)",
    focus_by_stage={
        "preschool": ["한글·기초수", "책 읽기 습관"],
        "elem_low": ["국어 문해력", "기초 연산", "독서 습관"],
        "elem_mid": ["독해력", "수학 개념", "글쓰기"],
        "elem_high": ["국·영·수 기본기", "자기주도 학습"],
        "middle": ["국·영·수 내신", "진로 탐색", "독서·글쓰기"],
        "high": ["내신 전 과목", "수능 국·영·수+탐구", "학생부 서사"],
        "university": ["희망 계열 진학"],
    },
    activities_by_stage={
        "middle": ["자유학기 진로탐색"], "high": ["동아리·세특·독서활동"],
    },
)

_DIM_LABEL = {
    "realistic": "현실형(R)", "investigative": "탐구형(I)", "artistic": "예술형(A)",
    "social": "사회형(S)", "enterprising": "진취형(E)", "conventional": "관습형(C)",
}


def _select_track(aptitude: AptitudeProfile) -> tuple[TrackTemplate, bool]:
    """상위 흥미 유형으로 트랙 선택. 뚜렷한 강점이 없으면 일반계 기본 트랙.
    반환: (트랙, 일반계 기본 여부)."""
    interest = aptitude.interest.as_dict()
    top = aptitude.interest.top_types(2)
    primary = top[0]
    # 강점이 뚜렷하지 않으면(최고 흥미가 중립 이하) 일반계 기본 트랙
    if interest[primary] <= 0.5:
        return _GENERAL_TRACK, True
    # 진취형이 우세하고 사회형이 동반되면 경영 계열로
    if primary == "enterprising" and "social" in top:
        return _TRACKS["enterprising"], False
    return _TRACKS.get(primary, _GENERAL_TRACK), False


def build_pathway(profile: StudentProfile) -> EducationPathway:
    aptitude = resolve_aptitude(profile.survey, profile.aptitude, profile.interests)
    track, is_general = _select_track(aptitude)
    current: Stage = get_stage(profile.age_years)

    milestones: list[PathwayMilestone] = []
    for stage in stages_from(current.key):
        focus = track.focus_by_stage.get(stage.key) or stage.core_areas
        activities = track.activities_by_stage.get(stage.key) or stage.activity_types
        milestones.append(
            PathwayMilestone(
                stage=stage.label,
                focus=focus,
                activities=activities,
                decision=_DECISION_BY_STAGE.get(stage.key),
            )
        )

    if is_general:
        rationale = [
            "아직 뚜렷한 강점이 드러나지 않아, 일반계 표준 경로(기본기 + 진로 탐색)를 권장합니다.",
            "관심 활동을 더 선택하면 계열 맞춤 로드맵으로 좁혀집니다.",
        ]
    else:
        top = aptitude.interest.top_types(2)
        rationale = [
            f"{' · '.join(_DIM_LABEL.get(t, t) for t in top)} 흥미가 우세하여 '{track.name}' path를 제안"
        ]
    return EducationPathway(
        recommended_track=track.name, rationale=rationale, milestones=milestones
    )
