발행일: 2026-08-15
발신: COO (via ORDER 100 intake)
수신: codex
상태: 진행 중
도구: 없음

---

번호: 131
제목: ivk-investment-kg-parity-root-cause-fix
목적: ORDER 129의 유일한 Phase 1-C 필수 blocker인 `investment-kg` MCP 호출의 `user cancelled MCP tool call` 원인을 runtime/config/code 수준에서 특정하고 최소 수정하여, live Neo4j canonical read와의 relation parity를 실제 MCP 호출로 PASS시킨다.
대상: investment-kg MCP runtime/config/source, neo4j-official canonical endpoint, ORDER 127/129 parity queries 및 reports/129_report.md.
작업:
1. Governance ACTIVE v1.2 preflight 4개를 실행 직전 재확인하고 보고서에 기록한다. Order 131 외 새 번호 생성 금지.
2. `investment-kg`의 실제 MCP 등록 위치, command/transport, environment, DB URI/database target, startup log, tool exposure 상태를 실측한다. `user cancelled MCP tool call`이 사용자 승인 UI, MCP client/runtime, server startup, timeout, transport, config inheritance, tool schema 중 어디에서 발생하는지 단계별로 분리한다.
3. 서버 프로세스/CLI를 직접 기동 가능한 경우 health/tool-list 수준까지 확인하고, 동일 runtime에서 최소 read call을 재현한다. 단순 Neo4j 직접조회 성공을 investment-kg 성공으로 간주하지 않는다.
4. 원인이 코드/설정으로 특정되면 최소 수정한다. credential/secret은 출력·commit 금지. 광범위 refactor 금지.
5. 수정 후 실제 investment-kg MCP로 `get_company_graph(FormFactor)`, `get_company_graph(티에스이)`, `get_company_graph(WinWay)`, `trace_demand_driver(HBM)` 4개를 재실행한다.
6. 각 결과를 `neo4j-official` + `queries/127_sti_reconciliation.cypher` canonical output과 company ID, relation type, endpoint, HBM path, source/evidence 기준으로 비교한다. 네 호출 모두 payload가 반환되고 의미적 parity가 확인되어야 PASS다.
7. parity가 PASS하면 Phase 1-C 진입 gate를 다시 판정하고 다음 단계가 `STI Discovery/Expansion Loop 1회 완주`임을 명시한다. 실패하면 정확한 root cause, 외부/사용자 조치가 필요한 최소 항목, 재검증 절차를 명시한다. 반복적으로 같은 cancelled 호출만 수행하고 종료하지 않는다.
8. 첫 줄 `Run-ID: RUN-131-01`인 `reports/131_report.md`를 작성하고 변경 파일, 진단 증거, 수정 내용, 4-call 결과, parity matrix, Phase 1-C gate PASS/FAIL을 기록한다.
금지:
• Neo4j 직접조회로 MCP parity PASS 대체 금지
• credential/token/secret commit 금지
• 신규 산업 Pack 구축 금지
• causal/taxonomy를 근거 없이 confirmed 승격 금지
• 불필요한 대규모 refactor 금지
DoD:
• Run-ID 첫 줄 존재
• `user cancelled MCP tool call` root cause가 구체적 계층까지 특정됨
• 필요한 경우 최소 수정이 적용되고 테스트됨
• investment-kg 4개 표본 호출의 실제 결과가 기록됨
• live Neo4j와 parity matrix가 존재
• relation parity PASS 또는 외부조치가 필요한 명확한 BLOCKED 원인이 확정됨
• Phase 1-C 진입 여부 PASS/FAIL 명시
• reports/131_report.md 및 필요한 산출물 commit 완료
