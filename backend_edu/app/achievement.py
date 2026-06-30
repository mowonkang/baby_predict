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

# 무료/저렴 공공·온라인 자원 (실제 링크, 2026 기준 — 운영 시 주기적 점검)
_EBS = EduOption(name="EBS", provider="EBS", cost="무료~저렴", note="전 과목 강의", url="https://www.ebs.co.kr/")
_EBS_P = EduOption(name="EBS 초등", provider="EBS", cost="무료", note="초등 강의", url="https://primary.ebs.co.kr/")
_EBS_M = EduOption(name="EBS 중학", provider="EBS", cost="무료~저렴", note="중학 강의(일부 프리미엄)", url="https://mid.ebs.co.kr/")
_EBSI = EduOption(name="EBSi 고교", provider="EBS", cost="무료", note="고교·수능 강의", url="https://www.ebsi.co.kr/")
_EBSE = EduOption(name="EBSe", provider="EBS", cost="무료", note="영어 전문 채널", url="https://www.ebse.co.kr/")
_EBSMATH = EduOption(name="EBS MATH", provider="EBS", cost="무료", note="수학 전문", url="https://www.ebsmath.co.kr/")
_TOCTOC = EduOption(name="똑똑! 수학탐험대", provider="교육부", cost="무료", note="초등 AI 수학(공교육)", url="https://www.toctocmath.kr/")
_KHAN = EduOption(name="칸아카데미 한국어", provider="Khan Academy", cost="무료", note="개념 영상 + 연습", url="https://ko.khanacademy.org/")
_ELEARN = EduOption(name="e학습터", provider="교육부·에듀넷", cost="무료", note="초1~중3 교과 영상·평가", url="https://cls.edunet.net/")
_KOCW = EduOption(name="KOCW 공개강의", provider="KERIS", cost="무료", note="대학 공개강의(심화)", url="http://www.kocw.net/")
_NEULBAEUM = EduOption(name="늘배움(평생학습포털)", provider="국가평생교육진흥원", cost="무료", note="무료 강좌", url="https://www.lifelongedu.go.kr/")
_LIB = EduOption(name="공공도서관 프로그램", provider="지역 도서관", cost="무료/저렴", note="독서·학습 지원(거주지 검색)", url="")
_AISARANG = EduOption(name="아이사랑(임신육아종합포털)", provider="보건복지부", cost="무료", note="영유아 발달·돌보기·검진", url="https://www.childcare.go.kr/")
_TODO = EduOption(name="토도수학/토도한글", provider="에누마", cost="저렴(무료체험)", note="유아~초등 앱", url="https://todoschool.com/")

_FREE_GENERAL: list[EduOption] = [_EBS, _ELEARN, _NEULBAEUM, _LIB]

# 과목 × 학교급별 무료·저렴 자원 (level: 영아/유아/초등/중등/고등, "*"=공통)
_FREE_MAP: dict[str, dict[str, list[EduOption]]] = {
    "수학": {"유아": [_TODO, _TOCTOC], "초등": [_TOCTOC, _EBS_P, _KHAN],
            "중등": [_EBS_M, _KHAN, _ELEARN], "고등": [_EBSI, _EBSMATH, _KHAN]},
    "영어": {"유아": [_EBSE, _EBS_P], "초등": [_EBSE, _EBS_P, _ELEARN],
            "중등": [_EBSE, _EBS_M], "고등": [_EBSI, _EBSE]},
    "국어": {"초등": [_EBS_P, _ELEARN, _LIB], "중등": [_EBS_M, _ELEARN],
            "고등": [_EBSI, _LIB]},
    "과학": {"초등": [_EBS_P, _ELEARN], "중등": [_EBS_M, _ELEARN], "고등": [_EBSI, _KOCW]},
    "사회": {"초등": [_EBS_P, _ELEARN], "중등": [_EBS_M, _ELEARN], "고등": [_EBSI, _KOCW]},
    "한글": {"유아": [_TODO, _ELEARN], "영아": [_AISARANG, _LIB]},
    "기초수": {"유아": [_TODO, _TOCTOC]},
    "독서": {"*": [_LIB, _AISARANG]},
    "애착·정서": {"*": [_AISARANG]}, "언어 자극": {"*": [_AISARANG, _LIB]}, "대·소근육": {"*": [_AISARANG]},
}

# 성취도 입력 과목 → 카탈로그 영역 매칭(유료 학원/인강 후보)
_CATALOG_AREA = {"국어": "국어", "영어": "영어", "수학": "수학", "과학": "과학", "사회": "사회",
                 "한글": "한글", "기초수": "기초수"}


def _free_for(subject: str, level: str) -> list[EduOption]:
    by_level = _FREE_MAP.get(subject)
    if not by_level:
        # 매핑 없으면 학교급별 EBS + e학습터
        ebs = {"초등": _EBS_P, "중등": _EBS_M, "고등": _EBSI}.get(level, _EBS)
        return [ebs, _ELEARN]
    opts = by_level.get(level) or by_level.get("*") or next(iter(by_level.values()))
    return list(opts)[:3]


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
            free=_free_for(subject, grade.level),
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
