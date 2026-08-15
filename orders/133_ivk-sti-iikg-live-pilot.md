발행일: 2026-08-15
발신: COO (via ORDER 100 intake)
수신: codex
상태: 진행 중
도구: 없음

---

번호: 133
제목: ivk-sti-iikg-live-pilot
목적: IVK preflight에서 확인된 Golden Example/Neo4j 상태를 기준으로 STI·IIKG를 실제 소규모 live pilot으로 전환하고, 데이터 생성→검증→그래프 반영까지 end-to-end로 확인한다.
대상: 현재 Golden Example 11개사 및 live Neo4j IVK graph
작업:
1. Governance ACTIVE v1.2 preflight를 먼저 수행하고, Order 133이 globally unused인지 Git/Slack/active task 기준으로 재확인한다.
2. `orders/133_ivk-sti-iikg-live-pilot.md`가 정확히 하나 존재하도록 canonical Order 파일을 생성/등록한 뒤 본 작업을 시작한다.
3. 최신 master와 현재 IVK 관련 코드/설정/데이터 상태를 실측한다.
4. 기존 정적 Golden Example을 훼손하지 말고, STI/IIKG live pilot용 최소 입력 세트를 선정한다.
5. 선정 입력에 대해 실제 STI/IIKG 파이프라인을 실행하여 신규/갱신 node, evidence, relationship을 생성한다.
6. Neo4j 반영 전후 count와 생성/갱신된 entity·relationship을 비교한다.
7. 중복, orphan, evidence 없는 relationship, 잘못된 company mapping을 검증한다.
8. 실패가 있으면 원인과 재현 명령을 기록하되 임의 대규모 수정/확장은 하지 않는다.
9. 결과를 reports/133_report.md에 작성하고 관련 산출물/로그 경로 및 commit SHA를 명시한다.
금지: Golden Example 정적 pack 삭제/덮어쓰기, 전체 universe 대량 ingest, 검증 없이 production 범위 확대, unrelated refactor, Order 133 외 새 번호 생성.
DoD: (a) canonical `orders/133_*.md` 정확히 1개, (b) 최소 1개 이상의 STI/IIKG live pilot end-to-end 완료, (c) Neo4j 반영 전후 수치와 변경점 제시, (d) 데이터 무결성 검증 결과 제시, (e) 실패 시 정확한 blocker와 재현법 제시, (f) reports/133_report.md 생성 및 commit/push 완료.
