"""AI 시대 역량 축 테스트."""
from app.ai_track import build_ai_track


def test_ai_track_each_stage():
    for age, label in [(8, "초등 저학년"), (14, "중등"), (17, "고등")]:
        a = build_ai_track(age)
        assert a.stage == label
        assert a.skills and a.tools and a.tip


def test_middle_mentions_python_or_data():
    a = build_ai_track(14)
    text = " ".join(a.skills + a.tools)
    assert "파이썬" in text or "데이터" in text


def test_tip_is_constant_axis():
    assert "AI" in build_ai_track(10).tip
