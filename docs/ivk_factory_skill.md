# IVK Factory 공용 Skill — 2026-08-24

## Universal / Unique Enrichment

IVK의 모든 분석은 세 질문에 답해야 한다: 기업이 어떻게 돈을 버는가, 현재와 미래 상태가 어떠한가, 이를 확인하려면 무엇을 더 봐야 하는가. 회사 공통 사실은 `UniversalFact`, VC·Frame별 해석은 `UniqueAssertion`, 부족한 근거는 `EvidenceGap`으로 분리한다.

```powershell
python -m ivk prepare-enrichment `
  --input <intake.json> `
  --qa <enrichment-qa.json> `
  --output-dir <artifact-dir>
```

primary frame은 하나이며 secondary frame은 별도 view로 생성되어 primary 해석을 덮어쓰지 않는다. 자세한 계약, 출력물, 확장 규칙은 `docs/ivk_universal_unique_enrichment.md`를 따른다. `ENRICHMENT_PLANNED`는 수집·분석·Neo4j write 완료가 아니다.

## 목적

IVK(Investment Value-chain Knowledge Factory)는 `name`, `seed`, `frame`, `thesis`, `questions` 중심의 Intake를 재현 가능한 Blueprint, Evidence/KE 산출물, Neo4j write/read-back 결과로 변환한다. Python은 계약 검증·정규화·멱등성·상태 관리를 담당하고, agent/MCP는 원문 수집과 근거 기반 구조화를 담당한다.

## 절대 구분

`python -m ivk build`는 자동 리서치 명령이 아니다. 실행 전에 다음 실측 입력이 필요하다.

- `graph-results`: `neo4j-official.read_cypher` 결과
- `documents`: DART, TIKR, 거래소, 회사 IR, 어닝콜 등 원문과 provenance
- `structure`: Evidence에 연결된 Company/Product/Process/EndMarket/Driver/Assertion 후보

`build --execute-neo4j`는 이 입력을 검증·조립하고 MERGE write, 동일 배치 replay, live read-back까지 수행한다. 자료가 회사 개요뿐이면 결과도 회사 identity와 candidate membership에 그친다.

## Intake 식별자 계약

Intake에는 별도 `market` 필드를 넣지 않는다.

- 미국: `NVDA`, `FORM`
- 한국: `KR:131290|티에스이`
- 일본: `JP:6855|Japan Electronic Materials`
- 대만: `TW:6515|WinWay Technology`

숫자 ticker는 국가 prefix 없이 입력하면 reject한다. `KR:`, `JP:`, `TW:`는 국가 범위 canonical seed이며 거래소 약자가 아니다. 실제 KOSPI/KOSDAQ, TSE, TWSE/TPEX는 DART·거래소·TIKR·회사 원문에서 확인한다. 회사명은 숫자 ticker의 오식별을 막기 위해 `|회사명`으로 보존한다.

한국 기업은 DART와 회사 IR로 라우팅하며 TIKR를 사용하지 않는다. 일본은 TIKR/JPX/회사 IR/earning call, 대만은 TIKR/TWSE-TPEX/MOPS/회사 IR/monthly revenue를 사용한다. 미국은 TIKR/SEC/earning call 경로를 유지한다.

## Frame nickname

- `svb`: Sponsor → Value Chain → Bottleneck
- `matrix`: clustering된 기업 집합 비교
- `stream`: Upstream → Midstream → Downstream

nickname은 versioned frame pack으로 해석되며 관계나 기업을 자동 확정하지 않는다.

## 표준 실행

```powershell
python -m ivk validate --input <intake.json>

python -m ivk build `
  --input <intake.json> `
  --run-id <immutable-run-id> `
  --runs-dir runs `
  --graph-results <neo4j-read-result.json> `
  --documents <source-documents.json> `
  --structure <evidence-linked-structure.json> `
  --sector <sector-pack-or-bootstrap-name> `
  --execute-neo4j
```

`--region`은 선택이다. 생략하면 seed의 `US/KR/JP/TW`에서 필요한 region pack을 추론한다. 기존 VC 변경에는 `new`를 반복하지 않고 `add`, `update`, `expand`, `enrich`, `repair`, `review`를 목적에 맞게 사용한다.

## 상태와 품질 등급

- `PLANNED`: Blueprint와 Source Plan 준비
- `BATCH_READY`: write batch 준비, DB write 미실행
- `WRITE_CONFIRMED`: 실제 receipt 확인
- `VERIFIED`: live write, replay, read-back을 통과한 구조적 E2E 상태
- `STI_70_TARGET`: STI Golden Reference 대비 정의된 coverage benchmark를 통과한 목표 등급
- `STI_GRADE`: 5분기 재무, 사업부, 재고, CAPEX, provenance, 검토된 causal/link-expansion을 포함한 별도 품질 gate

`VERIFIED`는 STI 70%나 STI-grade를 뜻하지 않는다. “Intake JSON만 넣고 build하면 STI 70%”라고 보고하지 않는다. 충분한 원문 수집과 evidence-linked structure, enrichment, benchmark가 준비된 경우에만 70% 목표를 평가할 수 있다. 점수 또는 축별 coverage artifact 없이 퍼센트를 주장하지 않는다.

## STI 70% 목표의 최소 전제

- 기업 identity와 Value Chain membership
- 주요 제품·공정·기술·End Market
- 최근 5분기 재무
- 사업부 실적
- 재고 및 CAPEX
- 모든 수치·관계의 provenance
- Driver/Bottleneck/Beneficiary 후보와 counter-evidence/falsifier
- Link Expansion 재검토
- Neo4j write/replay/read-back
- STI 동일 rubric의 benchmark artifact

누락된 항목은 `blocked-with-reason`으로 남기며, inference/hypothesis를 confirmed로 자동 승격하지 않는다.

## Neo4j identity 규칙

Existing Graph Check는 반드시 `neo4j-official.read_cypher`를 canonical path로 사용한다. 기존 Company가 있으면 legacy ID를 재사용한다. 신규 비미국 Company는 국가 범위 ID를 사용한다.

- 기존 티에스이: `company:tse`
- 신규 한국 예: `company:kr:131970`
- 신규 일본 예: `company:jp:<ticker>`
- 신규 대만 예: `company:tw:<ticker>`

Company에는 `security_id`, ticker, country, 실제 exchange, local/English name, provider/provider ID를 저장한다. Evidence·Product·Process 관계는 ticker 문자열을 조립하지 않고 해석된 Company ID를 사용한다.

## 2026-08-24 실측 기준

- focused tests: 39/39 PASS
- KR 기존 ID 재사용: `company:tse`, duplicate-free replay PASS
- JP 기존 ID 재사용: `company:jem`, duplicate-free replay PASS
- TW 기존 ID 재사용: `company:winway`, duplicate-free replay PASS
- KR 신규 생성: 두산테스나·코미코·미코·네패스아크, 각 `company:kr:<ticker>`, duplicate-free replay PASS
- `intakes/new/kr_후공정.json`: structural `VERIFIED`; 5개 Company와 DART Evidence 5개 적재
- `semiconductor_backend`: 아직 reusable sector pack이 없어 bootstrap 사용

따라서 다국가 identity/write 경로는 KR 신규 생성과 KR/JP/TW 기존 노드 재사용까지 실측됐다. JP/TW 신규 Company 생성과 STI 70% 자동 source/enrichment 경로는 아직 release gate 전이다.

## Agent 완료 보고 규칙

완료 보고에는 Run-ID, 입력과 source artifact, pack selection, write receipt, read-back, duplicate/replay 결과, 질문 closure, 품질 등급, 미충족 gate를 포함한다. `VERIFIED`와 분석 품질을 혼용하지 않는다. 비밀정보를 Intake·Run·Git·Slack에 저장하지 않는다.

## 정본 문서

- `docs/ivk_factory_skill.md`
- `docs/ivk_build_cli.md`
- `docs/ivk_new_intake_blueprint.md`
- `docs/ivk_multi_market_build_verification.md`
- `docs/ivk_universal_unique_enrichment.md`
- `schemas/ivk_*.schema.json`
- `registry/ivk_factory_packs.json`
