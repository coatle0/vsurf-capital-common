발행일: 2026-08-15
발신: COO (via ORDER 100 intake)
수신: codex
상태: 진행 중
도구: 없음

---

번호: 127
제목: ivk-phase1a-sti-v2-foundation
목적: STI Golden Example를 IVK v2의 기준선으로 완성하기 위한 Phase 1-A를 수행한다. 관계 정본 불일치, G1 33행 미종결, IVK v2 causal schema 부재를 해소할 수 있는 구현 기반을 만들고 대표 3사에서 Driver/Bottleneck/Beneficiary/Link Expansion prototype을 실증한다.
대상: 기존 STI Ecosystem Pack, live Neo4j/IIKG, investment-kg 관계 조회 경로, bu030_taxonomy_mapping.csv, 관련 loader/query/test/report. 신규 산업 Pack 구축은 이번 Order 범위에서 제외.
작업:
1. 발행 즉시 Governance v1.2 preflight 결과를 보고서 첫 부분에 기록한다: Git latest-order check, Git duplicate check, Slack active-order check, globally-unused check. 이 Order ID 127 외 다른 번호를 새로 만들지 않는다.
2. STI 관계 정본을 명시한다. 현 preflight에서 live Neo4j와 investment-kg get_company_graph 결과가 불일치하므로, 현행 source-of-truth와 synchronization 경로를 코드/데이터 기준으로 실측하고 최소 수정으로 관계 조회가 동일 결과를 반환하도록 한다. 대표 표본은 티에스이, FormFactor, WinWay 및 HBM→Wafer Test Cell→Probe Card 경로로 한다.
3. G1 `bu030_taxonomy_mapping.csv` 33행을 human-review 가능한 판정 패킷으로 정리한다. 각 행에 현재 제안 taxonomy, source/evidence, 추천 판정(accepted/rejected/deferred), 판단 사유, rollup 여부를 남긴다. Codex가 불확실한 항목을 임의 confirmed 처리하지 않는다. 특히 Yamaichi Test Solution, WinWay Optoelectronic Products Test Fixtures, Yamaichi optical/JEM electron-tube 및 Other 처리, Micro2Nano 중복 주석 2행, Megatouch 합계행을 개별 표시한다.
4. 승인 전제 없이 IVK v2 최소 causal model을 코드/스키마 수준에서 구현 가능하게 만든다. 최소 개념은 EarningsDriverLink, Bottleneck, BeneficiaryAssessment이며 period, affected_metric, direction, lag, source/evidence, confidence, counter_evidence, status(fact/inference/hypothesis 또는 동등한 명시 구분), review_status를 보존한다. 자동 confirmed 승격은 금지한다.
5. 샘씨엔에스 component→Probe Card 누락을 포함해 STI 11사 HBM 관련 경로 coverage를 점검하고, 누락 edge/제품 연결을 evidence 기반으로 보완할 수 있는 로직과 검증 query를 만든다. 근거 없는 edge 생성 금지.
6. 대표 3사(FormFactor, 티에스이, WinWay)에 대해 기존 데이터만 사용해 prototype 분석을 수행한다: Demand Driver→Earnings Driver→실적 metric→Bottleneck 후보→Beneficiary 후보→counter-evidence→Link Expansion frontier. 각 단계에서 DB에 명시된 사실과 LLM/분석 추론을 분리한다.
7. Link Expansion frontier는 supplier/customer만이 아니라 Product, Process, Capacity, Technology, EndMarket, 인접 기업/산업 후보까지 포함하되, `confirmed`가 아니라 evidence와 confidence를 가진 후보 상태로만 제시한다.
8. read/query 경로 regression test를 추가한다. 최소 검증: MCP/live 관계 count 또는 표본 path 일치, HBM 대상 11사 coverage, source/evidence 존재, duplicate 0, unsupported auto-confirm 0.
9. 첫 줄 `Run-ID: RUN-127-01`을 포함한 `reports/127_report.md`를 작성하고, 변경 파일/테스트/실측 결과/남은 human decisions/Phase 1-B blocker를 기록한다.
금지:
• 신규 산업 Pack 구축 금지
• 신규 외부 산업 데이터 수집 금지(기존 STI/TIKR/DART/공식 evidence 재사용은 허용)
• 불확실 taxonomy/causal inference 자동 confirmed 금지
• source 없는 관계/beneficiary/bottleneck 생성 금지
• 운영에 불필요한 대규모 refactor 금지
DoD:
• Run-ID가 report 첫 줄에 존재
• 관계 조회 표본 3사 + HBM 핵심 path에서 investment-kg/live Neo4j 불일치 원인과 해소 상태가 명시되고 테스트 결과가 존재
• G1 33/33행 human-review packet 완성, 미종결 5개 범주가 개별 표시
• IVK v2 causal 최소 모델과 fact/inference 구분이 구현 또는 실제 적용 가능한 migration/loader/query 형태로 존재하며 테스트됨
• HBM 관련 STI 11사 coverage query가 11사를 반환하거나, 반환하지 못할 경우 정확한 blocker와 누락 좌표가 보고됨
• 대표 3사 prototype에 Driver/Bottleneck/Beneficiary/counter-evidence/Link Expansion 결과와 source가 포함
• source/evidence coverage 100%(이번 Order에서 새로 생성한 causal/relationship assertion 기준), duplicate 0, 자동 confirmed 0
• reports/127_report.md + 필요한 산출물 commit 완료
