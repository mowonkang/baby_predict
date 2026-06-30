"""학업 성취 수준 평가 → 과목 보완 + 교육 추천.

과목별 현재 수준(잘함/보통/부족)을 입력받아:
  - 보완이 필요한 과목과 '무엇을 할지(action)'를 제시하고
  - 학원/인강(유료, 카탈로그) + **무료/저렴 대안**(EBS·공공·칸아카데미 등)을 함께 추천한다.
무료·저렴 옵션을 우선 노출해 사교육비 부담을 낮춘다.
근거: docs/edu/교육현황_리서치.md §2·§5·§6
"""
from __future__ import annotations

from .catalog import CATALOG
from .grades import grade_for_age
from .models import AchievementResponse, EduOption, SubjectPlan

# 입력 레벨 정규화
_LEVEL = {
    "잘함": "good", "상": "good", "good": "good",
    "보통": "ok", "중": "ok", "ok": "ok",
    "부족": "weak", "하": "weak", "weak": "weak",
}

_ACTION = {
    "weak": "기초 개념부터 다시 — 진도보다 '구멍 메우기'를 우선하세요.",
    "ok": "취약 단원을 골라 집중하고, 문제풀이로 다지세요.",
    "good": "심화·응용으로 강점을 더 키우세요.",
}

# 무료/저렴 공공·온라인 자원
_FREE_GENERAL: list[EduOption] = [
    EduOption(name="EBS 초등·중학·고교", provider="EBS", cost="무료~저렴", note="학년·과목별 강의(교재만 저렴)"),
    EduOption(name="e학습터 / 위두랑", provider="교육부·시도교육청", cost="무료", note="공공 온라인 학습"),
    EduOption(name="늘배움", provider="국가평생교육진흥원", cost="무료", note="무료 강좌 모음"),
    EduOption(name="공공도서관 프로그램", provider="지역 도서관", cost="무료/저렴", note="독서·학습 지원"),
]
_FREE_BY_SUBJECT: dict[str, list[EduOption]] = {
    "수학": [EduOption(name="칸아카데미 한국어", provider="Khan Academy", cost="무료", note="개념 영상 + 연습 문제")],
    "영어": [EduOption(name="EBSe", provider="EBS", cost="무료", note="영어 전문 무료 채널"),
             EduOption(name="칸아카데미", provider="Khan Academy", cost="무료", note="문법·읽기")],
    "국어": [EduOption(name="EBS 국어 + 도서관 독서", provider="EBS·도서관", cost="무료", note="독해·어휘는 다독이 기본")],
    "과학": [EduOption(name="EBS 과학·유튜브 공개강의", provider="EBS 등", cost="무료", note="개념 영상")],
    "사회": [EduOption(name="EBS 사회·유튜브 공개강의", provider="EBS 등", cost="무료", note="개념 영상")],
}

# 성취도 입력 과목 → 카탈로그 영역 매칭(유료 학원/인강 후보)
_CATALOG_AREA = {"국어": "국어", "영어": "영어", "수학": "수학", "과학": "과학", "사회": "사회",
                 "한글": "한글", "기초수": "기초수"}


def _free_for(subject: str) -> list[EduOption]:
    opts = list(_FREE_BY_SUBJECT.get(subject, []))
    opts.append(_FREE_GENERAL[0])  # EBS 항상
    return opts[:3]


def _paid_for(subject: str, age: int) -> list[EduOption]:
    area = _CATALOG_AREA.get(subject)
    out: list[EduOption] = []
    if area:
        for r in CATALOG:
            if r.area == area and r.min_age <= age <= r.max_age:
                out.append(EduOption(
                    name=r.name, provider=r.resource_type,
                    cost=("무료" if r.cost == 0 else f"유료 약 {r.cost:,}원"),
                    note="입점 리소스(예시)"))
    if not out:
        out.append(EduOption(name="동네 학원·인강 비교", provider="—", cost="유료",
                             note="무료체험 후 우리 아이에 맞는 곳 비교 추천"))
    return out[:2]


def build_achievement(age_years: int, achievements: dict[str, str]) -> AchievementResponse:
    grade = grade_for_age(age_years)
    weak: list[SubjectPlan] = []
    strong: list[str] = []
    for subject, raw in achievements.items():
        level = _LEVEL.get(str(raw).strip(), "ok")
        if level == "good":
            strong.append(subject)
            continue
        weak.append(SubjectPlan(
            subject=subject,
            level=("부족" if level == "weak" else "보통"),
            action=_ACTION[level],
            paid=_paid_for(subject, age_years),
            free=_free_for(subject),
        ))
    # 부족 → 보통 순으로
    weak.sort(key=lambda s: 0 if s.level == "부족" else 1)
    if weak:
        note = "보완이 필요한 과목입니다. 비용 부담이 크면 무료·저렴 옵션부터 시작해 보세요."
    elif strong:
        note = "입력한 과목이 모두 양호해요. 강점을 심화로 더 키워 보세요."
    else:
        note = "과목 수준을 입력하면 보완 과목과 무료·저렴 교육을 추천해 드려요."
    return AchievementResponse(grade=grade.label, note=note, weak=weak, strong=strong)
