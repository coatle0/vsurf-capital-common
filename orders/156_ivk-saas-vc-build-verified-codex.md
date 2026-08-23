발행일: 2026-08-23
발신: COO (via ORDER 100 intake)
수신: codex
상태: 진행 중
도구: 없음

---

번호: 156
제목: ivk-saas-vc-build-verified-codex
목적: 실패 종결된 Grok Order 154를 대체하여 Codex가 IVK Factory build 경로로 미국 상장 SaaS Value Chain을 신규 생성하고 live Neo4j write/read-back까지 VERIFIED로 종결한다.
대상: nickname saas, frame matrix, region us, sector software_saas, seed CRM·NOW·SNOW·DDOG·MDB.
작업:
1. 착수 전 git clean/current와 TIKR·neo4j-official MCP 가용성을 확인한다.
2. repository convention에 맞는 Intake JSON을 작성한다. thesis는 기업용 cloud software 수요와 데이터·관측성·워크플로 플랫폼의 병목/수혜 식별로 하고 bottleneck·beneficiary·seed 밖 link-expansion 질문을 포함한다.
3. TIKR MCP로 각 seed의 상장 identity와 company overview를 실제 조회한다. ticker·exchange·cid와 source_url/source_date/collected_at/content_hash/publisher를 보존한 documents JSON을 만든다. 조회하지 않은 사실은 만들지 않는다.
4. neo4j-official read_cypher로 기존 Company/ValueChain/Product/Process/EndMarket/Evidence/Assertion을 조회해 graph-results JSON으로 저장한다. investment-kg를 canonical read 대체로 사용하지 않는다.
5. 확인된 근거 범위에서만 evidence_id가 연결된 structure JSON을 작성한다. Driver/Bottleneck/Beneficiary는 근거 부족 시 pending 또는 blocked-with-reason으로 둔다.
6. 고유 Run-ID로 다음 단일 명령을 실행한다:
python -m ivk build --input &lt;intake&gt; --run-id &lt;run-id&gt; --runs-dir runs --graph-results &lt;graph&gt; --documents &lt;documents&gt; --structure &lt;structure&gt; --sector software_saas --region us --execute-neo4j
7. software_saas pack이 없으면 가장 좁은 bootstrap pack만 추가하고 관련 테스트를 수행한다.
8. manifest=VERIFIED, receipt/readback 존재, idempotency_replay=PASS, duplicate_ids=0, ValueChain count=1, evidence_complete&gt;=1을 확인하고 neo4j-official read_cypher로 독립 재조회한다.
9. STI·us_optic·us_nuclear 및 시계열 노드 수 불변을 guard query로 확인한다.
10. Run-ID를 첫 줄에 둔 reports/156_report.md와 필요한 machine-readable artifacts를 작성한다. 관련 변경만 남기고 dispatcher가 commit/push하도록 한다. 결과 요약을 #vsurf-code-reports에 게시한다.
금지: 허위 근거·가짜 receipt/readback, unsupported assertion confirmed 승격, unrelated refactor, Power Semiconductor 복원, credential 출력, reset/rebase/force push.
DoD: SaaS Intake/graph/documents/structure 생성, TIKR 실측 근거, build --execute-neo4j 성공, live Neo4j VERIFIED, idempotency·중복·기존 VC 불변 PASS, reports/156_report.md 및 관련 산출물 commit/push, #vsurf-code-reports 결과 게시.
