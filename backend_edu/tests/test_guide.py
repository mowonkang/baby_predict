"""단계별 학습·준비 가이드 테스트."""
from app.guide import build_guide


def test_guide_for_each_stage():
    for age, label in [(5, "미취학"), (8, "초등 저학년"), (14, "중등"), (17, "고등")]:
        g = build_guide(age)
        assert g.stage == label
        assert g.study and g.prepare and g.tip


def test_high_school_guide_mentions_naesin():
    g = build_guide(17)
    text = " ".join(g.study + g.prepare) + g.tip
    assert "내신" in text  # 일반계 고등 핵심


def test_guide_out_of_range_clamps():
    g = build_guide(30)  # 대학 단계로 클램프
    assert g.stage == "대학"
