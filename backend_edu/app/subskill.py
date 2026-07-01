"""성취도 하위 스킬 상세 + 또래 대비 밴드 (무과금·규칙 기반).

기존 성취도는 과목 단위 잘함/보통/부족뿐이라 '무엇이' 부족한지 알 수 없었다.
과목을 하위 스킬(예: 수학=연산·개념·응용)로 쪼개 각각을 평가하고,
**또래 평균 대비 밴드/백분위**로 무엇이 부족·양호한지 구체화한다.

밴드 프레이밍은 참고용(정규분포 가정)이며 표준화 규준 검사가 아니다.
"""
from __future__ import annotations

from dataclasses import dataclass

from .models import SubskillDetail, SubskillItem


@dataclass(frozen=True)
class _Sub:
    subject: str
    name: str
    desc: str          # 무엇을 보는지
    weak_what: str     # 부족할 때 무엇이 약한지
    weak_how: str      # 어떻게 보완
    strong_how: str    # 잘할 때 어떻게 심화


# 과목 × 하위 스킬 카탈로그(인문계 공통 핵심 과목 중심)
SUBS: list[_Sub] = [
    _Sub("수학", "연산", "사칙연산의 정확도와 속도",
         "계산 실수가 잦거나 느려 시간이 부족", "매일 10분 연산 루틴(똑똑수학탐험대·연산앱)으로 자동화",
         "시간 단축·암산으로 넘어가고 사고력 문제에 시간 배분"),
    _Sub("수학", "개념", "원리·정의의 이해",
         "공식은 외웠지만 왜 그런지 설명을 못함", "개념을 말로 설명·오답노트로 원리 재구성(EBS 개념강의)",
         "개념을 남에게 설명·다른 단원과 연결"),
    _Sub("수학", "응용", "문장제·사고력·문제해결",
         "조건이 복잡한 문장제에서 식 세우기를 어려워함", "문제를 그림·표로 옮기고 조건→식 단계 훈련",
         "심화·경시 유형과 서술형으로 확장"),
    _Sub("국어", "읽기이해", "글의 내용·구조 파악",
         "긴 글에서 요지·근거를 잘 못 찾음", "문단 요약·핵심어 표시로 구조 읽기(EBS·독서프로그램)",
         "비문학 지문·주제 통합 독해로 확장"),
    _Sub("국어", "어휘", "낱말·관용표현의 폭",
         "모르는 낱말이 많아 이해가 끊김", "어휘노트·문맥추론으로 매일 소량 누적",
         "한자어·개념어로 학습어휘 확장"),
    _Sub("국어", "쓰기표현", "문장·글로 표현",
         "생각은 있으나 문장으로 정리가 안 됨", "한 문단 쓰기·고쳐쓰기 루틴으로 구조화",
         "논술·서술형·글쓰기 대회로 확장"),
    _Sub("영어", "듣기", "듣고 이해",
         "말의 속도를 못 따라가고 놓침", "짧은 영상·받아쓰기로 귀 트기(EBSe)",
         "원어민 속도 콘텐츠·섀도잉으로 확장"),
    _Sub("영어", "읽기어휘", "독해·단어",
         "단어가 부족해 문장 해석이 막힘", "빈출 단어·짧은 리딩 누적(칸아카데미 리딩)",
         "원서·긴 지문 독해로 확장"),
    _Sub("영어", "문법쓰기", "문법·영작",
         "문장 구조·시제에서 오류가 잦음", "핵심 문법 1개씩·짧은 영작 교정",
         "에세이·자유 영작으로 확장"),
    _Sub("과학", "개념이해", "과학 개념·용어",
         "용어·원리를 피상적으로만 앎", "개념을 실생활 예로 연결·EBS 개념강의",
         "단원 간 개념 통합·심화"),
    _Sub("과학", "탐구실험", "관찰·실험·자료해석",
         "실험 절차·결과 해석을 어려워함", "과학관·가정실험·유튜브 실험으로 절차 체득",
         "자유탐구·발명·영재원 활동으로 확장"),
    _Sub("사회", "개념암기", "개념·용어·사실",
         "용어와 흐름을 헷갈려 함", "마인드맵·타임라인으로 구조 암기",
         "개념 간 인과 연결로 심화"),
    _Sub("사회", "자료해석", "도표·자료 읽기",
         "지도·그래프에서 정보를 잘 못 뽑음", "자료 1개씩 읽고 요약하는 연습",
         "비교·추론형 자료 문제로 확장"),
]
_BY_ID = {f"{s.subject}:{s.name}": s for s in SUBS}


def options() -> list[SubskillItem]:
    return [SubskillItem(id=f"{s.subject}:{s.name}", subject=s.subject, name=s.name, desc=s.desc)
            for s in SUBS]


def subjects() -> list[str]:
    out: list[str] = []
    for s in SUBS:
        if s.subject not in out:
            out.append(s.subject)
    return out


_LEVEL = {"부족": "부족", "하": "부족", "보통": "보통", "중": "보통", "잘함": "잘함", "상": "잘함"}
# 또래 대비 밴드 + 대략 백분위(참고)
_BAND = {
    "부족": ("또래 평균 대비 하위(보완 필요)", 25),
    "보통": ("또래 평균 수준", 50),
    "잘함": ("또래 평균 대비 상위(우수)", 80),
}


def build_subskill_detail(subskills: dict[str, str]) -> list[SubskillDetail]:
    """하위스킬 응답(id→수준) → 또래 대비 상세."""
    out: list[SubskillDetail] = []
    for sid, raw in (subskills or {}).items():
        s = _BY_ID.get(sid)
        if s is None:
            continue
        lvl = _LEVEL.get(str(raw).strip())
        if lvl is None:
            continue
        band, pct = _BAND[lvl]
        weak = lvl == "부족"
        what = s.weak_what if weak else (s.desc + " — 양호")
        how = s.weak_how if lvl != "잘함" else s.strong_how
        out.append(SubskillDetail(
            id=sid, subject=s.subject, name=s.name, level=lvl,
            peer_band=band, percentile=pct, what=what, how=how, weak=weak))
    # 부족 먼저
    out.sort(key=lambda d: (not d.weak, d.subject))
    return out
