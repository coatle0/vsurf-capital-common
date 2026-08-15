발행일: 2026-08-15
발신: COO (via ORDER 100 intake)
수신: codex
상태: 진행 중
도구: 없음

---

번호: 132
제목: ivk-phase1c-sti-discovery-expansion-loop
목적: STI Golden Example에서 IVK v2의 핵심 순환형 Discovery Loop를 실제로 1회 완주한다. 정형 실적/재고/사업부/코멘터리는 investment-kg를 사용하고, 기업·제품·공정·수요동인 다중 관계와 경로 검증은 live Neo4j/Cypher를 사용하여 각 도구의 적합한 역할을 유지한다.
대상: STI Ecosystem Pack 11사, investment-kg 정형 조회 도구, live Neo4j/IIKG, ORDER 127/129/131 산출물, 대표 causal prototype 3사(FormFactor, 티에스이, WinWay).
작업:
1. Governance ACTIVE v1.2 preflight 4개를 실행 직전 재확인하고 reports/132_report.md 첫 부분에 기록한다. Order 132 외 새 번호 생성 금지.
2. 역할 분리를 명시한다: 실적·재고·사업부·월매출·증설·경영진 코멘터리 등 정형 조회는 investment-kg; 기업:left_right_arrow:제품:left_right_arrow:공정:left_right_arrow:수요동인 관계 및 다중 hop 탐색은 live Neo4j/Cypher를 canonical graph read로 사용한다. get_company_graph parity 문제는 본 Order의 blocker가 아니라 별도 remediation 항목으로 기록한다.
3. STI에서 대표 3사(FormFactor, 티에스이, WinWay)를 중심으로 실제 `Source → Analyze → Structure → Graph → Query → Discover → Expand → Source` loop를 수행한다.
4. 각 회사에 대해 investment-kg 정형 도구로 최근 실적/사업부/재고/증설/경영진 코멘터리 중 사용 가능한 항목을 수집하고, live Neo4j/Cypher로 HBM/DRAM, Wafer Test Cell, Probe Card/Test Socket/Vertical Probe Card 등 관련 graph path를 조회한다.
5. 수집 결과를 근거로 Earnings Driver를 도출한다. 각 driver에 affected_metric, direction, lag, period, source/evidence, confidence, counter_evidence, epistemic status를 포함한다. fact/inference/hypothesis 구분 유지, 자동 confirmed 금지.
6. 각 회사 또는 value-chain 공통 수준에서 Bottleneck 후보를 최소 1개 이상 도출하고, 병목의 종류(capacity/process/product/component/technology/customer qualification 등), 제한 메커니즘, evidence, counter-evidence, confidence를 기록한다. 근거가 부족하면 hypothesis로 유지한다.
7. Bottleneck 변화 시 최대 수혜 가능성이 있는 Beneficiary 후보를 식별한다. 단순 HBM exposure가 아니라 bottleneck과 beneficiary의 경제적 연결 메커니즘을 설명하고, 어떤 metric이 어떻게 개선될 수 있는지와 반증 조건을 기록한다.
8. Link Expansion을 실제 수행한다. 기존 graph와 분석에서 새로운 Product, Process, Component, Capacity, Technology, EndMarket, Adjacent Company/Industry frontier를 생성하고 각 후보별 `왜 연결되는가`, `기존 근거`, `추가 확인이 필요한 source`, `우선순위`를 기록한다. 이번 Order에서는 근거 없는 새 edge를 live DB에 쓰지 않는다.
9. Expansion frontier 중 가장 투자적으로 유의미한 1~3개를 선택해 기존 STI/TIKR/DART/공식 source 범위에서 재조사하고, 그 결과로 기존 가설을 strengthen/weaken/reject 중 하나로 업데이트한다. 이것으로 `Expand → Source`까지 loop를 닫는다.
10. 최종적으로 대표 3사와 STI 공통 value chain에 대해 `Demand Driver → Earnings Driver → Metric → Bottleneck → Beneficiary → Counter-evidence → Link Expansion → Source 재확인` chain을 표와 구조화 파일로 남긴다.
11. IVK v2 Golden Example 관점에서 이번 loop가 재현 가능한지 평가한다. 어떤 단계가 자동화 가능하고, 어떤 단계가 analyst judgment를 필요로 하는지 분리한다. 다음 단계가 신규 Ecosystem Pack E2E 구축인지, STI 내 추가 loop가 필요한지 PASS/FAIL로 판정한다.
12. 첫 줄 `Run-ID: RUN-132-01`인 `reports/132_report.md`를 작성하고 필요한 data/query 산출물을 commit한다.
금지:
• get_company_graph parity 문제를 이유로 본 loop를 중단하지 말 것
• 근거 없는 새 graph edge를 live DB에 쓰지 말 것
• inference/hypothesis 자동 confirmed 금지
• 신규 산업 Pack 구축 금지
• 불필요한 대규모 refactor 금지
DoD:
• Run-ID 첫 줄 존재
• investment-kg 정형 조회 + live Neo4j 관계 조회 역할 분리가 실제 실행 결과로 입증됨
• 대표 3사 모두 Earnings Driver / Bottleneck / Beneficiary / Counter-evidence / Link Expansion 결과 존재
• 최소 1개 이상의 expansion frontier에 대해 source 재조사 후 strengthen/weaken/reject 판정 존재
• `Source → Analyze → Structure → Graph → Query → Discover → Expand → Source` loop가 실제 한 바퀴 닫힘
• source/evidence 없는 assertion 0, duplicate 0, auto-confirm 0 유지
• STI Golden Example의 Phase 1-C PASS/FAIL과 다음 단계가 명시됨
• reports/132_report.md 및 필요한 산출물 commit 완료
