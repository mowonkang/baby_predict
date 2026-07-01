@echo off
chcp 65001 >nul
setlocal enableextensions
title EduPath
cd /d "%~dp0backend_edu"

echo ==================================================
echo   EduPath - 적성 기반 교육 로드맵 (로컬 실행)
echo ==================================================
echo.

if not exist "app\main.py" (
  echo [오류] backend_edu\app\main.py 를 찾을 수 없습니다.
  echo   이 start.bat 은 baby_predict 폴더 안에서 실행해야 합니다.
  echo   (GitHub ZIP 을 받은 경우 압축을 풀고 그 안의 start.bat 을 실행하세요.)
  echo.
  pause
  exit /b 1
)

REM --- Python 탐지 (py 우선, 없으면 python) ---
set "PY="
where py >nul 2>nul && set "PY=py"
if not defined PY ( where python >nul 2>nul && set "PY=python" )
if not defined PY (
  echo [오류] Python 이 설치되어 있지 않거나 PATH 에 없습니다.
  echo   1) https://www.python.org/downloads/ 에서 Python 3.11 이상 설치
  echo   2) 설치 첫 화면에서 "Add Python to PATH" 를 반드시 체크
  echo   3) 설치 후 이 파일을 다시 실행하세요.
  echo.
  pause
  exit /b 1
)

echo [1/2] 필요한 패키지를 설치합니다 (처음 1회만 시간이 걸립니다)...
%PY% -m pip install -q -r requirements.txt
if errorlevel 1 (
  echo   - 기본 설치에 실패해 사용자 폴더(--user) 로 재시도합니다...
  %PY% -m pip install -q --user -r requirements.txt
)
if errorlevel 1 (
  echo [오류] 패키지 설치에 실패했습니다.
  echo   인터넷 연결을 확인하거나, 관리자 권한으로 다시 실행해 보세요.
  echo.
  pause
  exit /b 1
)

echo [2/2] 서버를 시작합니다. 잠시 후 브라우저가 자동으로 열립니다.
echo        주소: http://localhost:8000
echo        (종료하려면 이 창에서 Ctrl+C 를 누르거나 창을 닫으세요)
echo.
start "" cmd /c "timeout /t 3 /nobreak >nul & start http://localhost:8000"
%PY% -m uvicorn app.main:app --host 127.0.0.1 --port 8000

echo.
echo 서버가 종료되었습니다. (포트 8000 이 이미 사용 중이면 위 메시지를 확인하세요)
pause
