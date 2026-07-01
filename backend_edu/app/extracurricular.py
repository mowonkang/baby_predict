"""사교육·활동 선택지 정의 (능력치·테크트리 공용 입력 소스).

'몬테소리·영어·태권도·발레·미술·한자·음악…' 등 유년기부터의 다양한 사교육을
**계열(어학·사고력·예술·체육·기초인성)**로 정리한 선택지. 쉬운 입력을 위해
사용자는 '경험했거나 관심 있는 것'을 탭으로 고르기만 하면 된다(리커트 X).

각 옵션은 어떤 능력치(stats.STAT_AXES key)에 얼마나 기여하는지 가중치를 갖는다.
근거·설계: docs/edu/육성엔진_설계.md
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Extracurricular:
    id: str
    label: str
    category: str                 # 어학 / 사고력 / 예술 / 체육 / 기초·인성
    # 능력치 key → 기여 가중치(대략 0.4~1.0). stats.STAT_AXES 참고
    stat_weights: dict[str, float] = field(default_factory=dict)


# 계열별 대표 사교육/활동 — 유아기부터 흔한 종목 중심(예시 카탈로그)
EXTRACURRICULARS: list[Extracurricular] = [
    # 어학
    Extracurricular("ex_eng", "🔤 영어(회화·파닉스)", "어학", {"language": 1.0, "social": 0.3}),
    Extracurricular("ex_hanja", "🀄 한자·중국어", "어학", {"language": 0.8, "logic": 0.3}),
    Extracurricular("ex_read", "📚 독서·논술", "어학", {"language": 0.9, "creativity": 0.5}),
    Extracurricular("ex_speech", "🎤 웅변·스피치·토론", "어학", {"language": 0.7, "leadership": 0.8, "social": 0.5}),
    # 사고력
    Extracurricular("ex_monte", "🧩 몬테소리·오감놀이", "사고력", {"creativity": 0.9, "science": 0.6}),
    Extracurricular("ex_thinkmath", "🧮 사고력수학·교구수학", "사고력", {"logic": 1.0, "science": 0.5}),
    Extracurricular("ex_coding", "💻 코딩·로봇", "사고력", {"logic": 0.9, "creativity": 0.6, "science": 0.6}),
    Extracurricular("ex_baduk", "⚫ 바둑·체스·보드게임", "사고력", {"logic": 0.8, "creativity": 0.4}),
    Extracurricular("ex_science", "🔬 과학실험·창의과학", "사고력", {"science": 1.0, "creativity": 0.5}),
    # 예술
    Extracurricular("ex_music", "🎹 피아노·음악", "예술", {"art": 1.0, "creativity": 0.6}),
    Extracurricular("ex_paint", "🎨 미술·그리기", "예술", {"art": 1.0, "creativity": 0.7}),
    Extracurricular("ex_ballet", "🩰 발레·무용", "예술", {"art": 0.7, "physical": 0.8}),
    # 체육
    Extracurricular("ex_taekwondo", "🥋 태권도·무술", "체육", {"physical": 1.0, "leadership": 0.4}),
    Extracurricular("ex_swim", "🏊 수영", "체육", {"physical": 1.0}),
    Extracurricular("ex_ball", "⚽ 축구·구기 운동", "체육", {"physical": 0.9, "social": 0.6, "leadership": 0.4}),
    # 기초·인성
    Extracurricular("ex_group", "🤝 협동·단체활동(그룹수업)", "기초·인성", {"social": 1.0, "leadership": 0.5}),
    Extracurricular("ex_leader", "🧭 리더십·기획 캠프", "기초·인성", {"leadership": 1.0, "social": 0.5}),
]

CATEGORIES: tuple[str, ...] = ("어학", "사고력", "예술", "체육", "기초·인성")

_BY_ID = {e.id: e for e in EXTRACURRICULARS}


def get(option_id: str) -> Extracurricular | None:
    return _BY_ID.get(option_id)
