"""학년별 가이드 (유치원 ~ 고3, 인문계 기준).

주 기능: 나이/학년별로 '이 학년에는 무엇을 해야 하는지'를 정리해 제공한다.
인문계(대학 진학 중심) 표준 경로 기준. 진단 없이 나이만으로 동작.
"""
from __future__ import annotations

from dataclasses import dataclass

from .models import GradePlanResponse


@dataclass(frozen=True)
class Grade:
    key: str
    label: str
    min_age: int
    max_age: int
    level: str  # 유아 / 초등 / 중등 / 고등


GRADES: list[Grade] = [
    Grade("k", "유치원", 3, 6, "유아"),
    Grade("e1", "초1", 7, 7, "초등"),
    Grade("e2", "초2", 8, 8, "초등"),
    Grade("e3", "초3", 9, 9, "초등"),
    Grade("e4", "초4", 10, 10, "초등"),
    Grade("e5", "초5", 11, 11, "초등"),
    Grade("e6", "초6", 12, 12, "초등"),
    Grade("m1", "중1", 13, 13, "중등"),
    Grade("m2", "중2", 14, 14, "중등"),
    Grade("m3", "중3", 15, 15, "중등"),
    Grade("h1", "고1", 16, 16, "고등"),
    Grade("h2", "고2", 17, 17, "고등"),
    Grade("h3", "고3", 18, 25, "고등"),
]


def grade_for_age(age_years: int) -> Grade:
    if age_years <= GRADES[0].max_age:
        return GRADES[0]
    for g in GRADES:
        if g.min_age <= age_years <= g.max_age:
            return g
    return GRADES[-1]


def grade_by_key(key: str) -> Grade | None:
    return next((g for g in GRADES if g.key == key), None)


# 학년별 핵심 과목 (성취도 입력·보완 대상)
def core_subjects(grade: Grade) -> list[str]:
    if grade.key == "k":
        return ["한글", "기초수", "독서"]
    if grade.key in ("e1", "e2"):
        return ["국어", "수학", "영어"]
    if grade.level == "고등":
        return ["국어", "영어", "수학", "사회", "과학"]
    # 초3~6, 중등
    return ["국어", "영어", "수학", "과학", "사회"]


# 학년별 '이 학년에 할 것' (인문계 기준)
GRADE_PLAN: dict[str, list[str]] = {
    "k": ["한글 자모·낱말 익히기(놀이로)", "수 세기·기초 연산 개념", "매일 책 읽어주기로 어휘·집중력", "바른 생활습관"],
    "e1": ["받침 있는 글자 읽기·쓰기", "한 자리 덧셈·뺄셈 정확히", "매일 그림책·동화 읽기", "연필 바르게 잡고 또박또박 쓰기"],
    "e2": ["문장 읽고 이해하기", "두 자리 덧셈·뺄셈, 구구단", "일기 쓰기 습관", "영어 알파벳·파닉스 노출"],
    "e3": ["글의 중심내용 파악(독해 시작)", "곱셈·나눗셈, 분수 입문", "영어 기초 단어·읽기", "과학·사회 호기심(독서·체험)"],
    "e4": ["문단 독해·요약", "분수·소수 연산", "영어 문장 읽기", "사회·과학 기본 개념 정리"],
    "e5": ["설명문·논설문 독해", "약수·배수·분수 계산", "영어 문법 기초·독해", "중등 대비 학습량 적응"],
    "e6": ["비문학 독해력 키우기", "비·비율·도형(중등 연결)", "영어 문법·어휘 확장", "자기주도 학습 습관(중학 대비)"],
    "m1": ["국어 문법·문학 기초", "정수·일차방정식 등 중등수학 적응", "영어 독해·어휘 확장", "자유학기 진로탐색 활용"],
    "m2": ["내신 시험 대비 시작", "함수·도형 등 수학 누적 관리", "영어 독해·문법 심화", "과학·사회 개념 정리"],
    "m3": ["고입 대비 내신 마무리", "수학 기초 구멍 점검(고교 연결)", "영어 독해 속도·어휘", "고교 유형·계열 방향 1차 결정"],
    "h1": ["공통과목 내신 집중(국·영·수·통합사·통합과)", "수능 국·영·수 기초 다지기", "2~3학년 선택과목 설계 시작", "학생부(독서·동아리) 시작"],
    "h2": ["선택과목 내신 + 수능 본격", "수학·탐구 심화", "학생부 세특에 일관된 진로 서사", "모의고사로 약점 보완"],
    "h3": ["수능·내신 마무리, 약점 집중 보완", "수시(학종/교과)·정시 전략 확정", "면접/논술·자기소개 대비", "실전·컨디션 관리"],
}

# 학교급별 한 줄 팁
LEVEL_TIP: dict[str, str] = {
    "유아": "선행보다 '책 좋아하는 아이'와 바른 습관이 가장 큰 자산이에요.",
    "초등": "이 시기 핵심은 '문해력 + 학습 습관'. 구멍 없는 기본기가 중·고등을 좌우해요.",
    "중등": "내신과 자기주도 습관을 만들고, 진로 방향을 탐색하는 시기예요.",
    "고등": "일반계는 '내신 + 학생부 서사 + 수능'의 균형. 약점 과목을 일찍 메우세요.",
}


def build_grade_plan(age_years: int, grade_key: str | None = None) -> GradePlanResponse:
    grade = grade_by_key(grade_key) if grade_key else None
    if grade is None:
        grade = grade_for_age(age_years)
    return GradePlanResponse(
        grade=grade.label, level=grade.level,
        subjects=core_subjects(grade),
        todo=GRADE_PLAN.get(grade.key, []),
        tip=LEVEL_TIP.get(grade.level, ""),
    )
