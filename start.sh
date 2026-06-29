#!/usr/bin/env bash
# EduPath 로컬 실행 (macOS / Linux) — Windows는 start.bat 사용
set -e
cd "$(dirname "$0")/backend_edu"

PY="$(command -v python3 || command -v python || true)"
if [ -z "$PY" ]; then
  echo "[오류] Python이 없습니다. https://www.python.org/downloads/ 에서 3.11+ 설치 후 다시 실행하세요."
  exit 1
fi

echo "[1/2] 패키지 설치 중 (처음 1회만 시간이 걸립니다)..."
"$PY" -m pip install -q -r requirements.txt

echo "[2/2] 서버 시작: http://localhost:8000  (Ctrl+C 로 종료)"
(
  sleep 3
  (command -v open >/dev/null && open http://localhost:8000) \
    || (command -v xdg-open >/dev/null && xdg-open http://localhost:8000) \
    || true
) >/dev/null 2>&1 &

exec "$PY" -m uvicorn app.main:app --host 127.0.0.1 --port 8000
