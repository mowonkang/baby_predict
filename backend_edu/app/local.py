"""지역 허브 — 실제 학원 정보 + 지도 + 맘카페 커뮤니티 연동.

학부모가 실제로 필요로 하는 세 가지를 한 곳에 모은다.
1. **실제 학원 목록** — 네이버 지역검색 라이브 API(환경변수 키가 있을 때) 또는 수집 스냅샷.
2. **지도 딥링크** — 카카오맵·네이버지도에서 '{지역} {과목}학원'을 바로 열기.
3. **맘카페 커뮤니티 딥링크** — 네이버 카페(맘카페)·후기 검색으로 실제 후기/토론을 열기.

딥링크는 **API 키 없이 항상 동작**한다(런타임 안전). 라이브 학원 조회는 키가 있으면 실데이터,
없으면 `data/academies_seed.json` 스냅샷을 사용한다.

⚠️ 학원명·주소는 공개 정보이며, 본 앱의 추천/평가가 아니다. 후기는 외부 커뮤니티 링크로 연결한다.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from urllib.parse import quote

from .models import LiveAcademy, LocalHubResponse, LocalLink

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_SEED_FILE = _DATA_DIR / "academies_seed.json"


# ── 딥링크 빌더 (키 불필요, 항상 동작) ─────────────────────────
def _q(*parts: str) -> str:
    return quote(" ".join(p for p in parts if p).strip())


def kakao_map_url(query: str) -> str:
    return f"https://map.kakao.com/?q={quote(query)}"


def naver_map_url(query: str) -> str:
    return f"https://map.naver.com/p/search/{quote(query)}"


def naver_cafe_search_url(query: str) -> str:
    # where=article → 카페글(맘카페 등)
    return f"https://search.naver.com/search.naver?where=article&query={quote(query)}"


def naver_review_search_url(query: str) -> str:
    return f"https://search.naver.com/search.naver?query={quote(query)}"


def map_links(region: str, subject: str) -> list[LocalLink]:
    q = f"{region} {subject}학원".strip()
    return [
        LocalLink(label=f"🗺️ 카카오맵에서 ‘{q}’ 보기", url=kakao_map_url(q), kind="map"),
        LocalLink(label=f"🗺️ 네이버지도에서 ‘{q}’ 보기", url=naver_map_url(q), kind="map"),
    ]


def community_links(region: str, subject: str) -> list[LocalLink]:
    q1 = f"{region} {subject}학원 추천".strip()
    q2 = f"{region} {subject}학원 후기".strip()
    return [
        LocalLink(label="💬 맘카페에서 학원 추천글 검색", url=naver_cafe_search_url(q1), kind="community"),
        LocalLink(label="⭐ 학원 후기·평판 검색", url=naver_review_search_url(q2), kind="search"),
    ]


# ── 실제 학원: 라이브 API(선택) → 스냅샷 폴백 ──────────────────
def _load_seed() -> list[dict]:
    try:
        return json.loads(_SEED_FILE.read_text(encoding="utf-8")).get("items", [])
    except Exception:
        return []


def _seed_academies(region: str, subject: str) -> list[LiveAcademy]:
    region = (region or "").strip()
    subject = (subject or "").strip()
    out: list[LiveAcademy] = []
    for it in _load_seed():
        r, s = it.get("region", ""), it.get("subject", "")
        # 지역 토큰 일부라도 겹치고(있으면), 과목이 맞으면 채택
        region_ok = (not region) or any(tok and tok in r for tok in region.split())
        subject_ok = (not subject) or subject in s or s in subject
        if region_ok and subject_ok:
            name = it.get("name", "")
            out.append(LiveAcademy(
                name=name, category=it.get("category", ""), address=it.get("address", ""),
                url=it.get("url", ""), map_url=kakao_map_url(name or f"{r} {s}학원")))
    return out


def _live_academies(region: str, subject: str) -> list[LiveAcademy] | None:
    """네이버 지역검색 API로 실시간 조회. 키(NAVER_CLIENT_ID/SECRET) 없으면 None."""
    cid = os.environ.get("NAVER_CLIENT_ID")
    csec = os.environ.get("NAVER_CLIENT_SECRET")
    if not (cid and csec):
        return None
    try:  # 표준 라이브러리만 사용(추가 의존성 없음)
        import urllib.request as _rq

        query = f"{region} {subject}학원".strip()
        url = "https://openapi.naver.com/v1/search/local.json?display=5&query=" + quote(query)
        req = _rq.Request(url, headers={
            "X-Naver-Client-Id": cid, "X-Naver-Client-Secret": csec})
        with _rq.urlopen(req, timeout=4) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        out: list[LiveAcademy] = []
        for it in data.get("items", []):
            name = _strip_tags(it.get("title", ""))
            out.append(LiveAcademy(
                name=name, category=it.get("category", ""),
                address=it.get("roadAddress") or it.get("address", ""),
                url=it.get("link", ""), map_url=kakao_map_url(name or query)))
        return out
    except Exception:
        return None


def _strip_tags(s: str) -> str:
    return s.replace("<b>", "").replace("</b>", "")


def build_local_hub(region: str | None, subject: str | None) -> LocalHubResponse:
    region = (region or "").strip()
    subject = (subject or "수학").strip()

    live = _live_academies(region, subject)
    if live is not None:
        academies, is_live = live, True
        source = "네이버 지역검색 API(실시간)"
    else:
        academies, is_live = _seed_academies(region, subject), False
        source = "네이버 지역검색 스냅샷(2026-07). 키 설정 시 실시간 조회."

    note = ("지도·맘카페 링크는 항상 실시간입니다. 학원명·주소는 공개 정보이며 추천/평가가 아닙니다."
            if academies else
            "이 지역·과목의 수집 데이터가 아직 없어요. 아래 지도·맘카페 링크로 실시간 확인하세요.")

    return LocalHubResponse(
        region=region or "전체", subject=subject,
        academies=academies,
        map_links=map_links(region, subject),
        community_links=community_links(region, subject),
        live=is_live, source=source, note=note)
