"""생애주기 타임라인 테스트."""
from app.lifecycle import build_lifecycle


def test_lifecycle_has_all_stages():
    res = build_lifecycle(9)
    labels = [s.label for s in res.stages]
    assert labels[0] == "영아" and labels[-1] == "대학·진로"
    assert len(res.stages) == 8


def test_current_marked():
    res = build_lifecycle(14)
    current = [s for s in res.stages if s.current]
    assert len(current) == 1 and current[0].label == "중등"
    assert res.current_label == "중등"


def test_infant_and_adult():
    assert build_lifecycle(1).current_label == "영아"
    assert build_lifecycle(20).current_label == "대학·진로"
    assert build_lifecycle(40).current_label == "대학·진로"  # 클램프
