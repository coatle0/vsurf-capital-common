# IVK Universal / Unique Enrichment Contract

## 목적

IVK는 기업 목록을 저장하는 그래프가 아니라 투자자가 각 기업에 대해 다음 세 질문에 반복 가능하게 답하도록 만드는 시스템이다.

1. 이 기업은 어떻게 돈을 버는가?
2. 지금의 상태와 미래의 상태는 어떠한가?
3. 그 상태를 확인하기 위해 무엇을 더 봐야 하는가?

이 계약은 사실을 여러 Value Chain이 공유하는 `Universal` 층과, 특정 Value Chain 및 Frame에서 사실을 해석하는 `Unique` 층으로 분리한다. 확인되지 않은 내용을 사실로 승격하지 않으며, 부족한 근거는 `EvidenceGap`으로 되돌린다.

## 기본 구조

```text
Intake
  -> Frame resolve
  -> Enrichment Q&A
  -> Analysis Contract
       |-> Universal Plan -> UniversalFact
       |-> Unique Plan    -> UniqueAssertion
       `-> Evidence Gaps  -> source task -> 재검증
```

### Universal

회사에 귀속되고 다른 Value Chain에서도 재사용할 수 있는 관찰 사실이다. 예: 제품, 고객·시장 노출, 최근 5분기 실적, 사업부 실적, 재고, CAPEX, 수주, 공시 발언과 provenance. `vc_role`, 수혜 순위, 투자등급, frame position은 Universal에 넣지 않는다.

### Unique

특정 Value Chain과 Frame에서 Universal Fact를 해석한 결과다. 모든 `UniqueAssertion`은 `value_chain_id`, `frame_id`, `question_id`, 참조한 `UniversalFact` ID, 근거·반증·falsifier, epistemic/review status를 가져야 한다. shared fact를 복사하거나 수정하지 않는다.

### EvidenceGap

세 질문에 답하기 위해 아직 부족한 사실 또는 출처다. shared Universal coverage를 먼저 확인한 뒤에만 수집 작업을 만들며, gap이 닫히면 영향을 받는 Unique assertion을 재검증한다.

## Frame 적용 방식

Value Chain마다 primary frame 하나를 지정한다. secondary frame은 별도 보조 뷰로 생성하며 primary 해석을 덮어쓰지 않는다.

- `matrix`: 군집 기업 비교, 차별화, 상대적 위치와 순위
- `stream`: upstream-midstream-downstream 흐름, handoff, 충격 전파
- `svb`: Sponsor-Demand-Bottleneck-Beneficiary 인과와 수혜 경로

Frame pack은 세 투자 질문별 하위 질문, 필요한 Universal 항목, 생성할 Unique 출력, 허용 관계, 확장 지점을 선언한다. secondary frame을 요청하면 그 frame에 필요한 Universal 항목도 coverage plan에 합쳐지고, 출력은 `secondary_view_plans`에 격리된다.

## 실행

입력은 기존 Intake와 별도 Enrichment Q&A다.

```powershell
python -m ivk prepare-enrichment `
  --input intakes/new/kr_후공정.json `
  --qa examples/kr_backend_enrichment_qa.json `
  --output-dir artifacts/enrichment/kr_backend_v01
```

출력은 다음 네 machine-readable artifact다.

- `analysis_contract.json`: 세 질문, primary/secondary frame, gate, 확장 계약
- `universal_plan.json`: 회사별 공유 사실 coverage 요구
- `unique_plan.json`: primary 해석과 격리된 secondary view 계획
- `evidence_gaps.json`: coverage 확인 및 후속 source task 후보

`ENRICHMENT_PLANNED`는 분석 계획이 생성됐다는 뜻이다. 자료 수집, Universal write, Unique 확정, Neo4j write 또는 STI-grade를 뜻하지 않는다.

## 전체 처리 Process

1. Intake validation 및 ticker/company identity 정규화
2. primary/secondary Frame pack resolve
3. Enrichment Q&A validation
4. 세 투자 질문 기반 Analysis Contract 생성
5. 기존 shared Universal coverage 조회
6. 부족한 항목만 EvidenceGap 및 source task로 전환
7. 출처 정규화 후 UniversalFact 적재
8. Frame 규칙으로 UniqueAssertion 후보 생성
9. 근거·반증·falsifier 검토 후 승인 또는 보류
10. Neo4j write/read-back, benchmark, gap 재검증

현재 구현 범위는 1~4와 5~6의 실행 계획 생성이다. 5의 실제 조회 resolver, 6~10의 executor/write/revalidation은 다음 구현 단계다.

## 확장 Point

- Frame: 새 분석 렌즈를 versioned pack으로 추가
- Sector: 여러 VC에서 반복 검증된 요구만 공용 sector pack으로 승격
- Source adapter: DART/TIKR/거래소/IR/월매출 등 시장별 수집기를 계약 변경 없이 연결
- Quality gate: STI-grade 등 benchmark 축을 버전 관리
- Secondary view: primary를 보존한 채 추가 frame 해석 생성
- Question extension: 세 핵심 질문은 고정하고 VC별 보조 질문만 추가
- Relationship extension: 허용 관계를 pack/Q&A에 명시하고 임의 관계 생성을 금지

확장 시 기존 artifact를 덮어쓰지 않고 contract/pack version과 Run-ID로 재현성을 유지한다.
