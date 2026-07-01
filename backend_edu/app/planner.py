"""적응형 학습 계획기 (규칙 기반 — LLM 호출 없음, 추가 과금 0).

성취도(잘함/보통/부족) + 학년 + 주당 가용 시간으로 **주간 학습 계획**을 생성한다.
- 약점 과목에 시간을 더 배분(가중치), 과목별 '이번 주 할 일·미니 목표·무료자료' 제시
- 잘하는 과목은 '복습(망각 방지)' 슬롯으로 유지
- 영아·유아는 시간표 대신 '매일 놀이·대화·책읽기' 발달 루틴
성취 이력이 쌓이면(프론트) 지난 대비 변화로 자동 적응 메모를 보여준다.
"""
from __future__ import annotations

from .achievement import _free_for
from .grades import core_subjects, grade_for_age
from .models import EduOption, StudentProfile, StudyPlanResponse, StudySession

# 학교급별 기본 주당 학습시간(자기학습 기준, 예시)
_DEFAULT_HOURS = {"영아": 0, "유아": 3, "초등": 6, "중등": 9, "고등": 12}

from . import levels

# 레벨 가중치(시간 배분)
_WEIGHT = {"부족": 3.0, "보통": 2.0, "잘함": 1.0, "기본": 2.0}

_ACADEMIC_ACTION = {
    "부족": ("기초 개념부터 — 쉬운 단원 영상 보고 따라 풀기", "핵심 개념 1개 확실히 이해하기"),
    "보통": ("취약 단원 골라 문제풀이로 다지기", "자주 틀리는 유형 2개 정복하기"),
    "잘함": ("심화·응용 + 주 1회 복습으로 유지", "심화 1단계 도전하기"),
    "기본": ("교과 진도 따라 매일 조금씩", "이번 주 배운 내용 복습하기"),
}
_DEV_ACTION = {
    "애착·정서": ("눈맞춤·반응·안아주기로 정서 안정", "매일 충분한 상호작용"),
    "언어 자극": ("많이 말 걸고 그림책 읽어주기", "새 낱말·표현 들려주기"),
    "대·소근육": ("기기·걷기·잡기 등 몸놀이", "안전한 환경에서 대근육 활동"),
    "한글": ("놀이로 자모·낱말 익히기", "좋아하는 책 반복해 읽기"),
    "기초수": ("세기·모으기 등 수 놀이", "생활 속 수 개념 경험"),
    "독서": ("매일 책 읽어주기·함께 보기", "책과 친해지기"),
}


def _norm(level: str) -> str:
    return levels.coarse(level)


def build_plan(profile: StudentProfile) -> StudyPlanResponse:
    grade = grade_for_age(profile.age_years)
    developmental = grade.level in ("영아", "유아")

    # 대상 과목: 성취 입력이 있으면 그 과목, 없으면 학년 핵심 과목(기본)
    if profile.achievements:
        subjects = {s: _norm(lv) for s, lv in profile.achievements.items()}
    else:
        subjects = {s: "기본" for s in core_subjects(grade)}

    total = profile.weekly_hours if profile.weekly_hours is not None else _DEFAULT_HOURS.get(grade.level, 6)

    sessions: list[StudySession] = []
    review: list[str] = []

    if developmental:
        # 발달 루틴(시간표 대신 매일 활동)
        for s in subjects:
            focus, goal = _DEV_ACTION.get(s, ("매일 놀이·상호작용", "즐겁게 경험하기"))
            res = _free_for(s, grade.level)[0]
            sessions.append(StudySession(subject=s, level="기본", weekly_hours=0.0,
                                         focus=focus, goal=goal, resource=res))
        tips = ["이 시기는 시간표보다 **매일의 놀이·대화·책읽기**가 핵심이에요.",
                "발달은 개인차가 커요 — 비교보다 우리 아이 속도에 맞춰요."]
        return StudyPlanResponse(grade=grade.label, mode="developmental",
                                 total_weekly_hours=0.0, sessions=sessions,
                                 review=["매일 같은 책 반복 읽기(애착·언어에 좋아요)"], tips=tips)

    # 학습(초~고): 가중치로 시간 배분
    weights = {s: _WEIGHT.get(lv, 2.0) for s, lv in subjects.items()}
    wsum = sum(weights.values()) or 1.0
    for s, lv in subjects.items():
        hrs = round(total * weights[s] / wsum, 1)
        if hrs < 0.5:
            hrs = 0.5
        focus, goal = _ACADEMIC_ACTION.get(lv, _ACADEMIC_ACTION["기본"])
        res = _free_for(s, grade.level)[0]
        sessions.append(StudySession(subject=s, level=lv, weekly_hours=hrs,
                                     focus=focus, goal=goal, resource=res))
        if lv == "잘함":
            review.append(f"{s}: 주 1회 복습으로 실력 유지")
    # 우선순위: 약점 과목 먼저(시간 큰 순)
    sessions.sort(key=lambda x: x.weekly_hours, reverse=True)

    if not review:
        review.append("배운 단원은 1~2주 뒤 한 번 더 복습하면 오래 기억돼요(분산 복습).")
    tips = [
        "약점 과목에 시간을 더 배분했어요. **무료강의로 먼저** 시도하고 막히면 보완하세요.",
        "한 번에 길게보다 **짧게 자주**가 효과적이에요.",
    ]
    return StudyPlanResponse(grade=grade.label, mode="academic",
                             total_weekly_hours=round(sum(s.weekly_hours for s in sessions), 1),
                             sessions=sessions, review=review, tips=tips)
