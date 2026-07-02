"""공신력 체계 레지스트리 — 우리가 어떤 권위 있는 평가·발달 체계를 어떻게 차용했는지.

투명성 원칙: 각 기능이 참고한 체계·주관기관·차용 방식·한계를 사용자에게 그대로 공개한다.
(검사 자체를 시행하는 것이 아니라 '구조'를 차용한 참고 도구임을 명시 — 표시광고법 리스크 회피)

상세 조사: docs/edu/평가체계_벤치마킹.md
"""
from __future__ import annotations

from .models import FrameworkRef

FRAMEWORKS: list[FrameworkRef] = [
    FrameworkRef(
        key="kwisc", name="K-WISC-V (한국 웩슬러 아동지능검사 5판)", authority="Pearson/인싸이트(임상 전문가 시행)",
        what="6~16세 인지능력 5지표: 언어이해·시공간·유동추론·작업기억·처리속도 (평균 100·SD 15)",
        how_used="인지 성향 5영역의 구조와 '또래 대비 백분위 밴드' 해석 프레임을 차용(관찰형 문항).",
        caveat="본 서비스는 IQ를 산출하지 않으며 임상 검사를 대체하지 않음."),
    FrameworkRef(
        key="kdst", name="K-DST (한국 영유아 발달선별검사)", authority="질병관리청·대한소아과학회(국가 영유아검진 공식 도구)",
        what="0~71개월 발달 6영역: 대근육·소근육·인지·언어·사회성·자조",
        how_used="영유아(0~7세) 모드의 발달 영역 구분과 월령별 가이드 프레임의 근거.",
        caveat="발달 지연 의심 시 반드시 영유아 건강검진·전문의 상담."),
    FrameworkRef(
        key="cbq", name="Rothbart CBQ (아동 기질 척도)", authority="Rothbart(한국판 타당화 논문 존재)",
        what="3~7세 기질 3요인: 외향성(Surgency)·부정정서·의도적 통제 — 양육자 관찰 보고",
        how_used="기질 프로파일의 3요인 구조 차용 + Thomas&Chess '조화의 적합성'으로 환경 가이드 생성.",
        caveat="자체 예시 문항 사용(원척도 아님). 기질은 좋고 나쁨이 없는 개성."),
    FrameworkRef(
        key="gardner", name="Gardner 다중지능 이론(MI)", authority="Howard Gardner(하버드)",
        what="언어·논리수학·공간·신체운동·음악·대인·자기이해·자연친화 8지능",
        how_used="8각 능력치 축의 다차원 구성 근거(언어·수리논리·탐구·예술·신체·사회성·리더십·창의와 정렬).",
        caveat="심리측정적 검증 논쟁이 있어 '강점 렌즈'로만 사용, 점수화 근거로는 비사용."),
    FrameworkRef(
        key="riasec", name="Holland RIASEC 직업흥미 6유형", authority="Holland(커리어넷·워크넷 공공검사와 동일 이론)",
        what="현실형·탐구형·예술형·사회형·진취형·관습형 흥미 구조",
        how_used="관심활동 선택 → 흥미 벡터 → 진로 계열·커리어 추천(기존 반영).",
        caveat="흥미는 변할 수 있으며 진로를 확정하지 않음."),
    FrameworkRef(
        key="dmgt", name="Gagné DMGT 2.0 (영재성·재능 분화 모형)", authority="Françoys Gagné(영재교육 최다 인용 모형)",
        what="타고난 능력(gifts) → [개발 과정: 활동·투자·진전 + 개인내적/환경적 촉매] → 재능(talents)",
        how_used="테크트리 티어를 재능발달 단계로 라벨링, 예상 능력치의 '투자·촉매' 시나리오 논리.",
        caveat="상위 10% 기준의 학술 모형 — 모든 아이의 발달 서사에 참고로만 적용."),
    FrameworkRef(
        key="bloom", name="Bloom 재능발달 3단계", authority="Benjamin Bloom, 『Developing Talent in Young People』",
        what="초기(놀이·흥미) → 중기(체계적 기술 습득) → 후기(전문화) — 세계적 성취자 종단 연구",
        how_used="테크트리 tier 0~1(탐색·흥미), tier 2(기술 습득), tier 3(전문화) 단계 라벨의 근거.",
        caveat=""),
    FrameworkRef(
        key="cefr", name="CEFR (유럽공통 언어참조기준)", authority="유럽평의회(국제 표준)",
        what="언어 능력 6단계: A1·A2(기초) → B1·B2(자립) → C1·C2(숙달)",
        how_used="어학 트랙의 공인 등급 목표(단계별 A1→B1→B2+)로 사용.",
        caveat=""),
    FrameworkRef(
        key="certs", name="국내 공인 급수 체계", authority="국기원(태권도 품·단), 한국어문회(한자급수), 대한수영연맹(수영 급수), KMO/KOI(올림피아드), ABRSM(음악 등급)",
        what="분야별 공인 등급·급수 — 실존하는 '테크트리'",
        how_used="테크트리 각 단계에 공인 등급 목표를 부착해 진행도를 객관적 지표로 측정.",
        caveat="등급 취득이 교육의 목적 자체는 아님 — 동기·이정표로 활용."),
    FrameworkRef(
        key="growth", name="성장도표(백분위 트래킹) 개념", authority="WHO·질병관리청 소아 성장도표(신체 발육 표준)",
        what="같은 나이 집단 내 백분위 곡선을 따라 성장 경과를 추적하는 표준 방법",
        how_used="예상 능력치 전망을 '백분위 밴드 유지 + 투자에 따른 이동'으로 표현하는 프레임.",
        caveat="신체 성장과 달리 능력 발달의 개인 예측은 과학적으로 미검증 — 참고 전망으로만 제시."),
]


def all_frameworks() -> list[FrameworkRef]:
    return list(FRAMEWORKS)


# 8각 능력치 축 ↔ Gardner 다중지능 배지(프론트 표시용)
STAT_MI_BADGE: dict[str, str] = {
    "language": "MI 언어지능",
    "logic": "MI 논리수학지능",
    "science": "MI 자연친화·논리수학",
    "art": "MI 음악·공간지능",
    "physical": "MI 신체운동지능",
    "social": "MI 대인지능",
    "leadership": "MI 대인·자기이해",
    "creativity": "MI 공간·창의",
}
