"""공신력 체계 벤치마킹: 기질(CBQ)·예상 능력치(DMGT)·공인 등급 테크트리·레지스트리 테스트."""
from app.frameworks import all_frameworks
from app.models import StudentProfile
from app.persona import build_persona
from app.projection import build_projection
from app.techtree import build_techtree
from app.temperament import build_temperament, items


def test_temperament_items_cover_cbq_factors():
    facs = {i.factor for i in items()}
    assert facs == {"surgency", "negative_affect", "effortful_control"}
    assert len(items()) == 6


def test_temperament_high_surgency_low_negative():
    beh = {"tp_s1": 4, "tp_s2": 4, "tp_n1": 0, "tp_n2": 0, "tp_e1": 2, "tp_e2": 2}
    t = build_temperament(beh)
    d = {f.key: f for f in t.factors}
    assert d["surgency"].level == "높음" and d["negative_affect"].level == "낮음"
    assert t.type_label == "활발·긍정형"
    assert t.fit_guide and "외향성" in t.fit_guide


def test_temperament_cold_start():
    t = build_temperament({})
    assert t.answered == 0 and t.type_label == "미입력"
    assert all(f.score == 50 for f in t.factors)


def test_temperament_types_vary():
    shy = build_temperament({"tp_s1": 0, "tp_s2": 0, "tp_n1": 4, "tp_n2": 4})
    calm = build_temperament({"tp_s1": 0, "tp_s2": 0, "tp_n1": 0, "tp_n2": 0})
    assert shy.type_label == "신중·민감형" and calm.type_label == "차분·안정형"


def test_persona_includes_temperament():
    p = build_persona(StudentProfile(
        age_years=6, interests=["act_art"],
        behaviors={"tp_s1": 4, "tp_s2": 4, "tp_n1": 0, "tp_n2": 0}))
    assert "활발·긍정형" in p.persona_label and p.fit_guide
    # 기질 미입력이면 기존 라벨 유지
    p2 = build_persona(StudentProfile(age_years=6, interests=["act_art"]))
    assert p2.temperament_label == "" and "학습자" in p2.persona_label


def test_projection_bands_ordered_and_capped():
    pr = build_projection(StudentProfile(age_years=10, interests=["act_sci", "act_math"]))
    assert pr.projections and pr.horizon_label
    for p in pr.projections:
        assert p.conservative <= p.base <= p.optimistic <= 100
        assert p.now <= p.optimistic
    assert any("DMGT" in d for d in pr.drivers)


def test_projection_targeted_stat_grows_more():
    pr = build_projection(StudentProfile(age_years=10, interests=["act_sci"]))
    by = {p.key: p for p in pr.projections}
    # 강점(탐구) 축은 비대상 축보다 base 성장폭이 큼
    growth_sci = by["science"].base - by["science"].now
    growth_phys = by["physical"].base - by["physical"].now
    assert growth_sci > growth_phys


def test_techtree_has_certs_and_stages():
    r = build_techtree(StudentProfile(age_years=10, interests=["act_art"]))
    art = next(t for t in r.tracks if t.key == "art")
    assert "ABRSM" in art.cert_system
    assert any("ABRSM" in n.cert for n in art.nodes)
    lang = next(t for t in r.tracks if t.key == "lang")
    assert any("CEFR" in n.cert for n in lang.nodes)
    # 모든 노드에 재능발달 단계(Bloom·DMGT) 라벨
    assert all(n.stage for tr in r.tracks for n in tr.nodes)


def test_frameworks_registry():
    fr = all_frameworks()
    keys = {f.key for f in fr}
    assert {"kwisc", "kdst", "cbq", "gardner", "riasec", "dmgt", "cefr", "growth"} <= keys
    assert all(f.authority and f.how_used for f in fr)
