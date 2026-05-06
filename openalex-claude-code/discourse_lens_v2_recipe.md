# Discourse Lens v2 — Cross-Citation Layer Recipe

> 이 가이드북의 케이스 스터디 워크스루 풀버전.
> 가이드북 § 6의 5-프롬프트 시퀀스를 한 호흡으로 따라가면서 예상 산출물·실패 케이스·확장 아이디어까지 다룹니다.

---

## 0. 컨텍스트 — v1이 한 일, v2가 묻는 것

### v1 (2026-04-29 MVP)
- **데이터**: Learning Sciences (LS) ↔ Educational Technology (ET) 저널의 abstract 2015–2025
- **분석**: BERTopic 클러스터링, LLM-tagged discourse threads
- **결론**: 두 분야가 다루는 주제 클러스터 지도

### v2의 새 RQ
> "두 분야가 같은 토픽을 다룰 때, 그들은 서로의 연구를 얼마나 / 어떻게 인용하나? 시간이 지나며 그 관계가 변했나?"

이 질문은 v1 데이터로는 답할 수 없습니다. **인용 그래프 layer**가 필요해요. OpenAlex가 정확히 이걸 제공합니다.

---

## 1. 데이터 shape 설계 — 종이에 먼저 그리기

```
[Source × Source × Year-window × Citation_count]

   FROM \  TO     JLS     C&I    C&E    BJET   ETR&D
   ──────────────────────────────────────────────────
   JLS                                                ← LS group
   C&I                                                ← LS group
   C&E                                                ← ET group
   BJET                                               ← ET group
   ETR&D                                              ← ET group
```

이 5×5 매트릭스를 4개 시간 윈도우 (2015-17, 18-20, 21-23, 24-25)로 만들면 v2 분석의 본체.

**핵심 가설**: ET → LS 인용 / LS → ET 인용 비율의 비대칭성. ET가 LS를 더 많이 인용하지만 (이론 차용), LS는 ET를 덜 인용한다 (분야 위계). 시간이 지나며 이 비대칭이 줄어드는가?

---

## 2. 5-프롬프트 build-along

### 프롬프트 1: 저널 ID 매핑

```
openalex_helper.py의 find_source_by_issn를 사용해 다음 저널의 OpenAlex source_id를 lookup해서
data/sources.json으로 저장:

- Journal of the Learning Sciences (1050-8406)
- Cognition and Instruction (0737-0008)
- Computers & Education (0360-1315)
- British Journal of Educational Technology (0007-1013)
- Educational Technology Research and Development (1042-1629)

JSON 구조: {"<journal_short_name>": {"issn": "...", "source_id": "S...", 
"display_name": "...", "group": "LS" | "ET"}}
```

**예상 산출물 `data/sources.json`** (값은 실제 OpenAlex가 반환하는 ID):
```json
{
  "JLS":   {"issn": "1050-8406", "source_id": "S206377884", "display_name": "Journal of the Learning Sciences", "group": "LS"},
  "C&I":   {"issn": "0737-0008", "source_id": "S...",       "display_name": "Cognition and Instruction",       "group": "LS"},
  "C&E":   {"issn": "0360-1315", "source_id": "S...",       "display_name": "Computers & Education",            "group": "ET"},
  "BJET":  {"issn": "0007-1013", "source_id": "S...",       "display_name": "British Journal of Educational Technology", "group": "ET"},
  "ETR&D": {"issn": "1042-1629", "source_id": "S...",       "display_name": "Educational Technology Research and Development", "group": "ET"}
}
```

**검수 포인트**:
- 5개 모두 `source_id`가 채워졌는가
- `display_name`이 우리가 의도한 저널이 맞는가 (다른 같은 ISSN 저널 헷갈림 방지)
- 만약 누락이 있다면 ISSN 오타이거나 OpenAlex가 e-ISSN으로 매핑한 것 — 둘 다 시도

---

### 프롬프트 2: 저널별 전체 works

```
data/sources.json을 읽어서 5개 source_id에 대해 publication_year:2015-2025 범위로
openalex_helper.py paginate를 호출해 각 저널의 모든 works를 data/works.jsonl로 append.

select 파라미터로 다음 필드만 가져와 (토큰 절약):
id, doi, title, publication_year, primary_location, referenced_works, type

매 저널 시작 전 [START journal] 출력, 끝나면 [DONE journal: N records] 출력.
최종 총 record 수 보고.
```

**예상 산출물 `data/works.jsonl`**: 한 줄 한 work, 약 5,000–8,000 records 예상 (저널마다 연 100–500편 범위).

**자주 나는 실패**:
- `referenced_works`가 빈 배열인 work들이 보임 → OpenAlex가 reference를 추출 못한 case (특히 비-Crossref 저널). **drop하지 말고** 전체 카운트만 별도로 보고하라고 지시.
- 페이지네이션 도중 timeout → `openalex_helper.py`의 retry/backoff가 처리. 그래도 막히면 `--max`를 줄여서 분할.

---

### 프롬프트 3: Cross-source 엣지 추출

```
data/works.jsonl을 한 줄씩 스트리밍으로 읽어서, 각 work의 referenced_works 중
우리 5개 source 중 하나에 속한 것만 필터해서 cross-source citation edges 생성.

이걸 위해 prerequisite 단계: data/works.jsonl의 모든 work_id → source_id 매핑을 메모리 dict로.

출력: data/citation_edges.csv with columns:
from_work_id, from_source, from_group, from_year, 
to_work_id, to_source, to_group, to_year

OpenAlex의 referenced_works는 OpenAlex Work URL 형식이므로 W... ID만 추출.
```

**예상 산출물 `data/citation_edges.csv`**: 약 30,000–80,000 행 예상 (work × 평균 reference × in-set 비율).

**핵심 검수**:
- self-source citation (예: JLS → JLS) 도 포함되어 있는가? 둘 다 분석에 의미 — cross-group 비대칭성을 보려면 필요.
- to_year > from_year 같은 어색한 행이 있는가? OpenAlex 메타데이터 오류일 수 있음 — 카운트만 보고.

---

### 프롬프트 4: 분석 — 비대칭성 검정

```
data/citation_edges.csv을 pandas로 읽어서:

1. 4개 시간 윈도우 (from_year 기준): 2015-17, 18-20, 21-23, 24-25.
2. 각 윈도우마다 group 단위 (LS, ET) 4가지 cross-citation 비율을 계산:
   - LS → LS (within-LS)
   - LS → ET (LS cites ET)
   - ET → LS (ET cites LS)
   - ET → ET (within-ET)
   각 from-work 당 그 work의 referenced_works 중 to_group 분포의 평균.
3. LS → ET 평균 비율 vs ET → LS 평균 비율의 차이를 윈도우마다 t-test (Welch's).
4. 출력 results/asymmetry.md:
   - 4개 윈도우의 4×4 비율 표
   - 윈도우별 비대칭성 t-test 결과 (mean diff, 95% CI, p)
   - 한 단락 narrate: 비대칭성이 시간에 따라 줄어드나/늘어나나/유지되나
```

**예상 패턴 (가설일 뿐)**:
- 2015-17: ET → LS 비율이 LS → ET보다 유의미하게 높음 (분야 위계)
- 2024-25: 차이 축소 (분야 통합 가속화 가설)

**주의**: 이건 가설입니다. 실제 데이터가 다른 패턴을 보이면 그게 더 흥미로운 finding — Claude에게 "예상과 다르면 그 패턴을 그대로 보고하라"고 명시하세요.

---

### 프롬프트 5: 시각화 (R)

```
viz.R 작성. data/citation_edges.csv을 읽어서:

- ggplot2 + ggalluvial 또는 ggraph 사용
- 4개 시간 윈도우를 patchwork::wrap_plots로 2×2 패널
- 각 패널: 5개 source를 좌우로, sankey/chord 스타일로 cross-citation flow
- LS 그룹 노드는 따뜻한 색 (#DC2626 계열), ET 그룹은 차가운 색 (#1D4ED8 계열)
- 학술 백색 배경, EarlyTeacherEd 스토리피겨 스타일 (theme_minimal + Source Serif Pro 헤딩, plot.title.position="plot")

출력: figures/v2_cross_citation.png (2400×1800px @ 300dpi)

renderer: C:\Program Files\R\R-4.5.2\bin\Rscript.exe viz.R
```

**Render 검증**:
- 노드 라벨이 잘리지 않는가
- 4개 패널의 색 스케일이 공유되는가 (legend 한 번만)
- 시간 윈도우 제목이 명확한가

---

## 3. 자주 막히는 지점 (Troubleshooting)

| 증상 | 원인 | 해결 |
|---|---|---|
| `find_source_by_issn` 가 None 반환 | OpenAlex가 다른 ISSN 형식으로 인덱싱 | print-ISSN과 e-ISSN 둘 다 시도; 또는 search로 우회 |
| `paginate` 가 첫 페이지 후 멈춤 | next_cursor가 None 반환 (실제 결과 < per_page) | 정상. 작은 결과셋. |
| `referenced_works` 가 모두 빈 배열 | OpenAlex가 그 저널의 reference 추출 못함 | 다른 저널과 비교해 % 계산; 분석에서 분모 조정 |
| 인용 매트릭스 row sum이 0 | from_year 윈도우에 해당 source의 work이 없음 | 윈도우 폭을 늘리거나 (5년 단위) NA로 표시 |
| t-test가 모든 윈도우에서 비유의 | sample이 작거나 분산이 큼 | bootstrap 95% CI로 보고; effect size (Cohen's d)도 |

---

## 4. v2 확장 아이디어

이 5-프롬프트가 끝났다면 다음을 추가로 짤 수 있습니다.

### 4.1 토픽 × 인용 결합
```
각 cross-citation edge에 to_work의 topics를 enrich.
"LS → ET 인용은 어떤 토픽에 집중되나?" — 분야 간 가교 토픽 발굴.
```

### 4.2 저자 단위 분석
```
edges에 from_work, to_work의 authorships 합쳐서 author × author cross-citation.
"두 분야를 가장 많이 잇는 저자 (broker)" 식별 → 협력 네트워크 후보.
```

### 4.3 신간 alert
```
지난 30일 LS 저널 신간 + ET 저널 신간 모니터링,
ET → LS 인용이 드문 케이스를 자동 highlight (broker 후보).
주간 메일 / wiki/sources/Discourse Lens Watch.md.
```

### 4.4 Discourse Lens UI 통합
```
v1의 D3 시각화 옆에 v2 인용 매트릭스 패널 추가.
한 토픽 클러스터를 hover하면 그 클러스터에 속한 work들 사이의 cross-citation flow가 강조.
```

---

## 5. 데이터 보관 룰

- `data/works.jsonl`, `data/citation_edges.csv` 등 원시 데이터 → **vault에 넣지 말 것**. 프로젝트 폴더 또는 `Desktop\_research\` 안에서만.
- `results/asymmetry.md`, `figures/*.png` 같은 정제 산출물 → **Discourse Lens 저장소 README나 wiki/sources/Discourse Lens v2 Notes.md에 cite**.
- vault entity page `wiki/entities/Discourse Lens.md`에 "v2 OpenAlex citation layer (2026-05-05~)" 섹션 추가.

---

## 6. 한 페이지 요약

```
RQ        : LS↔ET cross-citation의 시간적 변화
Shape     : Source × Source × Year-window × Count
Tools     : openalex_helper.py + pandas + ggplot2/ggalluvial
Sequence  : sources → works → edges → matrix → viz
Output    : results/asymmetry.md + figures/v2_cross_citation.png
Time      : 첫 실행 ~30분 (그 중 paginate 20분), 재실행 < 5분 (cache)
Cost      : $0 (OpenAlex 무료, polite pool)
```
