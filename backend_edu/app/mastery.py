"""BKT-lite 숙련 추적 (Bayesian Knowledge Tracing 간이판).

단원/과목별 정·오답 시퀀스로 '숙련 확률'을 베이지안으로 업데이트한다.
LLM 호출 없이 서버 산수만으로 동작(추가 과금 0), 해석 가능.
근거: docs/edu/성장성_및_예측모델.md §3
"""
from __future__ import annotations

# BKT 기본 파라미터(초기값 — 운영 시 데이터로 보정)
P_INIT = 0.30   # 사전 숙련 확률
P_LEARN = 0.15  # 한 번 풀 때 학습(전이) 확률
P_SLIP = 0.10   # 알지만 실수할 확률
P_GUESS = 0.20  # 모르지만 찍어 맞힐 확률


def bkt_update(p_known: float, correct: bool,
               slip: float = P_SLIP, guess: float = P_GUESS, learn: float = P_LEARN) -> float:
    """관측(정/오답) 반영 → 학습 전이까지 적용한 사후 숙련 확률."""
    if correct:
        num = p_known * (1 - slip)
        den = num + (1 - p_known) * guess
    else:
        num = p_known * slip
        den = num + (1 - p_known) * (1 - guess)
    p_obs = num / den if den else p_known
    return p_obs + (1 - p_obs) * learn


def mastery_from_seq(correct_seq: list[bool], p0: float = P_INIT) -> float:
    p = p0
    for c in correct_seq:
        p = bkt_update(p, c)
    return round(min(1.0, max(0.0, p)), 4)


def p_correct_next(p_known: float, slip: float = P_SLIP, guess: float = P_GUESS) -> float:
    """다음 문제 정답 확률 예측."""
    return round(p_known * (1 - slip) + (1 - p_known) * guess, 4)


def level_from_mastery(m: float) -> str:
    if m >= 0.75:
        return "잘함"
    if m >= 0.45:
        return "보통"
    return "부족"
