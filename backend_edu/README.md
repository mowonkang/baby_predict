# EduPath — Backend (MVP, 교육 트랙)

학생 **적성(흥미 RIASEC + 학습성향) + 학령** 기반 커리큘럼 추천 및 **교육 path** 생성 엔진 (FastAPI).
설계 근거: [`../docs/edu/추천엔진_설계.md`](../docs/edu/추천엔진_설계.md)

## 구조

```
backend_edu/
├─ app/
│  ├─ models.py        # Pydantic 모델 (적성프로필·학생프로필·추천·path)
│  ├─ aptitude.py      # 적성 진단 설문(18문항) → 흥미(RIASEC)+학습성향 벡터
│  ├─ curriculum.py    # 학령 단계 매핑 (미취학~대학)
│  ├─ catalog.py       # 교육 리소스 샘플 카탈로그 (인기도·흥미 친화도)
│  ├─ recommender.py   # 규칙기반 추천 엔진 (Stage 1)
│  ├─ pathway.py       # 적성 → 미취학~대학 교육 path 생성기
│  └─ main.py          # FastAPI 엔드포인트
├─ static/index.html   # 데모 UI (적성 진단 → 추천 + 로드맵 타임라인)
└─ tests/              # pytest (25 cases)
```

## 실행

**가장 쉬운 방법 (원클릭)**: 레포 루트의 `start.bat`(Windows) 더블클릭 또는 `bash start.sh`(Mac/Linux).
비개발자용 안내: [`../docs/edu/실행방법.md`](../docs/edu/실행방법.md)

**수동 실행**:
```bash
cd backend_edu
pip install -r requirements.txt
uvicorn app.main:app --reload
```

- 앱(모바일 우선 PWA): http://localhost:8000/
- API 문서(Swagger): http://localhost:8000/docs

## 엔드포인트

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/health` | 헬스체크 |
| POST | `/api/grade-plan` | 나이/학년 → **이 학년에 할 것**(유치원~고3, 인문계) + 핵심 과목 |
| POST | `/api/achievement` | 과목별 수준(잘함/보통/부족) → **보완 과목 + 학원·무료/저렴 교육 추천**(학교급별 자원·실제 링크) |
| POST | `/api/lifecycle` | 나이 → **전 생애주기 타임라인**(영아~대학·진로) + 현재 위치 |
| GET | `/api/grades` | 학년 목록(유치원~고3) |
| POST | `/api/guide` | 나이 → 이 시기 공부할 것·준비할 것(학교급 단위) |
| GET | `/api/activities` | 쉬운 진단용 — 관심활동·학습성향 선택 옵션 |
| GET | `/api/survey` | (레거시) 리커트 적성 설문 |
| POST | `/api/recommend` | 프로필 → 커리큘럼 추천 |
| POST | `/api/pathway` | 프로필 → 교육 path(로드맵, 강점 없으면 일반계 기본) |
| POST | `/api/subjects` | 프로필 → 고교 과목 추천(2022 개정: 공통/일반/진로/융합선택) |
| POST | `/api/ai-track` | 나이 → **AI 시대 역량 축**(단계별 AI·디지털 역량, 계열 공통) |
| POST | `/api/careers` | 프로필 → **유망 커리어 추천**(로보틱스·공학·화학·바이오·생명공학·의학·AI 등) + 준비 커리큘럼 |

> 진단 입력은 `interests`(관심활동 선택, 권장) / `survey`(리커트) / `aptitude`(직접) 중 택1. 미입력 시 일반계 기본.

### 예시

```bash
curl -X POST localhost:8000/api/pathway -H 'Content-Type: application/json' -d '{
  "age_years": 11,
  "survey": [{"question_id":"i_i1","value":5},{"question_id":"i_i2","value":5},{"question_id":"i_r1","value":5}]
}'
```

## 테스트

```bash
cd backend_edu
pytest -q
```

## 핵심 로직 (요약)

- **추천**: `점수 = 0.40·인기도 + 0.35·적성(흥미) 친화도 + 0.25·단계 적합도`, 각 추천에 설명(reasons) 포함, 콜드스타트 동작.
- **교육 path**: 흥미 RIASEC 상위 유형 → 진로 계열 트랙 매핑 → 현재 학령부터 대학까지 단계별 마일스톤(집중 영역·활동·의사결정 포인트) 생성.
- 이후 단계(협업필터링 → 하이브리드 ML)는 `docs/edu/추천엔진_설계.md` §4 참조.
