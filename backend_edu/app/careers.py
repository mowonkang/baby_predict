"""유망 커리어 맞춤 커리큘럼.

로보틱스·공학·화학·바이오/생명공학·의학 + AI/데이터 등 유망 분야별로
'적성 적합도 + 단계별 준비 커리큘럼 + 핵심 고교 과목'을 제공한다.
적성(흥미 RIASEC)에 맞는 커리어를 추천하고, 각 커리어의 '지금 준비할 것'을 보여준다.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .curriculum import get_stage
from .models import AptitudeProfile, CareerPick, CareersResponse

_DIM_LABEL = {
    "realistic": "현실형(R)", "investigative": "탐구형(I)", "artistic": "예술형(A)",
    "social": "사회형(S)", "enterprising": "진취형(E)", "conventional": "관습형(C)",
}


@dataclass(frozen=True)
class Career:
    id: str
    name: str
    field: str
    riasec: frozenset[str]
    outlook: str
    key_subjects: list[str]
    prepare: dict[str, list[str]] = field(default_factory=dict)  # stage_key → 준비할 것


CAREERS: list[Career] = [
    Career(
        "ai_data", "AI·데이터 사이언티스트", "AI/데이터",
        frozenset({"investigative", "realistic", "conventional"}),
        "AI 시대 전 산업의 핵심 수요 — 고성장 분야",
        ["미적분Ⅱ", "확률과 통계", "인공지능 수학", "인공지능 기초", "데이터 과학"],
        {"elem_high": ["파이썬 입문", "수학 개념 탄탄히"],
         "middle": ["파이썬·데이터 다루기", "수학 심화", "정보 교과"],
         "high": ["AI/데이터 프로젝트(세특)", "통계·미적분", "정보 심화"],
         "university": ["머신러닝·통계 전공", "캐글·프로젝트 포트폴리오"]},
    ),
    Career(
        "robotics", "로보틱스 엔지니어", "로보틱스",
        frozenset({"realistic", "investigative"}),
        "제조·물류·의료 자동화로 수요 확대",
        ["물리학", "기하", "인공지능 기초", "역학과 에너지", "정보"],
        {"elem_high": ["코딩·로봇 키트", "수·과학 기본기"],
         "middle": ["코딩 경진대회", "수학·과학 심화", "메이커 활동"],
         "high": ["물리·수학 집중", "로봇/제어 프로젝트(세특)"],
         "university": ["기계·전자·SW 융합 전공", "로봇 대회·연구"]},
    ),
    Career(
        "mech_eng", "기계·자동차 공학자", "공학",
        frozenset({"realistic", "investigative"}),
        "전기차·항공·로봇 등 견조한 수요",
        ["물리학", "기하", "미적분Ⅱ", "역학과 에너지"],
        {"middle": ["수학·과학(물리) 심화", "만들기·설계 흥미"],
         "high": ["물리·수학 집중", "공학 프로젝트·동아리"],
         "university": ["기계공학 전공", "캡스톤·인턴"]},
    ),
    Career(
        "elec_semi", "전기·전자/반도체 공학자", "공학",
        frozenset({"investigative", "realistic"}),
        "반도체·전력 등 국가전략산업 고수요",
        ["물리학", "미적분Ⅱ", "전자기와 양자", "인공지능 수학"],
        {"middle": ["수학·과학(물리) 심화", "전자·코딩 체험"],
         "high": ["물리·수학 집중", "전자·반도체 탐구활동"],
         "university": ["전자공학·반도체 전공", "연구·인턴"]},
    ),
    Career(
        "chem_mat", "화학·신소재 연구자", "화학",
        frozenset({"investigative", "realistic"}),
        "이차전지·신소재·정밀화학 성장",
        ["화학", "물질과 에너지", "미적분Ⅰ", "융합과학 탐구"],
        {"middle": ["과학(화학) 흥미·실험", "수학 기본기"],
         "high": ["화학·수학 집중", "화학 실험·탐구활동(세특)"],
         "university": ["화학·신소재 전공", "연구실 인턴"]},
    ),
    Career(
        "bio_eng", "바이오·생명공학 연구자", "바이오/생명공학",
        frozenset({"investigative", "social"}),
        "제약·바이오·합성생물학 고성장",
        ["생명과학", "화학", "세포와 물질대사", "융합과학 탐구"],
        {"middle": ["과학(생명) 흥미·독서", "수학 기본기"],
         "high": ["생명과학·화학 집중", "생명 탐구·실험활동(세특)"],
         "university": ["생명공학·바이오 전공", "연구실·논문 활동"]},
    ),
    Career(
        "med", "의학·보건 (의사·의생명)", "의학",
        frozenset({"investigative", "social"}),
        "고령화로 의료수요 지속 + 디지털헬스 확장",
        ["생명과학", "화학", "미적분Ⅰ", "확률과 통계"],
        {"middle": ["전 과목 내신 최상위 습관", "생명·화학 흥미"],
         "high": ["내신 최상위 + 생명·화학", "의료·생명 탐구활동(세특)"],
         "university": ["의대/의생명 전공", "임상·연구 경험"]},
    ),
    Career(
        "env_energy", "환경·에너지 전문가", "환경/에너지",
        frozenset({"investigative", "social", "realistic"}),
        "탄소중립·신재생으로 수요 증가",
        ["화학", "지구과학", "기후변화와 환경생태"],
        {"middle": ["과학·사회(환경) 관심", "수학 기본기"],
         "high": ["과학+사회 융합 탐구", "환경 프로젝트·동아리"],
         "university": ["환경·에너지 공학 전공", "현장·연구 활동"]},
    ),
    Career(
        "design_tech", "디자인·콘텐츠 기술가", "디자인/콘텐츠",
        frozenset({"artistic", "realistic"}),
        "AI 융합 콘텐츠·UX/UI 수요 확대",
        ["미술 창작", "정보", "음악 연주와 창작"],
        {"middle": ["창작 활동 + 디지털 도구", "코딩 체험"],
         "high": ["실기·포트폴리오 + AI 도구", "콘텐츠 프로젝트"],
         "university": ["디자인·미디어·HCI 전공", "포트폴리오"]},
    ),
]

# 적성 중립(콜드스타트) 시 보여줄 대표 유망 분야
_DEFAULT_IDS = ["ai_data", "bio_eng", "robotics", "med"]
_GENERIC_PREPARE = ["기초 학습 습관", "관심 분야 책·체험으로 흥미 탐색"]


def _fit(career: Career, interest: dict[str, float]) -> tuple[float, str | None]:
    """적합 점수(중립 초과분 합)와 가장 크게 기여한 차원."""
    total, best, best_c = 0.0, None, 0.0
    for d in career.riasec:
        c = max(0.0, interest.get(d, 0.5) - 0.5)
        total += c
        if c > best_c:
            best, best_c = d, c
    return total, best


def recommend_careers(aptitude: AptitudeProfile, age_years: int, top_k: int = 4) -> CareersResponse:
    interest = aptitude.interest.as_dict()
    stage = get_stage(age_years)
    neutral = all(abs(v - 0.5) < 1e-6 for v in interest.values())

    def pick(career: Career, reasons: list[str]) -> CareerPick:
        return CareerPick(
            id=career.id, name=career.name, field=career.field, outlook=career.outlook,
            fit_reasons=reasons,
            prepare_now=career.prepare.get(stage.key, _GENERIC_PREPARE),
            key_subjects=career.key_subjects,
        )

    if neutral:
        by_id = {c.id: c for c in CAREERS}
        careers = [pick(by_id[i], ["대표 유망 분야 — 관심사를 고르면 적성 맞춤으로 추천돼요"]) for i in _DEFAULT_IDS]
        return CareersResponse(note="대표 유망 분야입니다. 관심 활동을 선택하면 적성에 맞춰 추천됩니다.", careers=careers)

    scored: list[tuple[float, CareerPick]] = []
    for c in CAREERS:
        score, dim = _fit(c, interest)
        if score <= 0:
            continue
        reasons = [f"{_DIM_LABEL.get(dim, dim)} 적성과 잘 맞아요"] if dim else []
        scored.append((score, pick(c, reasons)))
    scored.sort(key=lambda x: x[0], reverse=True)
    careers = [p for _, p in scored[:top_k]]
    if not careers:  # 안전망
        by_id = {c.id: c for c in CAREERS}
        careers = [pick(by_id[i], []) for i in _DEFAULT_IDS]
    return CareersResponse(note="적성 기반 유망 커리어 추천 (참고용).", careers=careers)
