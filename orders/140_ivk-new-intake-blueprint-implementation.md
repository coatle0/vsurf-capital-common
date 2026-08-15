발행일: 2026-08-16
발신: COO (via ORDER 100 intake)
수신: codex
상태: 진행 중
도구: 없음

---

번호: 140
제목: ivk-new-intake-blueprint-implementation
목적: Order 139 closure PASS 이후 Phase 1의 다음 단계로, 사용자가 `IVK NEW` 형식으로 신규 Value Chain의 name/seed/frame/thesis/questions 등을 입력하면 이를 검증·정규화하고 existing graph를 확인한 뒤 재현 가능한 Blueprint로 변환하는 Intake→Blueprint 단계를 구현·검증한다. 이번 Order는 Source Collection/Knowledge Engineering/Neo4j 신규 write까지 확장하지 않는다.
대상: IVK_HANDOVER_2026-08-15.md의 §4 IVK NEW 입력 표준, §5 표준 E2E Process, 현재 IVK/IIKG/Neo4j 관련 코드·schema·validator, live Neo4j canonical read path, Order 139 PASS 상태.
작업:
1. Governance/preflight와 clean working tree를 확인하고 Order 139가 RESOLVED/PASS 상태임을 reports/139_report.md 및 최신 Git 상태로 확인한다.
2. Handover의 IVK NEW 최소 입력/Intake 필드를 구현한다: 필수 `name`, `seed`, `frame`, `thesis`; 권장 `questions`; 선택 `known_links`, `limitations`, `references`.
3. Intake Schema와 parser/validator를 정의한다. 필수값 누락, 빈 seed, 중복 seed, 잘못된 field type을 명시적으로 reject하며 원본 사용자 입력과 normalized output을 모두 보존한다.
4. Normalize 단계를 구현한다. ticker/company ID 정규화, seed dedupe, canonical seed list 생성, primary frame 지정 및 필요한 경우 secondary frame 후보를 별도 필드로 둔다. Seed는 경계가 아니라 출발점임을 schema/logic에 반영한다.
5. Existing Graph Check를 live `neo4j-official.read_cypher` 기준으로 구현한다. 각 seed/company에 대해 existing company node, 기존 product/process/technology/end-market 관계, 기존 evidence/assertion 존재 여부를 읽고 Blueprint에 `existing_graph` 또는 동등 구조로 포함한다. graph-related investment-kg API로 canonical read를 대체하지 않는다.
6. Blueprint Schema를 정의한다. 최소한 normalized identity, validated seeds, unresolved/excluded seed 후보와 사유, primary/secondary frame, thesis, questions, known links, existing graph findings, initial value-chain structure, initial Driver/Bottleneck/Beneficiary 후보 슬롯, Link Expansion frontier 슬롯, source requirements, epistemic/review 상태 슬롯을 포함한다.
7. Blueprint 단계에서는 후보를 'confirmed'로 자동 승격하지 않는다. 명시 사실/기존 graph observation과 아직 evidence가 필요한 inference/hypothesis를 구분할 수 있는 상태 필드를 둔다.
8. 실제 입력 예제로 parser→normalize→existing graph check→blueprint를 end-to-end 실행한다. 기존 STI/WinWay 자체를 재사용하지 말고, 신규 Value Chain onboarding 예제로 Handover의 `AI Optical / CPO` 입력 또는 동등한 신규 테스트 fixture를 사용한다: seed NVDA, COHR, LITE, CRDO; frame Sponsor→Value Chain→Bottleneck; optical/CPO 확대 thesis와 bottleneck/beneficiary/expansion questions.
9. 정상 입력 최소 1건과 negative validation case들을 테스트한다. 최소: missing required field, duplicate seed, empty seed, malformed type. 정상 예제에서 normalized seed dedupe, existing graph check 결과, Blueprint 필드 completeness를 검증한다.
10. 다음 단계인 Knowledge Engineering이 이 Blueprint를 직접 소비할 수 있도록 machine-readable artifact(JSON/YAML 또는 repository convention에 맞는 형식)와 schema/contract를 남긴다. 구현 위치·입출력 예제·validation error 규칙을 문서화한다.
11. reports/140_report.md를 작성한다. Run-ID, 구현 파일, Intake Schema, Blueprint Schema, 실제 example input→normalized→existing graph→blueprint 결과, negative tests, live Neo4j read 경로, PASS/FAIL, blocker, 다음 단계 input contract를 포함한다.
12. 관련 코드/schema/test/example/report를 commit/push한다.
금지: 신규 Value Chain 전체 source collection, Driver/Bottleneck/Beneficiary를 evidence 없이 확정, Link Expansion 실제 대규모 수행, 신규 Neo4j graph write, 기존 Golden Example 훼손, unrelated refactor, credential 출력·commit, Git reset/rebase/force push.
DoD: (a) IVK NEW Intake Schema 구현, (b) 필수/선택 필드 validation과 normalized output 구현, (c) live Neo4j existing graph check 구현, (d) Blueprint Schema/contract 구현, (e) 신규 실제 입력 예제 1건 Intake→Normalize→Existing Graph Check→Blueprint E2E PASS, (f) negative validation tests PASS, (g) Blueprint가 다음 KE 단계에서 소비 가능한 machine-readable artifact로 생성, (h) reports/140_report.md 생성, (i) commit/push 완료.
