# Neo4j MCP read/write 기본 개방 결과

- 상태: PASS
- 승인: CIO, 2026-08-15
- 대상: `neo4j-official`

## 변경

- 공유 wrapper가 `NEO4J_READ_ONLY=false`를 명시한다.
- 단일 `neo4j-official` MCP에서 `get-schema`, `read-cypher`, `write-cypher`를 모두 노출한다.
- PC1/PC2 공용 wrapper와 설정 스크립트를 `scripts/`에 저장했다.
- 사용자 config와 마스킹 snapshot의 wrapper 경로를 공유 파일로 변경했다.

## 검증

- Python compile: PASS
- PowerShell parser: PASS
- 전체 단위 테스트: 72/72 PASS
- MCP tool list: `get-schema`, `read-cypher`, `write-cypher`
- smoke node 생성 후 count: 1
- smoke node 삭제 후 count: 0
- 전체 `VSURFMCPWriteSmoke` 잔존 노드: 0

## 제한

- GDS가 설치되지 않아 서버 시작 시 `gds.version()` 확인 경고가 발생하지만 Cypher read/write에는 영향이 없다.
- 실제 투자 데이터 write는 idempotent `MERGE`, 사전·사후 count, 중복 및 source/evidence 검증을 적용한다.
