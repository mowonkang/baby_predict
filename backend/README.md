# baby_predict — Backend (MVP)

아기 **성향(기질) + 월령 + 환경** 기반 용품 추천 엔진의 MVP 백엔드 (FastAPI).
설계 근거: [`../docs/추천엔진_설계.md`](../docs/추천엔진_설계.md)

## 구조

```
backend/
├─ app/
│  ├─ models.py         # Pydantic 도메인 모델 (프로필, 기질벡터, 추천)
│  ├─ temperament.py    # 성향 진단 설문 → 기질 벡터
│  ├─ developmental.py  # 월령별 발달 매핑 테이블
│  ├─ catalog.py        # 샘플 상품 카탈로그 (인기도·기질 친화도)
│  ├─ recommender.py    # 규칙기반 추천 엔진 (Stage 1)
│  └─ main.py           # FastAPI 엔드포인트
├─ static/index.html    # 데모 UI (단일 페이지)
└─ tests/               # pytest (17 cases)
```

## 실행

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

- 데모 UI: http://localhost:8000/
- API 문서(Swagger): http://localhost:8000/docs

## 엔드포인트

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/health` | 헬스체크 |
| GET | `/api/survey` | 성향 진단 설문 문항 |
| POST | `/api/recommend` | 프로필 → 추천 결과 |

### 예시

```bash
curl -X POST localhost:8000/api/recommend -H 'Content-Type: application/json' -d '{
  "age_months": 12,
  "budget_max": 100000,
  "survey": [{"question_id":"q1","value":5},{"question_id":"q2","value":1}]
}'
```

## 테스트

```bash
cd backend
pytest -q
```

## 추천 로직 (요약)

`점수 = 0.40·인기도(국민템) + 0.35·기질 친화도 + 0.25·발달 적합도`
각 추천에는 설명(`reasons`)이 함께 제공된다. 데이터가 없는 콜드스타트 상태에서도
규칙기반 + 인기도로 동작한다. 이후 단계(협업필터링 → 하이브리드 ML)는
`docs/추천엔진_설계.md` §4 참조.
