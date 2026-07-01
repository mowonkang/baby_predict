"""지역 허브(실학원·지도·맘카페) + 인앱 커뮤니티 테스트."""
import json
from pathlib import Path

from app import community
from app.local import build_local_hub, kakao_map_url

_CFILE = Path(__file__).resolve().parent.parent / "data" / "community.json"


def _reset_community():
    if _CFILE.exists():
        _CFILE.unlink()


# ── 지역 허브 ───────────────────────────────────────────
def test_local_hub_has_map_and_community_links():
    hub = build_local_hub("서울 노원 중계동", "수학")
    assert hub.map_links and hub.community_links
    assert all(l.url.startswith("https://") for l in hub.map_links + hub.community_links)
    # 카카오맵/네이버지도 둘 다
    kinds = {l.kind for l in hub.map_links}
    assert "map" in kinds


def test_local_hub_seed_academies_matched():
    hub = build_local_hub("중계동", "수학")
    assert not hub.live  # 키 없으면 스냅샷
    assert hub.academies
    names = [a.name for a in hub.academies]
    assert any("중계" in n for n in names)
    assert all(a.map_url.startswith("https://map.kakao.com") for a in hub.academies)


def test_local_hub_unknown_region_still_gives_links():
    hub = build_local_hub("어딘가시 아무동", "국어")
    assert hub.map_links and hub.community_links  # 링크는 항상 제공
    # 지역 토큰 안 겹치면 스냅샷 학원은 비어도 됨(링크로 실시간 안내)


def test_kakao_map_url_encoding():
    url = kakao_map_url("중계동 수학학원")
    assert url.startswith("https://map.kakao.com/?q=") and "%" in url


# ── 인앱 커뮤니티 ───────────────────────────────────────
def test_community_seed_posts_listed():
    _reset_community()
    res = community.list_posts("", "")
    assert len(res.posts) >= 2  # 시드 글


def test_community_filter_by_region_and_topic():
    _reset_community()
    res = community.list_posts("중계동", "수학학원")
    assert res.posts and all("중계" in p.region or p.region == "온라인" for p in res.posts)
    assert all(p.topic == "수학학원" for p in res.posts)


def test_community_create_and_comment_and_like():
    _reset_community()
    p = community.create_post("서울 양천 목동", "수학학원", "목동 초등수학 문의", "추천 부탁해요", "목동맘")
    assert p.id and p.likes == 0
    # 새 글이 목록에 뜬다
    listed = community.list_posts("목동", "수학학원")
    assert any(x.id == p.id for x in listed.posts)
    # 댓글
    assert community.add_comment(p.id, "이웃맘", "여기 좋아요") is True
    assert community.add_comment("없는id", "x", "y") is False
    # 공감
    assert community.like_post(p.id) == 1
    assert community.like_post("없는id") is None
    # 반영 확인
    again = [x for x in community.list_posts("목동", "수학학원").posts if x.id == p.id][0]
    assert again.likes == 1 and again.comments and again.comments[0].text == "여기 좋아요"
    _reset_community()
