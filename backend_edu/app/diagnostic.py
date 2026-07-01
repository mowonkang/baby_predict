"""미니 진단 문항 은행 (BKT 입력용).

자가체크(잘함/보통/부족)를 정·오답 기반 숙련 추정으로 정밀화하기 위한 소형 문항.
객관적으로 정답이 명확한 과목(수학·영어) 위주로 예시 문항을 둔다.
운영 시 교육과정 성취기준에 맞춰 문항을 확대·검수한다.
"""
from __future__ import annotations

from dataclasses import dataclass

from .grades import grade_for_age


@dataclass(frozen=True)
class Item:
    id: str
    subject: str
    band: str          # 초등/중등/고등
    difficulty: str    # 하/중/상
    question: str
    options: list[str]
    answer: int        # 정답 인덱스(0-based)
    unit: str = ""


ITEMS: list[Item] = [
    # ── 수학 초등 ──
    Item("m_e1", "수학", "초등", "하", "24 ÷ 6 = ?", ["3", "4", "5", "6"], 1, "나눗셈"),
    Item("m_e2", "수학", "초등", "중", "1/2 + 1/2 = ?", ["1/4", "1/2", "1", "2"], 2, "분수"),
    Item("m_e3", "수학", "초등", "중", "가로 4, 세로 3인 직사각형의 넓이는?", ["7", "10", "12", "14"], 2, "넓이"),
    # ── 수학 중등 ──
    Item("m_m1", "수학", "중등", "하", "x + 5 = 12일 때 x = ?", ["5", "6", "7", "8"], 2, "일차방정식"),
    Item("m_m2", "수학", "중등", "중", "(-3) + (-4) = ?", ["-1", "-7", "7", "1"], 1, "정수와 유리수"),
    Item("m_m3", "수학", "중등", "중", "2x = 10일 때 x = ?", ["2", "4", "5", "10"], 2, "일차방정식"),
    # ── 수학 고등 ──
    Item("m_h1", "수학", "고등", "중", "x² = 9의 양의 해는?", ["2", "3", "4", "9"], 1, "이차방정식"),
    Item("m_h2", "수학", "고등", "상", "d/dx (x²) = ?", ["x", "2x", "x²", "2"], 1, "미분"),
    Item("m_h3", "수학", "고등", "하", "2x + 1 = 7일 때 x = ?", ["2", "3", "4", "6"], 1, "방정식"),
    # ── 영어 초등 ──
    Item("e_e1", "영어", "초등", "하", "'apple'의 뜻은?", ["사과", "바나나", "포도", "딸기"], 0, "어휘"),
    Item("e_e2", "영어", "초등", "중", "'book'의 복수형은?", ["book", "books", "bookes", "booken"], 1, "문법"),
    # ── 영어 중등 ──
    Item("e_m1", "영어", "중등", "하", "'go'의 과거형은?", ["goed", "gone", "went", "going"], 2, "동사"),
    Item("e_m2", "영어", "중등", "중", "'beautiful'의 품사는?", ["명사", "동사", "형용사", "부사"], 2, "품사"),
    # ── 영어 고등 ──
    Item("e_h1", "영어", "고등", "중", "'increase'의 반의어는?", ["expand", "decrease", "raise", "grow"], 1, "어휘"),
    Item("e_h2", "영어", "고등", "중", "'happy'와 뜻이 비슷한 단어는?", ["sad", "glad", "angry", "tired"], 1, "어휘"),
]

_BY_ID = {it.id: it for it in ITEMS}


def band_for_age(age_years: int) -> str | None:
    level = grade_for_age(age_years).level
    return level if level in ("초등", "중등", "고등") else None


def items_for(age_years: int, subjects: list[str] | None = None) -> list[Item]:
    band = band_for_age(age_years)
    if band is None:
        return []
    out = [it for it in ITEMS if it.band == band]
    if subjects:
        out = [it for it in out if it.subject in subjects]
    return out


def grade_answer(item_id: str, choice: int) -> tuple[str, bool] | None:
    """(과목, 정답여부). 알 수 없는 문항이면 None."""
    it = _BY_ID.get(item_id)
    if it is None:
        return None
    return (it.subject, choice == it.answer)
