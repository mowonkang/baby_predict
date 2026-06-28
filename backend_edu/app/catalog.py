"""교육 리소스 샘플 카탈로그.

MVP 용 인메모리 카탈로그. 운영 시 카탈로그 서비스(DB) + 업체 입점으로 대체.
각 리소스는 적합 학령, 교과 영역, 인기도(국민 커리큘럼), 흥미 친화도(affinity)를 가진다.

affinity: {RIASEC차원: 가중치(-1~1)}
  - 양수: 해당 흥미가 '높은' 학생에게 적합
  예) {"investigative": +0.8} → 탐구형 학생에게 잘 맞음
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Resource:
    resource_id: str
    name: str
    area: str            # 교과/영역
    resource_type: str   # 인강 / 교재 / 학원 / 활동 / 진로
    cost: int            # 월/회 비용(원). 0 = 무료
    min_age: int
    max_age: int
    popularity: float    # 0~1, 코호트 인기도
    national_pick: bool = False  # 인기(국민) 커리큘럼 여부
    affinity: dict[str, float] = field(default_factory=dict)


CATALOG: list[Resource] = [
    # --- 미취학 ---
    Resource("R001", "한글 떼기 놀이 프로그램", "한글", "활동", 0, 3, 7, 0.8, national_pick=True),
    Resource("R002", "수 개념 보드게임 키트", "기초수", "교재", 35000, 4, 8, 0.7,
             affinity={"investigative": 0.4, "conventional": 0.3}),
    Resource("R003", "유아 미술·음악 체험", "예체능", "활동", 90000, 4, 8, 0.66,
             affinity={"artistic": 0.8}),
    # --- 초등 ---
    Resource("R010", "초등 독서·논술 프로그램", "국어", "학원", 150000, 7, 12, 0.84, national_pick=True,
             affinity={"social": 0.3, "artistic": 0.3}),
    Resource("R011", "초등 사고력 수학", "수학", "학원", 180000, 8, 12, 0.86, national_pick=True,
             affinity={"investigative": 0.6, "conventional": 0.3}),
    Resource("R012", "초등 코딩·로봇 교실", "과학", "학원", 160000, 9, 13, 0.72,
             affinity={"realistic": 0.7, "investigative": 0.6}),
    Resource("R013", "초등 영어 화상 회화", "영어", "인강", 99000, 8, 13, 0.78, national_pick=True,
             affinity={"social": 0.4}),
    Resource("R014", "과학 실험 탐구 키트(구독)", "과학", "교재", 39000, 9, 14, 0.64,
             affinity={"investigative": 0.8, "realistic": 0.4}),
    Resource("R015", "어린이 토론·리더십 클럽", "사회", "활동", 70000, 10, 14, 0.6,
             affinity={"enterprising": 0.7, "social": 0.5}),
    # --- 중등 ---
    Resource("R020", "중등 수학 심화 인강", "수학", "인강", 120000, 13, 16, 0.85, national_pick=True,
             affinity={"investigative": 0.6, "conventional": 0.3}),
    Resource("R021", "중등 과학 탐구 실험 강좌", "과학", "학원", 200000, 13, 16, 0.7,
             affinity={"investigative": 0.8, "realistic": 0.5}),
    Resource("R022", "중등 국어·문학 독해", "국어", "인강", 80000, 13, 16, 0.74, national_pick=True),
    Resource("R023", "예술중·예고 대비 실기", "예체능", "학원", 350000, 13, 18, 0.55,
             affinity={"artistic": 0.9}),
    Resource("R024", "청소년 창업·경제 캠프", "사회", "활동", 250000, 14, 18, 0.5,
             affinity={"enterprising": 0.8, "social": 0.3}),
    Resource("R025", "코딩 경진대회 대비반", "과학", "학원", 220000, 13, 18, 0.58,
             affinity={"realistic": 0.6, "investigative": 0.7}),
    # --- 고등 ---
    Resource("R030", "고등 수학 1:1 관리형", "수학", "학원", 400000, 16, 19, 0.83, national_pick=True,
             affinity={"investigative": 0.5, "conventional": 0.4}),
    Resource("R031", "수능 국어 인강 패키지", "국어", "인강", 130000, 16, 19, 0.88, national_pick=True),
    Resource("R032", "이과 과학탐구(물·화·생·지) 인강", "탐구", "인강", 150000, 16, 19, 0.76,
             affinity={"investigative": 0.7, "realistic": 0.4}),
    Resource("R033", "사회탐구 + 논술 대비", "탐구", "인강", 140000, 16, 19, 0.7,
             affinity={"social": 0.5, "enterprising": 0.4, "conventional": 0.3}),
    Resource("R034", "미대·디자인 입시 포트폴리오", "예체능", "학원", 500000, 16, 19, 0.52,
             affinity={"artistic": 0.9}),
    Resource("R035", "R&E 연구·세특 멘토링", "진로", "활동", 300000, 16, 19, 0.6,
             affinity={"investigative": 0.6}),
    # --- 대학/진로 공통 ---
    Resource("R040", "진로·전공 적성 컨설팅", "진로", "진로", 200000, 11, 22, 0.62, national_pick=True),
]


def resources_for_age(age_years: int) -> list[Resource]:
    return [r for r in CATALOG if r.min_age <= age_years <= r.max_age]
