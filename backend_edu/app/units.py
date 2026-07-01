"""학년별 단원 + 단원별 무료강의 링크.

'이번 학년 단원'을 보여주고, 막히면 바로 볼 무료 강의로 연결한다.
- 초등 수학: 칸아카데미 한국어(학년·학기별 무료, 한국 교육과정 정렬)
- 중등 수학·기타 교과: EBS(초등/중학)·EBSe(영어)
단원명은 2022 개정 교육과정 기준(근거: docs/edu/교육과정_커리큘럼.md).
"""
from __future__ import annotations

from .grades import grade_for_age
from .models import Unit, UnitsResponse

# 초등 학년 → 칸아카데미 한국어 수학(학기1 페이지)
_KHAN = {
    "e1": "https://ko.khanacademy.org/math/kor-1st-1",
    "e2": "https://ko.khanacademy.org/math/kor-2nd-1",
    "e3": "https://ko.khanacademy.org/math/kor-3rd-1",
    "e4": "https://ko.khanacademy.org/math/kor-4th-1",
    "e5": "https://ko.khanacademy.org/math/kor-5th-1",
    "e6": "https://ko.khanacademy.org/math/kor-6th-1",
}
_EBS_P = "https://primary.ebs.co.kr/"
_EBS_M = "https://mid.ebs.co.kr/"
_EBSE = "https://www.ebse.co.kr/"

# 학년별 수학 단원 (2022 개정)
_MATH_UNITS: dict[str, list[str]] = {
    "e1": ["9까지의 수", "여러 가지 모양", "덧셈과 뺄셈", "100까지의 수", "규칙 찾기·시계"],
    "e2": ["세 자리 수", "덧셈과 뺄셈", "길이 재기", "곱셈구구", "규칙 찾기"],
    "e3": ["덧셈과 뺄셈", "나눗셈", "곱셈", "분수와 소수", "길이와 시간"],
    "e4": ["큰 수", "곱셈과 나눗셈", "각도", "분수의 덧셈과 뺄셈", "막대그래프"],
    "e5": ["자연수의 혼합 계산", "약수와 배수", "약분과 통분", "분수의 덧셈과 뺄셈", "다각형의 넓이"],
    "e6": ["분수의 나눗셈", "소수의 나눗셈", "비와 비율", "비례식과 비례배분", "직육면체의 부피·겉넓이"],
    "m1": ["소인수분해", "정수와 유리수", "문자와 식·일차방정식", "좌표평면과 그래프", "기본 도형", "통계"],
    "m2": ["유리수와 순환소수", "식의 계산", "연립일차방정식·부등식", "일차함수", "도형의 성질·닮음", "확률"],
    "m3": ["제곱근과 실수", "인수분해", "이차방정식", "이차함수", "삼각비", "원의 성질"],
}

# 학년별 비(非)수학 핵심 단원 (과목, 단원명)
_OTHER_UNITS: dict[str, list[tuple[str, str]]] = {
    "e1": [("국어", "한글 또박또박 읽고 쓰기")],
    "e2": [("국어", "마음을 나타내는 말·받아쓰기")],
    "e3": [("국어", "중심 생각 파악(독해)"), ("영어", "알파벳·듣기·말하기")],
    "e4": [("국어", "글의 흐름·요약"), ("영어", "기초 어휘·읽기")],
    "e5": [("국어", "주장과 근거(설명·논설)"), ("영어", "문장·기초 문법")],
    "e6": [("국어", "비문학 독해"), ("영어", "문법·어휘 확장")],
    "m1": [("국어", "문법·문학 기초·비문학"), ("영어", "독해·어휘")],
    "m2": [("국어", "설명·설득 글 독해"), ("영어", "독해·문법 심화")],
    "m3": [("국어", "비문학·문학 심화"), ("영어", "독해 속도·어휘")],
}


def _math_link(grade_key: str) -> tuple[str, str, str]:
    """(provider, cost, url) for math by grade."""
    if grade_key in _KHAN:
        return ("칸아카데미 한국어", "무료", _KHAN[grade_key])
    return ("EBS 중학", "무료~저렴", _EBS_M)


def _other_link(subject: str, grade_key: str) -> tuple[str, str, str]:
    if subject == "영어":
        return ("EBSe", "무료", _EBSE)
    ebs = _EBS_M if grade_key.startswith("m") else _EBS_P
    prov = "EBS 중학" if grade_key.startswith("m") else "EBS 초등"
    return (prov, "무료~저렴" if grade_key.startswith("m") else "무료", ebs)


def build_units(age_years: int) -> UnitsResponse:
    grade = grade_for_age(age_years)
    units: list[Unit] = []
    # 수학 단원
    for name in _MATH_UNITS.get(grade.key, []):
        prov, cost, url = _math_link(grade.key)
        units.append(Unit(subject="수학", name=name, provider=prov, cost=cost, url=url))
    # 기타 교과 핵심 단원
    for subject, name in _OTHER_UNITS.get(grade.key, []):
        prov, cost, url = _other_link(subject, grade.key)
        units.append(Unit(subject=subject, name=name, provider=prov, cost=cost, url=url))
    return UnitsResponse(grade=grade.label, units=units)
