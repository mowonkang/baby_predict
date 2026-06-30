"""학원/사교육 추천 + 평점·리뷰.

무료강의(자기학습)와 함께 '필요한 사교육' 정보를 제공한다.
- 지역·과목(약점 우선)·학년으로 학원을 추천
- **입점(스폰서) 학원은 별도 표기**해 수익화(입점료·광고)와 신뢰를 양립
- 평점·리뷰(학원/선생님/강의)를 읽고 작성(서버 저장)

⚠️ 본 카탈로그·리뷰는 **가상의 예시 데이터**다(실제 업체 아님). 운영 시 입점사 실데이터로 대체.
수익화·신뢰 정책: docs/edu/기획안.md §5, §4.3
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from .grades import grade_for_age
from .models import AcademiesResponse, AcademyPick, Review, ReviewsResponse

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_REVIEW_FILE = _DATA_DIR / "reviews.json"


@dataclass(frozen=True)
class Academy:
    id: str
    name: str
    type: str           # 학원/인강/공부방
    subjects: tuple[str, ...]
    region: str
    online: bool
    min_age: int
    max_age: int
    price: int          # 월(원)
    sponsored: bool
    base_rating: float
    base_reviews: int
    url: str = ""


# 가상의 예시 학원 (실제 업체 아님)
ACADEMIES: list[Academy] = [
    Academy("A001", "수리탐구 수학학원(예시)", "학원", ("수학",), "서울 강남", False, 9, 16, 250000, True, 4.6, 38),
    Academy("A002", "또박또박 국어논술(예시)", "학원", ("국어",), "서울 강남", False, 8, 15, 180000, False, 4.4, 21),
    Academy("A003", "글로벌 영어센터(예시)", "학원", ("영어",), "서울 노원", False, 8, 16, 200000, True, 4.3, 30),
    Academy("A004", "개념과학 실험학원(예시)", "학원", ("과학",), "경기 분당", False, 11, 16, 220000, False, 4.5, 17),
    Academy("A005", "탄탄수학 공부방(예시)", "공부방", ("수학",), "경기 분당", False, 9, 14, 120000, False, 4.2, 12),
    Academy("A006", "메가스터디형 인강(예시)", "인강", ("국어", "영어", "수학", "탐구"), "온라인", True, 14, 19, 110000, True, 4.4, 120),
    Academy("A007", "EBS 연계 자기주도(예시)", "인강", ("국어", "영어", "수학"), "온라인", True, 12, 19, 40000, False, 4.1, 64),
    Academy("A008", "영재수학 사고력(예시)", "학원", ("수학",), "부산 해운대", False, 9, 13, 200000, False, 4.3, 15),
    Academy("A009", "입시전략 컨설팅(예시)", "학원", ("진로", "국어"), "서울 강남", True, 16, 19, 300000, True, 4.0, 9),
    Academy("A010", "함께크는 영어공부방(예시)", "공부방", ("영어",), "대전 유성", False, 8, 14, 130000, False, 4.6, 22),
    Academy("A011", "통합사회·역사 논술(예시)", "학원", ("사회", "국어"), "서울 노원", False, 13, 18, 170000, False, 4.2, 11),
    Academy("A012", "코딩·AI 융합학원(예시)", "학원", ("과학",), "경기 분당", True, 10, 18, 230000, True, 4.5, 26),
]
_BY_ID = {a.id: a for a in ACADEMIES}

# 가상의 예시 리뷰 (학원/선생님/강의)
SAMPLE_REVIEWS: dict[str, list[Review]] = {
    "A001": [Review(target_type="선생님", target_name="김민수 원장", rating=5, text="개념을 끝까지 이해시켜 주세요. 질문 받아주는 게 좋아요.", date="2026-03"),
             Review(target_type="강의", target_name="중등 심화반", rating=4, text="숙제가 많지만 실력은 확실히 늘어요.", date="2026-02")],
    "A003": [Review(target_type="선생님", target_name="Anna 쌤", rating=4, text="회화 위주라 아이가 영어를 좋아하게 됐어요.", date="2026-04")],
    "A006": [Review(target_type="강의", target_name="수능 국어 패키지", rating=4, text="인강이라 시간 활용 좋고 가성비 좋아요.", date="2026-01"),
             Review(target_type="강의", target_name="수학 개념완성", rating=5, text="개념 설명이 깔끔합니다.", date="2026-02")],
    "A010": [Review(target_type="선생님", target_name="박지영 선생님", rating=5, text="소수 정예라 꼼꼼히 봐주세요.", date="2026-03")],
}


# ── 리뷰 영속화(서버 저장) ──────────────────────────────
def _load_stored() -> dict:
    try:
        return json.loads(_REVIEW_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_stored(data: dict) -> None:
    _DATA_DIR.mkdir(exist_ok=True)
    _REVIEW_FILE.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def _all_reviews(academy_id: str) -> list[Review]:
    out = list(SAMPLE_REVIEWS.get(academy_id, []))
    for r in _load_stored().get(academy_id, []):
        out.append(Review(**r))
    return out


def _agg(academy_id: str) -> tuple[float, int]:
    """현재 평점·리뷰 수(샘플 + 작성)."""
    a = _BY_ID[academy_id]
    revs = _all_reviews(academy_id)
    total = a.base_rating * a.base_reviews + sum(r.rating for r in revs)
    count = a.base_reviews + len(revs)
    return (round(total / count, 2) if count else 0.0, count)


def get_reviews(academy_id: str) -> ReviewsResponse | None:
    a = _BY_ID.get(academy_id)
    if not a:
        return None
    avg, count = _agg(academy_id)
    revs = sorted(_all_reviews(academy_id), key=lambda r: r.date, reverse=True)
    return ReviewsResponse(academy_id=a.id, academy_name=a.name, avg_rating=avg, count=count, reviews=revs)


def submit_review(academy_id: str, rating: int, text: str, target_type: str, target_name: str) -> bool:
    if academy_id not in _BY_ID:
        return False
    data = _load_stored()
    data.setdefault(academy_id, []).append(
        {"target_type": target_type or "학원", "target_name": target_name or _BY_ID[academy_id].name,
         "rating": rating, "text": text, "date": "2026-06"})
    _save_stored(data)
    return True


# ── 추천 ────────────────────────────────────────────────
def _pick(a: Academy, reasons: list[str]) -> AcademyPick:
    rating, count = _agg(a.id)
    return AcademyPick(
        id=a.id, name=a.name, type=a.type, subjects=list(a.subjects), region=a.region,
        price=a.price, rating=rating, review_count=count, sponsored=a.sponsored,
        reasons=reasons, url=a.url)


def recommend_academies(age_years: int, region: str | None, weak_subjects: list[str],
                        budget: int | None, top_k: int = 5) -> AcademiesResponse:
    grade = grade_for_age(age_years)
    region = (region or "").strip()
    weak = set(weak_subjects or [])

    def reasons_for(a: Academy) -> list[str]:
        rs: list[str] = []
        if weak & set(a.subjects):
            rs.append(f"보완 필요 과목({', '.join(weak & set(a.subjects))}) 전문")
        if a.online:
            rs.append("온라인 — 지역 무관, 시간 자유")
        elif region and region in a.region:
            rs.append(f"우리 동네({a.region}) 학원")
        rt, _ = _agg(a.id)
        rs.append(f"평점 {rt}/5")
        return rs

    cands: list[Academy] = []
    for a in ACADEMIES:
        if not (a.min_age <= age_years <= a.max_age):
            continue
        if budget is not None and a.price > budget:
            continue
        if region and not (a.online or region in a.region):
            continue
        if weak and not (weak & set(a.subjects)):
            continue
        cands.append(a)

    # 약점 과목 미입력 시: 지역/온라인 기준만
    if not cands and not weak:
        cands = [a for a in ACADEMIES if a.min_age <= age_years <= a.max_age
                 and (not region or a.online or region in a.region)
                 and (budget is None or a.price <= budget)]

    sponsored = [a for a in cands if a.sponsored]
    organic = [a for a in cands if not a.sponsored]
    keyf = lambda a: (len(weak & set(a.subjects)), _agg(a.id)[0])
    sponsored.sort(key=keyf, reverse=True)
    organic.sort(key=keyf, reverse=True)

    note = "‘입점’은 광고(스폰서) 학원이며 추천 점수와 별개입니다. 무료강의로 먼저 시도하고, 필요할 때 비교하세요."
    if not cands:
        note = "조건에 맞는 예시 학원이 없어요. 지역/예산을 조정하거나 무료강의를 활용해 보세요."
    return AcademiesResponse(
        region=region or "전체", weak_subjects=list(weak), note=note,
        sponsored=[_pick(a, ["입점(광고) 학원"] + reasons_for(a)) for a in sponsored[:2]],
        organic=[_pick(a, reasons_for(a)) for a in organic[:top_k]],
    )
