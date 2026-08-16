발행일: 2026-08-16
발신: COO (via ORDER 100 intake)
수신: codex
상태: 진행 중
도구: 없음

---

번호: 142
제목: ivk-phase2-sti-vs-power-semi-quality-gap-benchmark
목적: IVK Phase 2 첫 한계검증으로 기존 STI Golden Example과 Order 141 Power Semiconductor 최초 full-path dry run의 결과 품질을 동일 rubric으로 비교하여, Factory의 실제 품질 gap과 다음 최소 개선 우선순위를 확정한다. 신규 기능 개발이 아니라 현 산출물의 비교·진단이 목적이다.
대상: 기존 STI Golden Example/관련 IVK artifacts 및 reports, Order 141 Power Semiconductor artifacts, reports/141_phase1_full_path_report.md, 현재 Neo4j read-back 결과.
작업:
1. 실행 전 Git clean-tree/preflight를 확인한다.
2. STI Golden Example의 실제 산출물과 Power Semiconductor Order 141 산출물을 repo/Neo4j에서 읽어 비교 가능한 evidence를 수집한다. 추정으로 STI 내용을 채우지 않는다.
3. 동일 rubric으로 최소 다음 6축을 평가한다: (a) Source depth, (b) Evidence provenance/coverage, (c) Value Chain structure quality, (d) Earnings Driver/Bottleneck/Beneficiary evidence quality, (e) Link Expansion quality, (f) Neo4j graph completeness/reviewability.
4. 각 축에 대해 STI를 baseline으로 두고 Power Semi의 상대 수준을 정량/등급화한다. 점수 기준과 근거를 명시하고, 비교 불가능한 항목은 N/A로 처리한다.
5. 단순 node/task 수가 아니라 투자판단에 필요한 정보 구조와 근거 수준을 중심으로 평가한다.
6. STI에 존재하지만 Power Semi에 없는 요소, Power Semi에 존재하지만 STI보다 개선된 요소를 각각 분리해 gap matrix로 제시한다.
7. 특히 filing/earnings call, segment/financial time series, earnings driver, bottleneck, beneficiary, counter-evidence, link expansion, human-review readiness의 실제 coverage를 확인한다.
8. 현재 Factory/contract 문제인지, 단순 evidence depth 부족인지, test-case 특성 차이인지 원인을 분류한다.
9. Phase 2에서 먼저 고쳐야 할 품질 gap 상위 3개만 선정한다. 완벽한 STI 복제를 목표로 하지 말고 E2E 반복에 가장 큰 효과가 있는 최소 개선을 우선한다.
10. Sector Pack은 prerequisite로 평가하지 않는다. Power Semi dry run에서 얻은 reusable knowledge가 있으면 후속 pack 재료로만 표시한다.
11. 결과를 machine-readable benchmark artifact와 `reports/142_report.md`에 기록한다. STI baseline evidence, Power Semi evidence, rubric/score, gap matrix, top-3 priorities, PASS/FAIL/BLOCKED 및 근거를 포함한다.
12. 비교/보고에 필요한 test/report artifact만 commit/push한다. Factory core/Neo4j data를 임의 수정하지 않는다.
금지: 신규 Factory 기능 구현, Neo4j write, 기존 STI/Order141 artifact 변경, evidence 없는 점수 추정, Sector Pack 선행 구축, unrelated refactor, reset/rebase/force push.
DoD: (a) STI와 Power Semi를 동일 rubric 6축으로 비교, (b) 각 판정에 실제 artifact/graph evidence 연결, (c) quality gap matrix 생성, (d) STI 대비 Power Semi 상대 품질 명시, (e) 원인 분류, (f) 다음 최소 개선 top-3 확정, (g) reports/142_report.md 및 machine-readable benchmark 생성, (h) commit/push 완료.
