"""샘플 상품 카탈로그.

MVP 용 인메모리 카탈로그. 운영 시 DB(카탈로그 서비스)로 대체한다.
각 상품은 적합 월령, 카테고리, 인기도(국민템 여부), 기질 친화도(affinity)를 가진다.

affinity: {기질차원: 가중치(-1~1)}
  - 양수: 해당 차원이 '높은' 아기에게 적합
  - 음수: 해당 차원이 '낮은' 아기에게 적합
  예) {"activity": +0.8} → 활동성 높은 아기에게 잘 맞음
      {"intensity": -0.8} → 반응강도 낮은(순한) 아기에게 잘 맞음(=예민한 아기에겐 자극↓ 제품)
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Product:
    item_id: str
    name: str
    category: str
    price: int
    min_months: int
    max_months: int
    popularity: float  # 0~1, 코호트 인기도
    national_pick: bool = False  # 국민템 여부
    play_category: str | None = None  # 발달 놀이/교구 카테고리(있으면)
    affinity: dict[str, float] = field(default_factory=dict)


CATALOG: list[Product] = [
    # --- 수유/수면 (0~6개월) ---
    Product("P001", "베이직 수유쿠션", "수유", 39000, 0, 6, 0.82, national_pick=True),
    Product("P002", "올인원 속싸개 3종", "수면", 29000, 0, 4, 0.78, national_pick=True,
            affinity={"intensity": -0.6}),
    Product("P003", "화이트노이즈 수면등", "수면", 45000, 0, 12, 0.7,
            affinity={"intensity": -0.8, "regularity": -0.4}),
    # --- 이앓이/촉감 (4~9개월) ---
    Product("P010", "실리콘 치발기 세트", "이앓이", 15000, 4, 12, 0.85, national_pick=True),
    Product("P011", "촉감 헝겊책", "이앓이", 18000, 4, 18, 0.66, play_category="촉감놀이",
            affinity={"mood": 0.3}),
    Product("P012", "사운드 딸랑이", "이앓이", 12000, 3, 9, 0.6, play_category="청각자극",
            affinity={"activity": 0.4}),
    # --- 이유식 (7~15개월) ---
    Product("P020", "이유식 마스터기", "이유식", 89000, 6, 18, 0.8, national_pick=True),
    Product("P021", "흡착 이유식 식판", "식기", 22000, 7, 36, 0.75, national_pick=True),
    Product("P022", "실리콘 턱받이", "식기", 9000, 6, 36, 0.7),
    # --- 보행/대근육 (9~18개월) ---
    Product("P030", "푸시워커(밀고 걷기)", "보행", 69000, 9, 18, 0.79, national_pick=True,
            play_category="대근육", affinity={"activity": 0.8}),
    Product("P031", "실내 미끄럼틀", "보행", 99000, 12, 48, 0.62, play_category="대근육",
            affinity={"activity": 0.9}),
    Product("P032", "논슬립 안전매트", "안전", 120000, 6, 36, 0.83, national_pick=True,
            affinity={"activity": 0.5}),
    # --- 소근육/창의 ---
    Product("P040", "원목 쌓기 블록", "학습", 35000, 10, 48, 0.74, play_category="소근육",
            affinity={"adaptability": 0.3}),
    Product("P041", "모양 맞추기 박스", "학습", 28000, 12, 36, 0.68, play_category="소근육",
            affinity={"adaptability": 0.4}),
    Product("P042", "역할놀이 주방세트", "학습", 79000, 24, 60, 0.6, play_category="역할놀이",
            affinity={"mood": 0.4, "adaptability": 0.3}),
    Product("P043", "대형 크레용 미술세트", "학습", 19000, 24, 60, 0.58, play_category="창의",
            affinity={"intensity": 0.3}),
    # --- 외출 ---
    Product("P050", "경량 휴대용 유모차", "외출", 320000, 6, 36, 0.77, national_pick=True),
    Product("P051", "아기띠(힙시트)", "외출", 110000, 3, 24, 0.8, national_pick=True,
            affinity={"adaptability": -0.4}),
    # --- 시각자극 (0~3개월) ---
    Product("P060", "흑백 초점책", "수면", 11000, 0, 3, 0.64, play_category="시각자극"),
    Product("P061", "모빌(오르골)", "수면", 42000, 0, 6, 0.69, play_category="시각자극",
            affinity={"intensity": -0.3}),
]


def products_for_age(age_months: int) -> list[Product]:
    return [p for p in CATALOG if p.min_months <= age_months <= p.max_months]
