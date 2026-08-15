발행일: 2026-08-15
발신: COO (via ORDER 100 intake)
수신: codex
상태: 진행 중
도구: 없음

---

번호: 129
제목: ivk-phase1b-sti-v2-blocker-closure
목적: ORDER 127 결과의 미해결 blocker를 제거하여 STI를 IVK v2 Golden Example의 실행 가능한 기준선으로 마무리한다. 신규 Pack 확장 전에 investment-kg/live Neo4j parity, source-less REQUIRES 처리, G1 deferred 판정 지원, causal migration dry-run/검증을 완료한다.
대상: ORDER 127 산출물, live Neo4j/IIKG, investment-kg MCP read path, data/127_bu030_taxonomy_review.csv, queries/127_*.cypher, scripts/ivk_v2.py 및 관련 테스트/보고서.
작업:
1. Governance ACTIVE v1.2 preflight 4개(Git latest-order, Git duplicate, Slack active-order, globally-unused)를 실행 직전 재확인하고 보고서 첫 부분에 기록한다. Order 129 외 새 번호를 생성하지 않는다.
2. ORDER 127에서 `user cancelled MCP tool call`로 막힌 investment-kg read path를 현재 runtime/configuration 기준으로 재실측한다. FormFactor, 티에스이, WinWay `get_company_graph`와 `trace_demand_driver(HBM)`를 실행하고 live Neo4j canonical Cypher 결과와 endpoint/type/path 수준으로 비교한다. 불일치가 있으면 원인을 코드/설정/DB target으로 좁히고 최소 수정 후 동일 결과가 나오도록 한다. MCP를 우회해 parity PASS로 간주하지 않는다.
3. source-less `REQUIRES` edge를 식별한다. 기존 STI/TIKR/DART/공식 evidence 안에서 근거를 찾을 수 있으면 source/evidence를 보강하고, 근거가 없으면 assertion/query 대상에서 제거 또는 disabled/deferred 상태로 처리한다. 근거 없는 관계를 confirmed로 승격하지 않는다.
4. `data/127_bu030_taxonomy_review.csv`의 12 deferred 항목을 human-decision-ready packet으로 더 압축한다. 각 항목에 `추천안`, `대안`, `채택 시 영향`, `defer 시 영향`, `근거`, `confidence`를 추가하고, 명백한 데이터 정규화/중복/합계행처럼 사람의 투자 판단이 필요 없는 항목은 deterministic rule로 accepted/rejected 가능 여부를 별도 표시한다. 단, 애매한 사업 taxonomy는 임의 confirmed 금지.
5. IVK v2 causal migration을 live write 없이 dry-run/rollback 가능한 형태로 검증한다. EarningsDriverLink/Bottleneck/BeneficiaryAssessment의 필수 필드, fact/inference/hypothesis 구분, review_status, evidence, confidence, counter_evidence, duplicate guard, no-auto-confirm guard를 포함한다.
6. ORDER 127 대표 3사 prototype(FormFactor, 티에스이, WinWay)을 MCP + live graph 기준으로 재생성/재검증하고 `Demand Driver → Earnings Driver → Metric → Bottleneck → Beneficiary → Counter-evidence → Link Expansion` 각 단계의 source/evidence와 epistemic status가 query로 회수되는지 확인한다.
7. STI Golden Example 완료 여부를 Gate 표로 판정한다: relation parity, G1 decision readiness, HBM 11사 coverage, causal schema readiness, source coverage, duplicate 0, auto-confirm 0. 각 항목 PASS/FAIL/BLOCKED와 정확한 blocker를 기록한다.
8. Phase 1-C 진입조건을 명시한다. 다음 단계는 `STI Discovery/Expansion Loop 1회 완주`이며, ① relation parity PASS ② source-less edge 처리 완료 ③ causal migration dry-run PASS를 필수 gate로 한다. G1의 순수 human taxonomy deferred는 별도 목록으로 남기되 신규 Pack 확산을 막아야 하는지 여부를 근거와 함께 판정한다.
9. 첫 줄 `Run-ID: RUN-129-01`을 포함한 `reports/129_report.md`를 작성하고 변경 파일, 테스트, 실측 결과, 남은 human decision, Phase 1-C 진입 가능 여부를 기록한다.
금지:
• 신규 산업 Pack 구축 금지
• 신규 외부 산업 데이터 대규모 수집 금지
• 근거 없는 taxonomy/causal relation confirmed 금지
• MCP parity 실패를 Neo4j 직접조회로 대체하여 PASS 처리 금지
• 불필요한 대규모 refactor 금지
DoD:
• Run-ID 첫 줄 존재
• investment-kg 4개 표본 호출이 실제 실행되고 live Neo4j와 parity 결과가 명시됨
• source-less REQUIRES가 evidence 보강 또는 명시적 제외/비활성 상태로 처리됨
• deferred 12건 human-decision-ready packet 완성
• causal migration dry-run 및 guard 테스트 PASS
• 대표 3사 causal chain query 재현 가능
• HBM 11/11 coverage 유지, source/evidence missing 0(활성 assertion 기준), duplicate 0, auto-confirm 0
• Phase 1-C 진입 여부가 PASS/FAIL로 명시
• reports/129_report.md 및 필요한 산출물 commit 완료
