발행일: 2026-08-23
발신: COO (via ORDER 100 intake)
수신: codex
상태: 진행 중
도구: 없음

---

번호: 157
제목: ivk-saas-vc-build-verified-codex
목적: Codex가 IVK Factory build 경로로 미국 상장 SaaS Value Chain을 신규 생성하고 live Neo4j write/read-back까지 VERIFIED로 종결한다.
대상: nickname saas, frame matrix, region us, sector software_saas, seed CRM·NOW·SNOW·DDOG·MDB.
작업:
1. git clean/current와 TIKR·neo4j-official MCP 가용성을 확인한다.
2. Intake JSON을 작성한다. thesis는 기업용 cloud software 수요와 데이터·관측성·워크플로 플랫폼의 병목/수혜 식별로 하고 bottleneck·beneficiary·seed 밖 link-expansion 질문을 포함한다.
3. TIKR MCP로 각 seed의 상장 identity/company overview를 실제 조회하고 ticker·exchange·cid·source_url·source_date·collected_at·content_hash·publisher를 보존한 documents JSON을 만든다.
4. neo4j-official read_cypher로 기존 graph를 조회해 graph-results JSON으로 저장한다.
5. evidence_id가 연결된 structure JSON을 작성한다. 근거 부족 인과관계는 pending 또는 blocked-with-reason으로 둔다.
6. 고유 Run-ID로 실행한다:
python -m ivk build --input &lt;intake&gt; --run-id &lt;run-id&gt; --runs-dir runs --graph-results &lt;graph&gt; --documents &lt;documents&gt; --structure &lt;structure&gt; --sector software_saas --region us --execute-neo4j
7. software_saas pack이 없으면 최소 bootstrap pack과 관련 테스트만 추가한다.
8. VERIFIED, receipt/readback, idempotency PASS, duplicate_ids=0, VC count=1, evidence_complete&gt;=1을 확인하고 neo4j-official로 독립 재조회한다.
9. STI·us_optic·us_nuclear와 시계열 노드 수 불변을 확인한다.
10. Run-ID를 첫 줄에 둔 reports/157_report.md를 작성한다. dispatcher가 관련 산출물을 commit/push하며 결과를 #vsurf-code-reports에 게시한다.
금지: 허위 근거·가짜 proof, unsupported confirmed 승격, unrelated refactor, Power Semiconductor 복원, credential 출력, reset/rebase/force push.
DoD: SaaS Intake/graph/documents/structure, TIKR 실측, build --execute-neo4j, live VERIFIED, 무결성 PASS, reports/157_report.md, commit/push, rpt 게시.
