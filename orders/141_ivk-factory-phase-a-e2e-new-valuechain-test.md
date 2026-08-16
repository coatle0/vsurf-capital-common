발행일: 2026-08-16
발신: COO (via ORDER 100 intake)
수신: codex
상태: 진행 중
도구: 없음

---

번호: 141
제목: ivk-factory-phase-a-e2e-new-valuechain-test
목적: IVK Factory Phase A가 신규 Value Chain 입력을 실제로 Intake→Blueprint→Pack Registry→Source Plan→Evidence Task까지 재현 가능하게 처리하는지 검증한다. 이번 Order는 Factory 기능 검증이 목적이며 LLM 호출 및 Neo4j write는 수행하지 않는다.
대상: 현재 master의 IVK Factory Phase A 구현, Order 140 Blueprint contract, reports/ivk_factory_phase_a_report_2026-08-16.md, AI Optical/CPO 기존 fixture와 다른 신규 테스트 입력.
테스트 입력:
• name: AI Data Center Power / Power Semiconductor
• seed: VRT, ETN, VST, ON, WOLF
• frame: Sponsor→Value Chain→Bottleneck
• thesis: AI 데이터센터 전력 수요 증가가 UPS·배전·전력반도체·전력관리 설비의 수요와 병목을 확대할 수 있다.
• questions:
    a. 핵심 수요 드라이버는 무엇인가?
    b. 전력 공급망의 병목은 어디에서 발생할 가능성이 높은가?
    c. 병목 완화 시 최대 수혜 후보는 누구인가?
    d. 어떤 인접 product/process/technology/company로 Link Expansion해야 하는가?
작업:
1. 실행 전 Governance/preflight와 Git 상태를 기록한다. 기존 IVK Factory Phase A 관련 코드/산출물을 임의 수정하지 않는다.
2. 위 IVK NEW 입력을 Order 140 Intake parser/validator에 투입한다.
3. Normalize 결과에서 seed canonicalization/dedupe, primary frame, thesis/questions 보존을 확인한다.
4. 기존 graph check가 지원되는 범위에서 seed별 existing/unresolved 상태를 기록하되, canonical live graph read 규칙을 위반하지 않는다.
5. Blueprint artifact를 생성하고 schema validation을 수행한다.
6. Pack Registry에서 Frame/Sector/Region pack selection 및 version/alias/compatibility 결과를 기록한다.
7. Blueprint→Source Plan planner를 실행하여 entity-resolution/source/evidence task를 생성한다.
8. unresolved seed가 누락되지 않는지, 각 question에 대응하는 evidence task가 존재하는지 확인한다.
9. Token Ledger의 stage/model budget 계획이 생성되는지 확인한다. 실제 LLM 호출은 0이어야 한다.
10. Neo4j write는 0이어야 하며 auto_confirm=false를 유지한다.
11. 동일 입력으로 Phase A를 한 번 더 실행해 deterministic output을 비교한다. task ordering, pack manifest, normalized seeds, source-plan 핵심 구조가 동일해야 한다. runtime timestamp/run-id처럼 비결정 필드는 비교에서 제외 가능하나 제외 근거를 명시한다.
12. negative case 최소 2건을 실행한다: empty seed, malformed field type. 둘 다 명시적 validation reject가 발생해야 한다.
13. 결과를 machine-readable artifact와 reports/141_report.md에 기록한다. report에는 입력, normalized result, blueprint, pack manifest, source plan/task counts, token budget, unresolved seeds, deterministic rerun 비교, negative tests, LLM call count, Neo4j write count, PASS/FAIL, blocker를 포함한다.
14. 이번 테스트로 생성된 test/report artifact만 commit/push한다. Factory core 수정이 필요하면 임의 수정하지 말고 FAIL/BLOCKED로 보고한다.
금지: LLM 실제 호출, Neo4j write, 기존 Golden Example/AI Optical CPO fixture 훼손, Factory core unrelated refactor, evidence 없는 confirmed 생성, credential 출력·commit, reset/rebase/force push.
DoD: (a) 신규 IVK NEW 입력 Intake PASS, (b) Blueprint schema PASS, (c) Frame/Sector/Region pack selection 및 manifest 고정, (d) unresolved seeds 보존, (e) Source Plan/Evidence Tasks 생성, (f) question별 evidence coverage 존재, (g) Token Ledger budget 생성, (h) LLM calls=0, Neo4j writes=0, auto_confirm=false, (i) 동일 입력 2회 deterministic 핵심 output 일치, (j) negative validation 2건 PASS, (k) reports/141_report.md 및 machine-readable test artifact 생성, (l) commit/push 완료.
