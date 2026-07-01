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
└─ tests/              # pytest (39 cases)
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
| POST | `/api/units` | 나이/학년 → **이번 학년 단원 + 단원별 무료강의 링크**(칸아카데미 학년별 수학·EBS) |
| POST | `/api/plan` | 성취도·학년·가용시간 → **적응형 주간 학습계획**(시간배분·할일·목표·무료자료·복습) — 규칙 기반, **LLM 호출 없음** |
| POST | `/api/diagnostic` | 학년대 미니 진단 문항(수학·영어, 정답 비노출) |
| POST | `/api/mastery` | 진단 응답 → **숙련도(BKT) + IRT(또래 백분위·적정 난이도) + 분산복습일(D-day)** — LLM 없음 |
| POST | `/api/persona` | 흥미·학습성향·성취 통합 **학습 페르소나 라벨** |
| GET | `/api/extracurriculars` | 사교육·활동(몬테소리·영어·태권도·미술 등) **계열별 선택지**(쉬운 탭 입력) |
| POST | `/api/stats` | 관심·경험·성취 → **8각형 능력치 스탯**(레이더) — 규칙 기반, **LLM 없음** |
| POST | `/api/techtree` | 능력치·나이 → **사교육 전체 테크트리 + 추천 루트**(스타크래프트식) — **LLM 없음** |
| POST | `/api/report` | **부모 리포트**(페르소나·이 학년 할 일·보완·주간계획 요약) |
| POST | `/api/academies` | 지역·약점 과목·학년 → **학원 추천**(입점/광고 별도 표기, 평점·예시데이터) |
| GET `/api/academies/{id}/reviews` · POST `/api/reviews` | 학원 **평점·리뷰**(선생님·강의 평) 조회/작성(서버 저장) |
| POST | `/api/sync/save` · GET `/api/sync/{code}` | **동기화 코드** 서버 저장/조회(여러 기기, MVP) |

> 응답에 `source`/`updated`(출처·갱신일) 포함. 영아(0~2)는 월령(나이)별 발달 가이드.
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
