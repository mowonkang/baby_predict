"""고교 과목 구조 모델링 (2022 개정 교육과정).

과목 유형: 공통 / 일반선택 / 진로선택 / 융합선택.
각 과목을 흥미(RIASEC) 차원에 매핑해, 적성 기반으로 '계열 적합 과목'을 추천한다.
이는 고교학점제(2025~) 하에서 '과목 선택 → 학생부 역량 서사 → 전형 적합도'를 잇는
차별화 기능의 1차 구현이다.
근거: docs/edu/교육현황_리서치.md §1·§3·(시사점 c)
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .models import AptitudeProfile, SubjectPick, SubjectsResponse

COMMON = "공통"
GENERAL = "일반선택"
CAREER = "진로선택"
FUSION = "융합선택"

_DIM_LABEL = {
    "realistic": "현실형(R)",
    "investigative": "탐구형(I)",
    "artistic": "예술형(A)",
    "social": "사회형(S)",
    "enterprising": "진취형(E)",
    "conventional": "관습형(C)",
}


@dataclass(frozen=True)
class Subject:
    name: str
    area: str
    course_type: str
    riasec: frozenset[str] = field(default_factory=frozenset)  # 비어있으면 전계열 공통


# 대표 과목 세트(2022 개정). 운영 시 교육과정 원문·대학 권장이수과목으로 확장.
SUBJECTS: list[Subject] = [
    # --- 공통(1학년, 전계열) ---
    Subject("공통국어1", "국어", COMMON),
    Subject("공통수학1", "수학", COMMON),
    Subject("공통영어1", "영어", COMMON),
    Subject("통합사회1", "사회", COMMON),
    Subject("통합과학1", "과학", COMMON),
    Subject("한국사1", "사회", COMMON),
    # --- 일반선택 ---
    Subject("대수", "수학", GENERAL, frozenset({"investigative", "conventional"})),
    Subject("미적분Ⅰ", "수학", GENERAL, frozenset({"investigative"})),
    Subject("확률과 통계", "수학", GENERAL, frozenset({"investigative", "conventional"})),
    Subject("물리학", "과학", GENERAL, frozenset({"investigative", "realistic"})),
    Subject("화학", "과학", GENERAL, frozenset({"investigative"})),
    Subject("생명과학", "과학", GENERAL, frozenset({"investigative", "social"})),
    Subject("지구과학", "과학", GENERAL, frozenset({"investigative", "realistic"})),
    Subject("독서와 작문", "국어", GENERAL, frozenset({"social", "artistic"})),
    Subject("문학", "국어", GENERAL, frozenset({"artistic", "social"})),
    Subject("영어Ⅰ", "영어", GENERAL, frozenset({"social"})),
    Subject("사회와 문화", "사회", GENERAL, frozenset({"social"})),
    Subject("세계사", "사회", GENERAL, frozenset({"social", "artistic"})),
    Subject("음악", "예술", GENERAL, frozenset({"artistic"})),
    Subject("미술", "예술", GENERAL, frozenset({"artistic"})),
    Subject("정보", "정보", GENERAL, frozenset({"realistic", "investigative"})),
    # --- 진로선택 ---
    Subject("미적분Ⅱ", "수학", CAREER, frozenset({"investigative"})),
    Subject("기하", "수학", CAREER, frozenset({"investigative", "realistic"})),
    Subject("경제 수학", "수학", CAREER, frozenset({"enterprising", "conventional"})),
    Subject("인공지능 수학", "수학", CAREER, frozenset({"investigative", "realistic"})),
    Subject("역학과 에너지", "과학", CAREER, frozenset({"investigative", "realistic"})),
    Subject("전자기와 양자", "과학", CAREER, frozenset({"investigative", "realistic"})),
    Subject("세포와 물질대사", "과학", CAREER, frozenset({"investigative"})),
    Subject("정치", "사회", CAREER, frozenset({"enterprising", "social"})),
    Subject("법과 사회", "사회", CAREER, frozenset({"conventional", "enterprising"})),
    Subject("경제", "사회", CAREER, frozenset({"enterprising", "conventional"})),
    Subject("윤리와 사상", "사회", CAREER, frozenset({"social", "artistic"})),
    Subject("국제관계의 이해", "사회", CAREER, frozenset({"social", "enterprising"})),
    Subject("인공지능 기초", "정보", CAREER, frozenset({"investigative", "realistic"})),
    Subject("데이터 과학", "정보", CAREER, frozenset({"investigative", "conventional"})),
    Subject("음악 연주와 창작", "예술", CAREER, frozenset({"artistic"})),
    Subject("미술 창작", "예술", CAREER, frozenset({"artistic"})),
    Subject("영미 문학 읽기", "영어", CAREER, frozenset({"artistic", "social"})),
    # --- 융합선택 ---
    Subject("사회문제 탐구", "사회", FUSION, frozenset({"social", "investigative"})),
    Subject("금융과 경제생활", "사회", FUSION, frozenset({"enterprising", "conventional"})),
    Subject("기후변화와 환경생태", "과학", FUSION, frozenset({"investigative", "social"})),
    Subject("융합과학 탐구", "과학", FUSION, frozenset({"investigative"})),
    Subject("실용 통계", "수학", FUSION, frozenset({"conventional", "investigative"})),
    Subject("수학과제 탐구", "수학", FUSION, frozenset({"investigative"})),
    Subject("여행지리", "사회", FUSION, frozenset({"artistic", "social"})),
    Subject("매체 의사소통", "국어", FUSION, frozenset({"social", "artistic"})),
]

# 적성이 중립(콜드스타트)일 때 보여줄 기본 일반선택
_FALLBACK_GENERAL = {"대수", "미적분Ⅰ", "영어Ⅰ", "독서와 작문"}

_ELECTIVE_TYPES = (GENERAL, CAREER, FUSION)
_MAX_PER_TYPE = 6


def _contrib(interest: dict[str, float], dim: str) -> float:
    """중립(0.5) 초과분만 점수로 인정 → 진짜 높은 흥미만 반영."""
    return max(0.0, interest.get(dim, 0.5) - 0.5)


def _subject_score(subject: Subject, interest: dict[str, float]) -> float:
    return sum(_contrib(interest, d) for d in subject.riasec)


def _best_dim(subject: Subject, interest: dict[str, float]) -> str | None:
    best, val = None, -1.0
    for d in subject.riasec:
        c = _contrib(interest, d)
        if c > val:
            best, val = d, c
    return best


def recommend_subjects(aptitude: AptitudeProfile) -> SubjectsResponse:
    """적성(흥미) 기반 고교 과목 추천. 공통은 항상 포함, 선택과목은 상위 흥미 유형과 매칭."""
    interest = aptitude.interest.as_dict()
    top = set(aptitude.interest.top_types(3))
    # 흥미가 모두 중립(콜드스타트)인지 판단
    neutral = all(abs(v - 0.5) < 1e-6 for v in interest.values())

    groups: dict[str, list[SubjectPick]] = {COMMON: [], GENERAL: [], CAREER: [], FUSION: []}

    # 공통: 전부 포함
    for s in SUBJECTS:
        if s.course_type == COMMON:
            groups[COMMON].append(
                SubjectPick(name=s.name, area=s.area, course_type=COMMON,
                            reasons=["1학년 공통과목 — 전 계열 공통 기초"])
            )

    # 선택과목: 점수화 후 매칭
    for ctype in _ELECTIVE_TYPES:
        picks: list[tuple[float, SubjectPick]] = []
        for s in SUBJECTS:
            if s.course_type != ctype:
                continue
            if neutral:
                if ctype == GENERAL and s.name in _FALLBACK_GENERAL:
                    picks.append((1.0, SubjectPick(
                        name=s.name, area=s.area, course_type=ctype,
                        reasons=["진단 전 기본 추천 — 적성 진단 후 맞춤화됩니다"])))
                continue
            if not (s.riasec & top):
                continue
            score = _subject_score(s, interest)
            dim = _best_dim(s, interest)
            reason = f"{_DIM_LABEL.get(dim, dim)} 적성에 맞는 {s.area} {ctype}" if dim else f"{s.area} {ctype}"
            picks.append((score, SubjectPick(name=s.name, area=s.area, course_type=ctype, reasons=[reason])))
        picks.sort(key=lambda x: x[0], reverse=True)
        groups[ctype] = [p for _, p in picks[:_MAX_PER_TYPE]]

    note = (
        "적성 진단 전 기본 과목입니다. 진단을 완료하면 맞춤 추천됩니다."
        if neutral
        else "2022 개정 교육과정 과목 구조 기반 적성 맞춤 추천 (참고용)."
    )
    return SubjectsResponse(aptitude=aptitude, note=note, groups=groups)
