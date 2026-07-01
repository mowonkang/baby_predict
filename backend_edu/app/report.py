"""부모 리포트 빌더.

현재 프로필로부터 페르소나·이 학년 할 일·보완 과목·주간 학습계획을 한 장으로 요약한다.
LLM 없이 기존 엔진 결과를 조합(추가 과금 0).
"""
from __future__ import annotations

from .achievement import build_achievement
from .grades import build_grade_plan
from .models import ReportResponse, ReportSection, StudentProfile
from .persona import build_persona
from .planner import build_plan


def build_report(profile: StudentProfile) -> ReportResponse:
    gp = build_grade_plan(profile.age_years, profile.grade)
    persona = build_persona(profile)
    plan = build_plan(profile)
    achv = build_achievement(profile.age_years, profile.achievements)

    sections: list[ReportSection] = []

    sections.append(ReportSection(
        title="우리 아이 요약",
        lines=[f"학습 페르소나: {persona.persona_label}",
               f"강점 흥미: {', '.join(persona.top_interests)}",
               f"권장 학습 방식: {persona.study_mode}"]))

    sections.append(ReportSection(
        title=f"{gp.grade} 이 시기에 할 일",
        lines=[t.replace("**", "") for t in gp.todo]))

    if achv.weak:
        lines = []
        for w in achv.weak:
            free = w.free[0].name if w.free else ""
            lines.append(f"[{w.level}] {w.subject} — {w.action} (무료: {free})")
        sections.append(ReportSection(title="보완이 필요한 과목", lines=lines))
    if achv.strong:
        sections.append(ReportSection(title="잘하는 과목(강점 심화)", lines=[", ".join(achv.strong)]))

    if plan.mode == "academic":
        lines = [f"{s.subject}: 주 {s.weekly_hours}시간 — {s.focus.replace('**','')}" for s in plan.sessions]
        lines.append(f"복습: {' · '.join(plan.review)}")
        sections.append(ReportSection(title=f"이번 주 학습 계획(총 {plan.total_weekly_hours}시간)", lines=lines))
    else:
        sections.append(ReportSection(title="이 시기 발달 루틴",
                                      lines=[f"{s.subject}: {s.focus.replace('**','')}" for s in plan.sessions]))

    sections.append(ReportSection(title="한 줄 조언", lines=plan.tips[:2] and [t.replace("**", "") for t in plan.tips[:2]] or ["꾸준함이 가장 큰 힘이에요."]))

    return ReportResponse(grade=gp.grade, persona_label=persona.persona_label, sections=sections)
