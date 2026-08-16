# IVK 현재 구현 구조 및 확장형 Value Chain Factory 검토

- 기준일: 2026-08-16
- 범위: 현재 IVK/IIKG/Neo4j 구현 실측, Order 127~140 진행 결과, 신규 Value Chain 대량 처리·토큰 경제·업종/Frame 확장 논의
- 목적: 현재 구현과 제안 구조를 분리하고, STI 수준 그래프를 반복 생산하기 위한 다음 개발 기준을 확정한다.

## 1. 결론

현재 시스템은 다음 두 부분까지 구현되어 있다.

1. STI 중심의 기존 투자 지식그래프와 시계열·재고·인과 assertion 기반
2. 신규 Value Chain 입력을 검증·정규화하고 기존 Neo4j를 조회하여 Blueprint JSON을 만드는 `Intake → Blueprint`

아직 구현되지 않은 핵심 구간은 다음이다.

```text
Blueprint
→ Source Plan
→ Source Collection
→ Evidence Extraction
→ Knowledge Engineering
→ Review/Approval
→ Neo4j Load
→ STI-level Completion Audit
```

따라서 현재 Order 140 프로세스만 실행해서는 STI 수준의 신규 Value Chain이 완성되지 않는다. 다만 현재 자산을 기반으로 위 구간을 Python 중심의 확장형 Factory로 연결하는 것은 가능하다.

## 2. 현재 Neo4j 실측

`neo4j-official.read_cypher`로 확인한 현재 live DB 상태는 다음과 같다.

| 항목 | 수량 |
|---|---:|
| 전체 노드 | 347 |
| 전체 관계 | 368 |
| Company | 11 |
| FinancialPeriod | 55 |
| InventorySnapshot | 56 |
| CausalAssertion | 3 |

Order 140의 신규 예제 seed `NVDA`, `COHR`, `LITE`, `CRDO`는 현재 Company 노드가 각각 0개다. 이는 Order 140에서 신규 Neo4j write를 명시적으로 금지했기 때문이며, 네 seed는 Blueprint의 `unresolved starting point`로만 보존되어 있다.

## 3. 현재 구현된 계층

### 3.1 STI/IVK v2 기반

Order 127~139에서 다음 기반이 구현·검증되었다.

- `fact`, `inference`, `hypothesis` 인식 상태
- `pending`, `accepted`, `rejected`, `deferred` 검토 상태
- CausalAssertion 및 ASSERTED_FOR
- 자동 확정 방지 규칙
- migration dry-run과 무결성 검사
- discovery/expansion loop 시범
- WinWay live pilot
- `neo4j-official.read_cypher` 및 승인형 `write_cypher`
- 동일 MERGE 재실행 시 count 불변인 멱등성 검증

주요 구현:

- `scripts/ivk_v2.py`
- `queries/127_ivk_v2_schema.cypher`
- `queries/132_sti_discovery_loop.cypher`
- `queries/133_winway_live_pilot.cypher`
- `data/127_causal_prototypes.json`
- `data/132_discovery_loop.json`
- `data/133_winway_live_pilot.json`

### 3.2 Order 140 Intake → Blueprint

구현 파일:

- `scripts/ivk_new_intake.py`
- `schemas/ivk_new_intake.schema.json`
- `schemas/ivk_blueprint.schema.json`
- `tests/test_ivk_new_intake.py`
- `examples/140_ai_optical_cpo_intake.json`
- `examples/140_ai_optical_cpo_graph.json`
- `artifacts/140_ai_optical_cpo_blueprint.json`
- `docs/ivk_new_intake_blueprint.md`
- `reports/140_report.md`

입력 계약:

| 구분 | 필드 |
|---|---|
| 필수 | `name`, `seed`, `frame`, `thesis` |
| 권장 | `questions` |
| 선택 | `known_links`, `limitations`, `references` |

현재 처리:

```text
원본 입력 보존
→ 필드·타입 검증
→ seed 정규화·중복 거부
→ primary/secondary frame 구성
→ neo4j-official canonical read snapshot 결합
→ review-gated Blueprint JSON 생성
```

안전 규칙:

- seed는 분석 경계가 아니라 출발점이다.
- 기존 graph observation과 미검증 hypothesis를 구분한다.
- `epistemic_policy.auto_confirm=false`를 강제한다.
- Blueprint의 최초 `review_status`는 `pending`이다.
- investment-kg API로 canonical Neo4j read를 대체하지 않는다.

## 4. 현재 미구현 또는 부분 구현

| 기능 | 상태 | 설명 |
|---|---|---|
| Intake/Normalize | 구현 | Order 140 |
| Existing Graph Check | 구현 | 공식 Neo4j read snapshot |
| Blueprint artifact | 구현 | `ivk-blueprint-1.0` |
| 자동 Source Plan | 미구현 | Blueprint 결손을 조사 과제로 변환 필요 |
| 지역별 자료 수집 | 분산 구현 | DART/TIKR/SEC/MOPS 등을 공통 IVK 인터페이스로 연결하지 않음 |
| Evidence Store | 미구현 | 문서 hash·section·추출 결과의 전역 재사용 필요 |
| 구조화 지식 추출 | 부분 구현 | STI 시범은 있으나 범용 pipeline 아님 |
| Frame별 추론 | 미구현 | 단일 공통 방식으로 처리 불가 |
| Sector별 KPI/taxonomy | 부분 구현 | 반도체 중심, Pack 구조 아님 |
| 승인 workflow | 부분 구현 | 상태 모델은 있으나 범용 review queue 부재 |
| 범용 Neo4j loader | 부분 구현 | 시범 Cypher 존재, Blueprint 소비형 loader 부재 |
| STI-level audit | 미구현 | completeness score와 자동 재작업 큐 필요 |
| Token ledger/budget gate | 미구현 | 단계별 비용 측정·중단 기준 필요 |

## 5. 단일 고정 파이프라인이 부적합한 이유

업종과 투자 Frame마다 핵심 질문·자료·지표가 다르다.

| 구분 | 대표 분석 축 |
|---|---|
| 반도체 | 공정, 장비, 소재, 수율, 가동률, 재공품, CAPEX |
| 바이오 | Drug, Target, 임상 단계, endpoint, 규제, cash runway |
| 전력/에너지 | 발전·송전 자산, 계통 연결, PPA, 수주, 허가 |
| 소비재 | 점포 매출, traffic, ticket, 판촉, 채널 재고, 브랜드 |

Frame도 서로 다르다.

- Sponsor → Value Chain → Bottleneck
- Demand → Capacity → Earnings
- Technology Transition → Replacement Cycle
- Regulation → Compliance → Beneficiary

Frame과 Sector를 하나의 템플릿으로 결합하면 조합 수가 폭발한다. 두 축을 독립 Pack으로 만들고 실행 시 조합해야 한다.

## 6. 권장 목표 구조

```text
IVK Core
 ├─ Frame Pack
 ├─ Sector Pack
 ├─ Region Pack
 ├─ Source Adapter
 ├─ Metric Pack
 ├─ Graph Mapping Pack
 └─ Validation Policy
```

### 6.1 고정 Core

경험이 쌓여도 다음은 공통으로 유지한다.

- Intake 계약과 정규화
- 원문·출처·기준일 보존
- fact/inference/hypothesis 구분
- evidence와 assertion 연결
- review 상태
- 중복·orphan·source 무결성 검사
- idempotent Neo4j 적재
- 실행 버전·토큰·비용 기록
- completeness audit

### 6.2 Frame Pack

Frame Pack은 필요한 슬롯, 질문 순서, 확장 순서, 중단 조건을 정의한다.

```yaml
id: sponsor_valuechain_bottleneck
version: 1.0.0
required_slots:
  - demand_driver
  - sponsor
  - system
  - process
  - component
  - bottleneck
  - beneficiary
stop_conditions:
  - unsupported_bottleneck
  - no_primary_source
```

### 6.3 Sector Pack

Sector Pack은 taxonomy, KPI, 재고·증설 해석, 허용 관계를 정의한다. 업종 특수 규칙은 Core 코드에 하드코딩하지 않는다.

### 6.4 Region Pack

- Korea: DART, 누적분기 역산, KRX 코드
- US: SEC/TIKR, 10-Q/10-K, earnings call
- Japan: 회계연도 라벨과 TSE 공시
- Taiwan: MOPS, 월별 매출, 월→분기 rollup

### 6.5 Source Adapter

Source Adapter는 접근·수집·메타데이터 정규화만 담당하고 투자 판단을 하지 않는다.

```text
DartAdapter / TikrAdapter / SecAdapter / MopsAdapter
CompanyIRAdapter / EarningsCallAdapter / TelegramResearchAdapter
```

## 7. Python과 LLM의 역할 경계

### Python 우선

- 입력·타입·ID 검증
- ticker·기간·통화·단위 정규화
- 기존 graph·cache 조회
- 문서 dedupe와 content hash
- 분기 계산, QoQ/YoY, 마진, 재고일수
- 관계 중복·무결성 검사
- Cypher 생성·MERGE·사전/사후 count
- 실행 이력·비용·버전 기록

### LLM 제한 사용

- 사업부·제품·공정 의미 해석
- 문서 근거의 구조화 추출
- Value Chain 후보와 인과 hypothesis 생성
- 상충 근거 요약
- 최종 투자 해석

LLM은 DB를 자유롭게 수정하지 않는다. 구조화 후보 JSON을 출력하고 Python validator와 review gate를 통과한 항목만 적재한다.

## 8. Token Economy 설계

Order 140 개발 세션은 누적 약 899,298토큰을 처리했으며 이 중 약 840,448토큰이 cached input이었다. 이는 Factory를 만드는 coding-agent 비용이며 Value Chain당 반복 운전비로 허용하면 안 된다.

목표 운전비:

| 단계 | 목표 토큰 |
|---|---:|
| Intake/Normalize/Graph read | 0 LLM token |
| Source Plan | 2천~5천 |
| Evidence Extraction | 1.5만~5만 |
| 관계·인과 합성 | 5천~1.5만 |
| 예외 검토 | 0~1만 |
| 최종 요약 | 2천~5천 |
| Value Chain 합계 | 약 2.5만~8.5만 |

핵심 절감 규칙:

1. 기업 공시를 Value Chain별로 다시 읽지 않고 Global Evidence Store에서 재사용한다.
2. 원문 전체가 아니라 Python 검색으로 선택한 관련 section만 LLM에 전달한다.
3. 계산·중복·적재는 Python이 수행한다.
4. 소형 모델이 후보를 만들고 고급 모델은 저신뢰·상충·중대 assertion만 검토한다.
5. 고정 Schema·정책은 prompt 앞부분에 두고 가변 evidence를 뒤에 배치해 cache를 활용한다.
6. 중간 결과는 장문이 아니라 JSON으로 제한한다.
7. 신규 문서와 변경된 section만 증분 처리한다.

권장 Token Ledger:

```json
{
  "run_id": "IVK-CPO-001",
  "value_chain_id": "vc:ai-optical-cpo",
  "stage": "evidence_extraction",
  "model": "configured-model",
  "input_tokens": 18200,
  "cached_input_tokens": 14300,
  "output_tokens": 2100,
  "documents_considered": 18,
  "documents_sent": 4,
  "facts_created": 27,
  "facts_accepted": 19,
  "retry_count": 0
}
```

관리 지표:

- accepted fact당 토큰/비용
- accepted relationship당 비용
- Company 1개 완성당 비용
- evidence 재사용률
- 고급 모델 escalation 비율
- completeness 1점당 비용

## 9. 경험 축적과 변경 관리

LLM이 실행 경험을 근거로 운영 규칙을 직접 수정하게 하지 않는다.

```text
실행 실패·수동 수정 기록
→ Improvement Proposal
→ Golden Example 회귀 실행
→ 품질·토큰 비교
→ 사람 승인
→ Pack 새 버전 발행
```

경험의 저장 단위는 프롬프트 문장 추가가 아니라 다음이어야 한다.

- Frame Pack 신규/개정
- Sector taxonomy 개정
- KPI 계산 규칙
- Source Adapter 개선
- Validation rule
- 실패 fixture
- Golden Example과 회귀 테스트

각 결과에 사용 버전을 기록한다.

```json
{
  "pipeline_version": "2.0.0",
  "frame_pack": "sponsor-valuechain-bottleneck@1.0.0",
  "sector_pack": "semiconductor-optical@1.0.0",
  "region_pack": "us@1.0.0",
  "graph_schema": "ivk-core@2.0.0",
  "extractor_version": "evidence-extractor@1.0.0"
}
```

## 10. STI 수준 완료 관문

노드 수가 아니라 완성도와 무결성으로 판정한다.

| 평가 영역 | 권장 기준 |
|---|---|
| Seed 해소 | 100% Company 식별 |
| 기업 기본정보 | 국가·거래소·ticker·표준 ID 완비 |
| 제품·공정 | 핵심 기업당 출처 있는 관계 1개 이상 |
| Driver/EndMarket | 핵심 기업 80% 이상 연결 |
| 분기 실적 | 최근 5분기 |
| 사업부 실적 | 공개 기업 전부 |
| 재고 | 총재고 5분기, 세부 재고는 공개 범위 |
| 증설 | 조사 기간 내 공개 투자 반영 |
| 출처 | 적재 사실·관계에 URL·기준일 |
| 인과 assertion | evidence·status·review 필수 |
| 무결성 | duplicate·orphan·wrong mapping 0 |
| 멱등성 | 동일 적재 2회 후 count 불변 |

예시 관문:

```text
completeness >= 85
AND critical_integrity_errors = 0
AND unresolved_required_seeds = 0
→ STI_LEVEL_READY
```

## 11. 권장 구현 순서

### Phase A — 범용 Factory 골격

1. Pack registry와 compatibility 계약
2. Global Evidence Store와 document/section hash
3. Blueprint → Source Plan
4. Token Ledger와 stage budget gate

### Phase B — STI 재현 Pack

1. `sponsor_valuechain_bottleneck` Frame Pack
2. `semiconductor_test_interface` Sector Pack
3. Korea/US/Japan/Taiwan Region Pack
4. 기존 STI를 Golden Example로 회귀 검증

### Phase C — 적재·완료 관문

1. Evidence Packet validator
2. review queue
3. idempotent Neo4j loader
4. STI-level completeness audit
5. 부족 항목만 재수집하는 remediation loop

### Phase D — 업종 확장

새 Frame/Sector는 Core 수정 없이 Pack 추가로 확장한다. Pack 승격 전 Golden Example에서 품질, 토큰, latency, 무결성을 비교한다.

## 12. 현재 판단

- 기술적 구현 가능성: 높음
- Order 140 단독으로 STI 수준 자동 구현: 불가
- 현재 자산을 재사용한 Factory 확장: 가능
- 우선순위: Source Plan보다 먼저 Pack 계약·Evidence Store·Token Ledger의 공통 골격을 확정
- 운영 원칙: `고정 Core + 조합 가능한 Pack + Source Adapter + Python deterministic pipeline + 예외만 LLM + 버전별 재현`

## 13. 저장소 상태 주의

본 문서 작성 시 working tree에는 IVK와 무관한 consumer stale-lock 복구 작업의 미커밋 변경 두 파일이 존재한다.

- `scripts/order_inbox_consumer.py`
- `tests/test_order_inbox_consumer.py`

이 변경은 본 IVK 구조 평가에서 제외했으며 삭제·초기화·커밋하지 않았다.
