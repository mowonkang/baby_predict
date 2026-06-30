# baby_predict

성향·적성을 진단해 **개인에게 맞는 것을 단계별로 추천**하는 플랫폼 프로젝트. 두 개의 트랙으로 구성됩니다.

| 트랙 | 내용 | 문서 | 코드 |
|------|------|------|------|
| 🍼 **아기용품** | 아기 성향·월령 → 발달 맞춤 용품·놀이 추천 | [docs/](docs/) | [backend/](backend/) |
| 🎓 **교육(EduPath)** | 학생 적성·학령 → 커리큘럼 추천 + 미취학~대학 교육 path | [docs/edu/](docs/edu/) | [backend_edu/](backend_edu/) |

---

## 🍼 아기용품 트랙

**아기 성향 기반 맞춤 추천 커머스 플랫폼** — 아기의 성향(기질)·월령·거주지 등을 입력하면 발달 단계에 맞는 국민템·용품·놀이·교구를 예측·추천하는 플랫폼.

- **주 사용자**: 초보 엄마·아빠, 영유아 양육자
- **수익화**: 브랜드(업체) 입점/구독료 + 광고
- **핵심**: 성향·발달 기반 예측 추천 엔진

### 기획 문서

| 문서 | 내용 |
|------|------|
| [docs/기획안.md](docs/기획안.md) | 종합 사업·제품 기획안 (시장·BM·로드맵·리스크) |
| [docs/추천엔진_설계.md](docs/추천엔진_설계.md) | 추천/예측 엔진 상세 설계 |
| [docs/데이터소스.md](docs/데이터소스.md) | 활용 가능한 외부 데이터 소스 |

### MVP (코드)

성향 진단 → 규칙기반 추천 엔진의 동작하는 MVP가 [`backend/`](backend/)에 있습니다 (FastAPI).

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload   # 데모 UI: http://localhost:8000/
pytest -q                       # 테스트 17건
```

자세한 내용은 [backend/README.md](backend/README.md) 참조.

---

## 🎓 교육 트랙 (EduPath)

**전 생애주기(0세~진로) 교육 가이드 플랫폼** — 나이/학년만 넣으면 **이 시기 할 일**(영아·유치원·초·중·고, 인문계 기준), 과목 보완(성취도 기반 + **무료/저렴 자원 우선**), 적성 기반 진로 마인드맵·유망 커리어를 제안하고, **성취도 변화까지 추적**.

- **주 사용자**: 학부모(미취학~고등) + 학생(중·고·대)
- **수익화**: 학원·인강·출판·컨설팅 업체 입점/구독료 + 광고
- **핵심**: 적성·학령 기반 추천 + 장기 교육 path 생성

### 기획 문서

| 문서 | 내용 |
|------|------|
| [docs/edu/기획안.md](docs/edu/기획안.md) | 교육 종합 사업·제품 기획안(무료/저가 구독 BM 포함) |
| [docs/edu/추천엔진_설계.md](docs/edu/추천엔진_설계.md) | 적성 진단 + 추천 + path 생성 설계 |
| [docs/edu/생애주기_가이드.md](docs/edu/생애주기_가이드.md) | 전 생애주기(0세~진로) 비전·단계 매핑 |
| [docs/edu/교육과정_커리큘럼.md](docs/edu/교육과정_커리큘럼.md) | 2022 개정·누리과정 학년·과목별 커리큘럼(딥리서치) |
| [docs/edu/교육현황_리서치.md](docs/edu/교육현황_리서치.md) | 한국 교육 현황 리서치(공식 출처) |
| [docs/edu/무료저가자원.md](docs/edu/무료저가자원.md) | 무료·저가 교육 자원 실제 링크 |
| [docs/edu/데이터소스.md](docs/edu/데이터소스.md) | 교육 외부 데이터 소스 |

### MVP (코드 + 앱)

적성 진단 → 추천 + 교육 path + 고교 과목 추천 MVP가 [`backend_edu/`](backend_edu/)에 있습니다 (FastAPI + 모바일 우선 웹앱/PWA).

**원클릭 실행**: 루트의 **`start.bat`**(Windows) 더블클릭 또는 `bash start.sh`(Mac/Linux) → 브라우저에 앱이 자동으로 열립니다.
비개발자용 안내: [docs/edu/실행방법.md](docs/edu/실행방법.md) · 앱 디자인: [docs/edu/앱_디자인.md](docs/edu/앱_디자인.md)

```bash
cd backend_edu && pip install -r requirements.txt
uvicorn app.main:app --reload   # 앱: http://localhost:8000/
pytest -q                       # 테스트 81건
```

자세한 내용은 [backend_edu/README.md](backend_edu/README.md) 참조.
