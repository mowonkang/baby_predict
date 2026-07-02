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
from .projection import build_projection
from .stats import build_stats
from .temperament import build_temperament


def build_report(profile: StudentProfile) -> ReportResponse:
    gp = build_grade_plan(profile.age_years, profile.grade)
    persona = build_persona(profile)
    plan = build_plan(profile)
    achv = build_achievement(profile.age_years, profile.achievements, profile.subskills)

    sections: list[ReportSection] = []

    sections.append(ReportSection(
        title="우리 아이 요약",
        lines=[f"학습 페르소나: {persona.persona_label}",
               f"강점 흥미: {', '.join(persona.top_interests)}",
               f"권장 학습 방식: {persona.study_mode}"]))

    # 기질(CBQ 착안) — 입력했을 때만
    temp = build_temperament(profile.behaviors)
    if temp.answered:
        sections.append(ReportSection(
            title="기질과 환경 맞춤(조화의 적합성)",
            lines=[f"기질 유형: {temp.type_label}"]
                  + [f"{f.label}: {f.level} — {f.parenting_tip}" for f in temp.factors if f.answered]))

    # 능력치 스탯 — 강점·보강 축 요약(입력이 있어 뚜렷할 때만)
    st = build_stats(profile)
    if st.top_axes:
        lines = [f"육성 타이틀: {st.title} (Lv.{st.overall} {st.overall_level})",
                 f"강점 능력치: {', '.join(st.top_axes)}"]
        if st.growth_axes:
            lines.append(f"보강 능력치: {', '.join(st.growth_axes)}")
        sections.append(ReportSection(title="능력치 프로파일(8각)", lines=lines))

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

    # 예상 전망 — 강점 축 상위 3개의 기본 시나리오(참고)
    proj = build_projection(profile)
    tops = sorted(proj.projections, key=lambda p: p.base - p.now, reverse=True)[:3]
    sections.append(ReportSection(
        title=f"예상 전망 — {proj.horizon_label} (참고)",
        lines=[f"{p.label}: {p.now} → {p.base} (범위 {p.conservative}~{p.optimistic})" for p in tops]
              + ["※ 성장도표·DMGT를 차용한 참고 전망이며 보장이 아닙니다."]))

    sections.append(ReportSection(title="한 줄 조언", lines=plan.tips[:2] and [t.replace("**", "") for t in plan.tips[:2]] or ["꾸준함이 가장 큰 힘이에요."]))

    return ReportResponse(grade=gp.grade, persona_label=persona.persona_label, sections=sections)
