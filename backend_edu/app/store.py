"""동기화 코드 기반 서버 저장 (MVP).

사용자가 정한 '동기화 코드'를 키로 프로필·이력을 서버 파일에 저장/조회한다.
여러 기기에서 같은 코드로 불러올 수 있다.
주의: 비밀번호 없는 MVP 수준 — 추측 어려운 코드 권장. 운영 시 로그인·DB로 대체.
"""
from __future__ import annotations

import json
from pathlib import Path

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_FILE = _DATA_DIR / "sync.json"


def _load_all() -> dict:
    try:
        return json.loads(_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_all(data: dict) -> None:
    _DATA_DIR.mkdir(exist_ok=True)
    _FILE.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def _key(code: str) -> str:
    return (code or "").strip().lower()


def save_profile(code: str, payload: dict) -> None:
    k = _key(code)
    if not k:
        raise ValueError("empty code")
    data = _load_all()
    data[k] = payload
    _save_all(data)


def load_profile(code: str) -> dict | None:
    return _load_all().get(_key(code))
