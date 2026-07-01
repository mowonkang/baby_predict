"""인앱 커뮤니티 — 엄마들이 지역·주제별로 정보를 나누고 의견을 다는 게시판.

외부 맘카페 링크(local.py)와 별개로, **앱 안에서 직접 글·댓글**을 남겨 정보를 나눈다.
- 지역 + 주제(예: 수학학원, 유아영어, 자유)로 글을 필터링
- 글에 댓글·공감(좋아요)
- 서버 JSON 저장(MVP). 운영 시 로그인·DB·신고/차단·욕설필터로 확장.

⚠️ 사용자 작성 콘텐츠 — 상업/비방/개인정보 게시는 금지(신고 대상). 표시광고·명예훼손 정책은 기획안 §12.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from .models import CommunityComment, CommunityListResponse, CommunityPost

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_FILE = _DATA_DIR / "community.json"

# 예시 시드 글(빈 게시판 방지). 파일이 없을 때 최초 1회 기록되며, 이후 실제 글이 쌓인다.
SEED_POSTS: list[dict] = [
    {"id": "seed1", "region": "서울 노원 중계동", "topic": "수학학원",
     "title": "중계동 초등 사고력수학 어디가 좋을까요?(예시)",
     "body": "3학년 아이 사고력수학 알아보고 있어요. 판서식보다 아이가 참여하는 곳 찾아요. 추천 부탁드려요!",
     "author": "중계맘", "date": "2026-06-20", "likes": 3,
     "comments": [{"author": "이웃맘", "text": "시매쓰 상담 가봤는데 아이가 흥미로워했어요.", "date": "2026-06-21"},
                  {"author": "익명맘", "text": "레벨테스트 먼저 받아보세요~", "date": "2026-06-22"}]},
    {"id": "seed2", "region": "온라인", "topic": "유아영어",
     "title": "5세 영어 노출, 유료학원 vs 무료앱 고민(예시)",
     "body": "아직 어린데 학원까지 필요할까요? 집에서 EBSe랑 영어동요로 하는 중인데 효과 있을지 궁금해요.",
     "author": "새싹맘", "date": "2026-06-18", "likes": 5,
     "comments": [{"author": "경험맘", "text": "이 시기엔 노출·놀이면 충분하다고 봐요. 무료로 시작 추천!", "date": "2026-06-19"}]},
]


def _load() -> list[dict]:
    """저장 파일을 읽되, 없으면 시드로 초기화."""
    try:
        return json.loads(_FILE.read_text(encoding="utf-8"))
    except Exception:
        return [dict(p) for p in SEED_POSTS]


def _save(posts: list[dict]) -> None:
    _DATA_DIR.mkdir(exist_ok=True)
    _FILE.write_text(json.dumps(posts, ensure_ascii=False), encoding="utf-8")


def _today() -> str:
    return date.today().isoformat()


def _to_post(d: dict) -> CommunityPost:
    return CommunityPost(
        id=d["id"], region=d.get("region", ""), topic=d.get("topic", "자유"),
        title=d.get("title", ""), body=d.get("body", ""), author=d.get("author", "익명맘"),
        date=d.get("date", ""), likes=int(d.get("likes", 0)),
        comments=[CommunityComment(**c) for c in d.get("comments", [])])


def list_posts(region: str | None, topic: str | None) -> CommunityListResponse:
    region = (region or "").strip()
    topic = (topic or "").strip()
    posts = _load()
    if region:
        toks = region.split()
        posts = [p for p in posts
                 if p.get("region") == "온라인"
                 or any(t and t in p.get("region", "") for t in toks)]
    if topic and topic != "전체":
        posts = [p for p in posts if p.get("topic") == topic]
    posts = sorted(posts, key=lambda p: (p.get("date", ""), p.get("likes", 0)), reverse=True)
    return CommunityListResponse(region=region or "전체", topic=topic or "전체",
                                 posts=[_to_post(p) for p in posts])


def create_post(region: str, topic: str, title: str, body: str, author: str) -> CommunityPost:
    posts = _load()
    new_id = f"p{len(posts) + 1}_{_today().replace('-', '')}"
    rec = {"id": new_id, "region": region.strip(), "topic": (topic or "자유").strip(),
           "title": title.strip(), "body": body.strip(), "author": (author or "익명맘").strip(),
           "date": _today(), "likes": 0, "comments": []}
    posts.append(rec)
    _save(posts)
    return _to_post(rec)


def add_comment(post_id: str, author: str, text: str) -> bool:
    posts = _load()
    for p in posts:
        if p["id"] == post_id:
            p.setdefault("comments", []).append(
                {"author": (author or "익명맘").strip(), "text": text.strip(), "date": _today()})
            _save(posts)
            return True
    return False


def like_post(post_id: str) -> int | None:
    """공감 +1. 반환: 새 공감 수(없는 글이면 None)."""
    posts = _load()
    for p in posts:
        if p["id"] == post_id:
            p["likes"] = int(p.get("likes", 0)) + 1
            _save(posts)
            return p["likes"]
    return None
