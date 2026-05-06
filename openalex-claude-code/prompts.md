# OpenAlex × Claude Code — 프롬프트 라이브러리

> 복사해서 토픽·DOI·ORCID만 바꾸면 바로 쓰는 프롬프트 모음.
> Companion to `index.html` (OpenAlex × Claude Code 가이드북, 2026-05-05).
> 모든 프롬프트는 `openalex_helper.py`가 같은 폴더 또는 프로젝트 `scripts/`에 있다고 가정합니다.

---

## 1. 워밍업 — "지금 작동하나?"

### 1.1 헬퍼 sanity check
```
openalex_helper.py를 사용해서 DOI 10.1038/nature12373을 lookup해줘.
title, publication_year, cited_by_count, primary_location.source.display_name만 보여줘.
```

### 1.2 단일 검색
```
openalex_helper.py search "AI literacy K-12" --year-min 2023 --min-citations 30 --per-page 10
을 실행하고 결과를 표로 정리.
```

---

## 2. 저자 (Authors)

### 2.1 ORCID로 전체 이력
```
ORCID 0000-0001-2345-6789의 모든 OpenAlex works를 author-works 명령으로
data/<lastname>_works.jsonl로 저장. 마지막에 총 출판수와 누적 인용수를 보고.
```

### 2.2 토픽 드리프트 (5년 단위)
```
data/<lastname>_works.jsonl을 읽어서 publication_year를 5년 윈도우로 나누고
(2010-14, 2015-19, 2020-24), 각 윈도우의 top-5 topics를 산출.
변화량이 큰 토픽 (rank shift ≥ 3)을 별도 표로.
```

### 2.3 동명이인 검증
```
"Jewoong Moon"으로 OpenAlex authors 검색해서 candidates 리스트.
각 candidate의 ORCID, last_known_institutions, works_count, top-3 topics를 표로 나란히 보여줘.
어느 ID가 진짜 본인인지 confirm 받기 전에는 author-works를 부르지 마.
```

### 2.4 협력 네트워크
```
ORCID 0000-... 의 works 중 co-author가 한 번 이상 등장한 사람들의
{co_author_orcid, co_author_name, count, first_year, last_year} 표.
count 내림차순.
```

---

## 3. 인용 그래프 (Citation Graph)

### 3.1 "이 논문 인용한 최근 N편"
```
DOI 10.1080/10508406.2020.1782269를 cited-by --max 200으로 가져와서
publication_year >= 2024인 것만 필터, cited_by_count 내림차순 표.
```

### 3.2 Forward citation chain (1-hop)
```
시드 DOI 10.xxx/yyy의 cited_by 결과 중 본인이 다시 5회 이상 인용된 것들 추리고,
각각의 cited_by를 또 가져와서 2-hop forward 그래프를 edge list로 만들어 data/forward_chain.csv.
중간에 진행 상황 출력. 노드가 1000개 넘으면 멈추고 보고.
```

### 3.3 Co-citation
```
시드 두 논문 (DOI A, DOI B)의 cited_by 결과를 각각 가져와서 교집합 추출.
"두 논문을 모두 인용한 후속 논문" 리스트를 표로.
```

### 3.4 Bibliographic coupling
```
시드 두 논문 (DOI A, DOI B)의 referenced_works (각자의 reference list) 교집합.
"공통으로 인용한 선행 연구" 리스트.
```

### 3.5 Reference network of a paper
```
DOI 10.xxx/yyy의 referenced_works 모두 가져와서 (각각의 메타데이터 lookup)
저자/저널/연도 분포를 산출. 어느 분야·시기에 뿌리를 두고 있는지 한 단락 요약.
```

---

## 4. 저널·소스 (Sources)

### 4.1 ISSN → source_id
```
다음 ISSN들의 OpenAlex source_id를 find_source_by_issn로 매핑해서 data/sources.json:
- 1050-8406 (Journal of the Learning Sciences)
- 0737-0008 (Cognition and Instruction)
- 0360-1315 (Computers & Education)
- 0007-1013 (British Journal of Educational Technology)
- 1042-1629 (Educational Technology Research and Development)
```

### 4.2 저널 전체 history
```
source_id S206377884의 모든 works 2015–2025를 paginate해서
(select: id,doi,title,publication_year,cited_by_count,topics,authorships)
data/jls_works.jsonl로. 진행률 매 500건마다 출력.
```

### 4.3 Cross-journal citation matrix
```
data/sources.json의 5개 source에 대해 각 저널 works의 referenced_works를 모아서
to_source가 우리 5개 안에 있는 것만 필터.
5×5 인용 매트릭스를 publication_year 3년 윈도우로 (2015-17, 18-20, 21-23, 24-25)
data/citation_matrix_<window>.csv 4개 파일로 저장.
```

### 4.4 저널의 토픽 변화
```
source_id S206377884의 works를 5년 윈도우로 나누고 각 윈도우 top-10 topics + share.
변화 패턴을 한 단락으로 narrate.
```

---

## 5. 토픽·랜드스케이프

### 5.1 토픽 트렌드 스냅샷
```
OpenAlex topic T10119 (educational technology)의 works를
group_by=publication_year로 2015-2025 집계. 연도별 출판량, 평균 인용수, OA 비율.
matplotlib으로 line plot.
```

### 5.2 신규 토픽 후보 발굴
```
"generative AI education"으로 search, 2024-2025만 필터, cited_by_count >= 10.
결과 50건의 topics 필드를 모아서 빈도수 상위 토픽 ID·이름·빈도수 표.
기존에 잘 알려진 토픽 vs. 새로 떠오르는 토픽을 분리해서 정리.
```

### 5.3 국가별 출판 점유율
```
topic T10119의 2024 works 중 authorships.institutions.country_code 분포.
top-15 국가 횡-막대 그래프 + 한국의 순위·점유율 별도 강조.
```

### 5.4 펀더 프로파일
```
funder F4320332161 (NSF)이 펀딩한 works를 paginate (max 5000), 
연도별 출판량 + 토픽 분포 + top-10 그랜트 수령 institutions.
```

---

## 6. 리뷰·메타분석 자동화

### 6.1 신간 알림 (지난 30일)
```
search "AI literacy" + 지난 30일 publication_date인 works.
마크다운 리스트로 정리하고 wiki/sources/AI Literacy Watch.md에 today's date 헤더와 함께 append.
```

### 6.2 메타분석 프리스크리닝
```
search "VR safety training civil engineering" + 2018 이후 + cited_by_count >= 5.
Title + abstract에 RCT/randomized/quasi-experimental 키워드 포함된 것만 남겨서
data/meta_candidates.csv (DOI, title, year, design_keyword, citations).
Zotero import 호환 형식으로.
```

### 6.3 systematic review의 PRISMA 카운트
```
search "<topic>" + year_min 2015. 결과 총 count 보고.
이어서 + filter type:journal-article로 좁힌 후 count.
이어서 + filter is_oa:true로 좁힌 후 count.
PRISMA flow에 들어갈 숫자 단계별로 정리.
```

---

## 7. Discourse Lens v2 (케이스 스터디 본 시퀀스)

> 이 5개 프롬프트는 가이드북 § 6에서 자세히 다룹니다. 여기는 빠른 참조용.

### v2-1. 저널 ID 매핑
```
openalex_helper.py를 사용해서 다음 저널의 source_id를 ISSN으로 lookup,
data/sources.json으로 저장:
- 1050-8406, 0737-0008, 0360-1315, 0007-1013, 1042-1629
```

### v2-2. 저널별 전체 works
```
위 5개 source_id에 대해 publication_year:2015-2025로 paginate, 
select=id,doi,title,publication_year,primary_location,referenced_works로 좁혀
data/works.jsonl. 매 500건 진행률.
```

### v2-3. Cross-source 엣지
```
data/works.jsonl을 스트리밍으로 읽어서 referenced_works 중 우리 5개 source 안에 있는 것만 추출,
data/citation_edges.csv (from_work_id, from_source, from_year, to_work_id, to_source, to_year).
```

### v2-4. 분석
```
citation_edges.csv를 3년 윈도우로 4개 매트릭스로 만들고,
LS 저널군 (JLS, C&I) ↔ ET 저널군 (C&E, BJET, ETR&D)의 cross-citation 비대칭성을 t-test.
results/asymmetry.md.
```

### v2-5. 시각화 (R)
```
viz.R로 ggplot2 + ggalluvial 이용 4-panel sankey/chord, 학술 백색 배경,
EarlyTeacherEd 스토리피겨 스타일. figures/v2_cross_citation.png.
```

---

## 8. 디버깅·검증 프롬프트

### 8.1 결과 sanity check
```
방금 받은 100건 중 publication_year가 None인 것, doi가 None인 것 카운트.
각 카테고리의 해당 work id 처음 5개를 보여줘 — OpenAlex 메타데이터 누락 패턴 확인용.
```

### 8.2 동일 검색 재현
```
정확히 같은 검색을 어제 날짜로도 한 번 돌려서 결과 수와 top-10 ID set의 차이를 보고.
변동이 있으면 어떤 work가 새로 들어오고 어떤 게 빠졌는지.
```

### 8.3 인용수 변화 추적
```
data/works.jsonl과 data/works_2026-04-01.jsonl 두 스냅샷에서 같은 work_id의 cited_by_count 차이.
가장 많이 늘어난 top-20을 표로.
```

---

## 9. 프롬프트 작성 팁

1. **단계별로 끊기.** 한 프롬프트 = 한 단계. 5단계를 한 번에 시키지 말 것.
2. **중간 산출물 명시.** "data/sources.json으로 저장" 같이 출력 경로를 적으면 Claude가 다음 단계에서 그 파일을 다시 읽음.
3. **카디널리티 미리 알려주기.** "100건+", "1만 건+" 같이 규모를 알려주면 Claude가 paginate 함수를 부름.
4. **select로 토큰 절약.** "id, title, year만 select" 명시 — raw JSON 전체를 LLM에 던지지 않음.
5. **검증 단계 기본 포함.** "총 count 보고", "처음 5개 sample 출력" 같은 sanity check를 항상.
6. **Polite pool 가정.** 이 가이드의 헬퍼는 자동으로 mailto 추가. 직접 URL 쓰는 경우만 명시적으로 추가.

---

## 10. 한 줄 요약 — "프롬프트 = 데이터 흐름"

좋은 OpenAlex 프롬프트는 **요청 → 입력 데이터 → 호출 → 출력 경로 → 검증**을 한 문장 안에 담습니다.
나쁜 프롬프트는 "이 토픽 좀 정리해줘" 같이 흐름이 빠진 것.
가이드북 § 5의 5단계 깔때기를 머릿속에서 한 번 돌리고 프롬프트를 쓰면 90% 작품질이 보장됩니다.
