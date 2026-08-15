발행일: 2026-08-15
발신: COO (via ORDER 100 intake)
수신: codex
상태: 진행 중
도구: 없음

---

번호: 138
제목: ivk-winway-live-e2e-write-validation
목적: 사용 불가능한 Order 133의 원래 목표를 Order 138로 승계한다. 이미 해결된 Neo4j write-capable 경로를 사용해 WinWay pilot의 STI/IIKG 분석 결과를 실제 Neo4j에 적재하고, 재조회·무결성·idempotency까지 검증하여 IVK live E2E를 완주한다.
대상: 기존 Order 133 산출물(data/133_winway_live_pilot.json, queries/133_winway_live_pilot.cypher 또는 동등 최신 경로), company:winway, live Neo4j IVK graph
작업:
1. 최신 master와 기존 Order 133 산출물/보고서를 확인하고, 이전 blocker였던 neo4j-official write_cypher 또는 동등 write 경로가 실제 사용 가능한지 실측한다.
2. 기존 WinWay pilot 3개 IIKG 레코드(EarningsDriverLink, Bottleneck, BeneficiaryAssessment)의 내용·evidence·epistemic/review status를 변경하지 않고 검증한다.
3. live Neo4j 적재 직전 baseline으로 total nodes, total relationships, CausalAssertion, ASSERTED_FOR count를 측정한다.
4. idempotent MERGE 방식으로 WinWay pilot 3개 assertion을 실제 Neo4j에 적재한다.
5. 적재 직후 post-write count를 측정하고 예상 delta(+3 CausalAssertion, +3 ASSERTED_FOR)와 대조한다. 이미 동일 assertion이 존재한다면 중복 생성 없이 기존 3개 존재를 확인한다.
6. 생성/존재하는 3개 assertion 각각에 대해 company:winway 연결, assertion type, evidence/source, epistemic status, review status를 read_cypher로 직접 재조회해 검증한다.
7. duplicate endpoint/type, orphan assertion, evidence/source 누락, 잘못된 company mapping, unsupported auto-confirm 여부를 검사하고 모두 0인지 확인한다.
8. 동일 loader/write를 한 번 더 실행해 idempotency를 검증하고 count가 추가 증가하지 않는지 확인한다.
9. 실제 결과를 reports/138_report.md에 기록한다. baseline/post-write/post-rerun count, 3개 assertion 상세, validation 결과, 사용한 write/read 경로, blocker 유무, 최종 commit SHA를 포함한다.
10. 결과 산출물과 report를 commit/push한다.
금지: Order 133 재사용, 새 universe ingest, WinWay pilot 외 임의 관계 추가, evidence 없는 confirmed 생성, 기존 Golden Example 훼손, unrelated refactor, credential 출력·commit, Order 138 외 새 번호 생성.
DoD: (a) write-capable Neo4j 경로 실측 PASS, (b) WinWay 3개 assertion live 존재, (c) 신규 적재라면 +3/+3 delta 또는 기존 존재 시 동등성 확인, (d) 3개 assertion의 company/evidence/status 검증 PASS, (e) duplicate/orphan/source 누락/unsupported auto-confirm 0, (f) 재실행 idempotency PASS, (g) reports/138_report.md 생성, (h) commit/push 완료.
