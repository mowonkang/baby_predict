# baby_predict

**아기 성향 기반 맞춤 추천 커머스 플랫폼** — 아기의 성향(기질)·월령·거주지 등을 입력하면 발달 단계에 맞는 국민템·용품·놀이·교구를 예측·추천하는 플랫폼.

- **주 사용자**: 초보 엄마·아빠, 영유아 양육자
- **수익화**: 브랜드(업체) 입점/구독료 + 광고
- **핵심**: 성향·발달 기반 예측 추천 엔진

## 기획 문서

| 문서 | 내용 |
|------|------|
| [docs/기획안.md](docs/기획안.md) | 종합 사업·제품 기획안 (시장·BM·로드맵·리스크) |
| [docs/추천엔진_설계.md](docs/추천엔진_설계.md) | 추천/예측 엔진 상세 설계 |
| [docs/데이터소스.md](docs/데이터소스.md) | 활용 가능한 외부 데이터 소스 |

## MVP (코드)

성향 진단 → 규칙기반 추천 엔진의 동작하는 MVP가 [`backend/`](backend/)에 있습니다 (FastAPI).

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload   # 데모 UI: http://localhost:8000/
pytest -q                       # 테스트 17건
```

자세한 내용은 [backend/README.md](backend/README.md) 참조.
