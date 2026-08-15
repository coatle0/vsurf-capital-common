발행일: 2026-08-15
발신: COO (via ORDER 100 intake)
수신: codex
상태: 진행 중
도구: 없음

---

번호: 139
제목: ivk-winway-live-e2e-write-closure-retry
목적: Order 138의 미완료 DoD를 closure한다. 이미 개방·검증된 neo4j-official write 경로를 사용해 WinWay pilot 3개 assertion을 실제 live Neo4j에 적재하고, post-write readback·integrity·idempotency까지 완료한다.
대상: reports/138_report.md, data/133_winway_live_pilot.json, queries/133_winway_live_pilot.cypher 또는 동일 최신 경로, company:winway, live Neo4j IVK graph
작업:
1. 최신 master와 reports/138_report.md를 확인하고, 138 blocker가 `user cancelled MCP tool call`이었음을 확인한다.
2. 실행 직전 live baseline으로 total nodes, total relationships, CausalAssertion, ASSERTED_FOR, pilot assertion ID 3개 존재 여부를 read_cypher로 측정한다.
3. 기존 WinWay pilot 3개 record의 내용·evidence/source·epistemic status·review status를 변경하지 않는다.
4. 기존 parameterized idempotent MERGE loader를 neo4j-official.write_cypher로 실제 실행한다. write approval이 요구되면 승인 경계를 정상 통과시켜 실제 write가 완료되도록 한다. 승인 취소 시 즉시 BLOCKED로 보고하고 임의 우회하지 않는다.
5. write 직후 counts를 재측정한다. 신규 적재라면 CausalAssertion +3, ASSERTED_FOR +3을 확인한다. 이미 동일 assertion이 존재하면 중복 생성 없이 3개 존재 및 동등성을 확인한다.
6. 3개 assertion 각각에 대해 company:winway 연결, assertion type, evidence/source, epistemic status, review status를 read_cypher로 직접 재조회해 input과 일치하는지 검증한다.
7. duplicate endpoint/type, orphan assertion, missing evidence/source, wrong company mapping, unsupported auto-confirm 여부를 검사하고 모두 0인지 확인한다.
8. 동일 loader/write를 한 번 더 실행하고 counts 및 pilot assertion 수가 더 증가하지 않는지 확인하여 idempotency를 증명한다.
9. reports/139_report.md를 생성한다. baseline/post-write/post-rerun counts, 3개 assertion 상세 readback, integrity 결과, write/read 경로, approval 결과, blocker 유무, 최종 commit SHA를 포함한다.
10. 결과 산출물과 report를 commit/push한다.
금지: Order 138 번호 재사용, 새 universe ingest, WinWay pilot 외 임의 관계 추가, evidence 없는 confirmed 생성, 기존 Golden Example 훼손, unrelated refactor, credential 출력·commit, approval 우회, 임의 reset/rebase/force push.
DoD: (a) live write 실제 완료, (b) WinWay 3개 assertion live 존재, (c) 신규 적재 시 +3/+3 또는 기존 존재 시 동등성 확인, (d) 3개 assertion의 company/type/evidence/status readback PASS, (e) duplicate/orphan/source 누락/wrong mapping/unsupported auto-confirm 모두 0, (f) 두 번째 동일 write 후 count 불변으로 idempotency PASS, (g) reports/139_report.md 생성, (h) commit/push 완료.
