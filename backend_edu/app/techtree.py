"""사교육 테크트리 + 추천 루트 엔진 (스타크래프트식 테크 진행).

유아기부터 진로까지 '어떤 사교육을 어떤 순서로' 밟는지를 계열별 트리로 정리하고,
능력치(stats)·나이·관심을 규칙으로 매칭해 **다음에 탈 루트**를 추천한다.
LLM 호출 없음(무과금). 노드·비용대는 예시이며 실제 학원/브랜드가 아니다.

설계: docs/edu/육성엔진_설계.md §3
"""
from __future__ import annotations

from dataclasses import dataclass

from .models import StudentProfile, TechNode, TechTrack, TechTreeResponse
from .stats import build_stats


@dataclass(frozen=True)
class _Node:
    id: str
    label: str
    tier: int
    age_hint: str
    stat: str
    requires: tuple[str, ...] = ()
    cost_band: str = "중"
    free_alt: str = ""


@dataclass(frozen=True)
class _Track:
    key: str
    label: str
    stat: str
    nodes: tuple[_Node, ...]


# tier: 0=유아(5~7), 1=초등(8~12), 2=중등(13~15), 3=고등·진로(16~19)
_TIER_AGE = {0: "5~7세", 1: "8~12세", 2: "13~15세", 3: "16~19세"}

TRACKS: tuple[_Track, ...] = (
    _Track("lang", "어학", "language", (
        _Node("lang0", "영어 노출·파닉스 놀이", 0, _TIER_AGE[0], "language",
              cost_band="저", free_alt="EBSe 유아영어·유튜브 영어동요"),
        _Node("lang1", "영어 회화·리딩", 1, _TIER_AGE[1], "language", ("lang0",),
              cost_band="중", free_alt="EBSe 초등·칸아카데미 리딩"),
        _Node("lang2", "영문법·독해 심화", 2, _TIER_AGE[2], "language", ("lang1",),
              cost_band="중", free_alt="EBS중학 영어"),
        _Node("lang3", "수능영어·공인시험(토플 등)", 3, _TIER_AGE[3], "language", ("lang2",),
              cost_band="고", free_alt="EBSi 수능영어"),
    )),
    _Track("think", "사고력·수리", "logic", (
        _Node("think0", "교구·오감 사고력 놀이(몬테소리 등)", 0, _TIER_AGE[0], "logic",
              cost_band="중", free_alt="집짓기·퍼즐·보드게임"),
        _Node("think1", "사고력수학·코딩 입문", 1, _TIER_AGE[1], "logic", ("think0",),
              cost_band="중", free_alt="똑똑수학탐험대·엔트리 코딩"),
        _Node("think2", "수학 심화·경시/정보올림피아드", 2, _TIER_AGE[2], "logic", ("think1",),
              cost_band="고", free_alt="EBS중학 수학·백준"),
        _Node("think3", "고등수학·심화탐구(수리논술)", 3, _TIER_AGE[3], "logic", ("think2",),
              cost_band="고", free_alt="EBSi 수학·MATH"),
    )),
    _Track("sci", "탐구·과학", "science", (
        _Node("sci0", "자연관찰·과학놀이", 0, _TIER_AGE[0], "science",
              cost_band="저", free_alt="국립과학관·유튜브 과학실험"),
        _Node("sci1", "창의과학실험·로봇", 1, _TIER_AGE[1], "science", ("sci0",),
              cost_band="중", free_alt="지역 과학관 교실·EBS 과학"),
        _Node("sci2", "과학 심화·영재원/발명", 2, _TIER_AGE[2], "science", ("sci1",),
              cost_band="고", free_alt="사이버영재교육·EBS중학 과학"),
        _Node("sci3", "이과 심화(물화생지)·탐구활동", 3, _TIER_AGE[3], "science", ("sci2",),
              cost_band="고", free_alt="EBSi 과학탐구"),
    )),
    _Track("art", "예술", "art", (
        _Node("art0", "음악·미술 놀이", 0, _TIER_AGE[0], "art",
              cost_band="저", free_alt="문화센터·유튜브 미술놀이"),
        _Node("art1", "피아노·미술 정규 레슨", 1, _TIER_AGE[1], "art", ("art0",),
              cost_band="중", free_alt="지역 문화센터 저가 강좌"),
        _Node("art2", "전공 심화 레슨(입시 기초)", 2, _TIER_AGE[2], "art", ("art1",),
              cost_band="고", free_alt="시립 예술교육·온라인 클래스"),
        _Node("art3", "예중·예고·입시(실기)", 3, _TIER_AGE[3], "art", ("art2",),
              cost_band="고", free_alt="입시 요강·기출 실기"),
    )),
    _Track("phys", "체육", "physical", (
        _Node("phys0", "신체놀이·기초 운동", 0, _TIER_AGE[0], "physical",
              cost_band="저", free_alt="놀이터·공원 활동"),
        _Node("phys1", "태권도·수영 등 종목", 1, _TIER_AGE[1], "physical", ("phys0",),
              cost_band="중", free_alt="공공 체육시설 강습"),
        _Node("phys2", "구기·전문 종목 심화", 2, _TIER_AGE[2], "physical", ("phys1",),
              cost_band="중", free_alt="학교 스포츠클럽"),
        _Node("phys3", "체대 입시·선수 트랙", 3, _TIER_AGE[3], "physical", ("phys2",),
              cost_band="고", free_alt="체대입시 요강·기록회"),
    )),
    _Track("human", "인성·리더십·표현", "social", (
        _Node("human0", "협동·그룹 놀이", 0, _TIER_AGE[0], "social",
              cost_band="저", free_alt="도서관·공동육아 모임"),
        _Node("human1", "독서·논술·스피치", 1, _TIER_AGE[1], "language", ("human0",),
              cost_band="중", free_alt="도서관 독서프로그램"),
        _Node("human2", "토론·리더십·동아리", 2, _TIER_AGE[2], "leadership", ("human1",),
              cost_band="저", free_alt="학교 자율동아리·학생회"),
        _Node("human3", "진로 탐색·대외활동·봉사", 3, _TIER_AGE[3], "leadership", ("human2",),
              cost_band="저", free_alt="커리어넷·지역 청소년센터"),
    )),
)

# 능력치 stat → 대표 트랙 key (추천 매칭용)
_STAT_TRACK: dict[str, str] = {
    "language": "lang",
    "logic": "think",
    "creativity": "think",
    "science": "sci",
    "art": "art",
    "physical": "phys",
    "social": "human",
    "leadership": "human",
}


def _current_tier(age: int) -> int:
    if age < 8:
        return 0
    if age < 14:
        return 1
    if age < 17:
        return 2
    return 3


def _to_node(n: _Node, *, recommended: bool = False, reason: str = "") -> TechNode:
    return TechNode(
        id=n.id, label=n.label, tier=n.tier, age_hint=n.age_hint, stat=n.stat,
        requires=list(n.requires), cost_band=n.cost_band, free_alt=n.free_alt,
        recommended=recommended, reason=reason,
    )


def build_techtree(profile: StudentProfile) -> TechTreeResponse:
    """능력치·나이 기반 사교육 테크트리 + 추천 루트."""
    stat = build_stats(profile)
    tier = _current_tier(profile.age_years)

    # 강점 능력치 → 추천 트랙 key (상위 축 순서, 중복 제거)
    rec_track_keys: list[str] = []
    for label in stat.top_axes:
        # top_axes 는 라벨이므로 stat key 로 역매핑
        for k, lb in ((a.key, a.label) for a in stat.axes):
            if lb == label:
                tk = _STAT_TRACK.get(k)
                if tk and tk not in rec_track_keys:
                    rec_track_keys.append(tk)
    # 콜드스타트: 강점이 없으면 기초·인성 + 사고력을 기본 추천
    if not rec_track_keys:
        rec_track_keys = ["human", "think"]

    tracks_out: list[TechTrack] = []
    route: list[TechNode] = []
    for tr in TRACKS:
        is_rec_track = tr.key in rec_track_keys
        nodes_out: list[TechNode] = []
        for n in tr.nodes:
            # 추천 루트: 추천 트랙이고, 현재 tier(지금 할 것) 또는 다음 tier(다음 목표)
            on_route = is_rec_track and n.tier in (tier, tier + 1)
            reason = ""
            if on_route:
                reason = ("지금 시기에 강점을 살릴 핵심 단계"
                          if n.tier == tier else "다음 단계 목표(미리 준비)")
            node = _to_node(n, recommended=on_route, reason=reason)
            nodes_out.append(node)
            if on_route:
                route.append(node)
        tracks_out.append(TechTrack(
            key=tr.key, label=tr.label, stat=tr.stat,
            nodes=nodes_out, recommended=is_rec_track))

    route.sort(key=lambda n: (n.tier, n.id))
    rec_labels = [tr.label for tr in TRACKS if tr.key in rec_track_keys]

    return TechTreeResponse(
        stat=stat, tracks=tracks_out, route=route,
        recommended_tracks=rec_labels,
    )
