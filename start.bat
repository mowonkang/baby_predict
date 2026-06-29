@echo off
chcp 65001 >nul
setlocal
title EduPath
cd /d "%~dp0backend_edu"

echo ==================================================
echo   EduPath - 적성 기반 교육 로드맵 (로컬 실행)
echo ==================================================
echo.

REM --- Python 탐지 (py 우선, 없으면 python) ---
set "PY="
where py >nul 2>nul && set "PY=py"
if not defined PY ( where python >nul 2>nul && set "PY=python" )
if not defined PY (
  echo [오류] Python이 설치되어 있지 않습니다.
  echo   1) https://www.python.org/downloads/ 에서 Python 3.11 이상 설치
  echo   2) 설치 화면에서 "Add Python to PATH" 체크 필수
  echo   3) 설치 후 이 파일을 다시 실행하세요.
  echo.
  pause
  exit /b 1
)

echo [1/2] 필요한 패키지를 설치합니다 (처음 1회만 시간이 걸립니다)...
%PY% -m pip install -q -r requirements.txt
if errorlevel 1 (
  echo [오류] 패키지 설치에 실패했습니다. 인터넷 연결을 확인하고 다시 시도하세요.
  pause
  exit /b 1
)

echo [2/2] 서버를 시작합니다. 잠시 후 브라우저가 자동으로 열립니다.
echo        주소: http://localhost:8000   (이 창을 닫으면 종료됩니다)
echo.
start "" cmd /c "timeout /t 3 /nobreak >nul & start http://localhost:8000"
%PY% -m uvicorn app.main:app --host 127.0.0.1 --port 8000

pause
