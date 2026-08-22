# Grok PC2 — neo4j-official MCP 연결 프롬프트

PC2 Grok 세션에 다음 지시를 붙여넣는다.

1. C:\lab에서 작업한다. 기존 ~/.grok/config.toml의 다른 MCP는 삭제·변경하지 않는다. NEO4J_PASSWORD는 출력·로그·파일·명령줄에 표시하지 않는다. 이번 작업에서는 write_cypher를 호출하지 않는다.

2. 다음 파일을 확인한다.

    C:\lab\knowgraph\vendor\neo4j-mcp\.venv\Scripts\python.exe
    C:\lab\knowgraph\investment_workbench\neo4j_mcp_wrapper.py

경로가 없으면 설치하지 말고 BLOCKED로 보고한다.

3. 현재 설정을 확인한다.

    grok mcp list

neo4j-official이 없을 때만 user scope로 등록한다.

    grok mcp add --scope user neo4j-official -e NEO4J_URI=bolt://127.0.0.1:7687 -e NEO4J_USERNAME=neo4j -e NEO4J_DATABASE=neo4j -- C:\lab\knowgraph\vendor\neo4j-mcp\.venv\Scripts\python.exe C:\lab\knowgraph\investment_workbench\neo4j_mcp_wrapper.py

NEO4J_PASSWORD는 wrapper가 Process 환경변수 또는 HKCU\\Environment에서 읽게 둔다.

4. 진단한다.

    grok mcp list
    grok mcp doctor
    grok inspect

neo4j-official의 initialize/health 상태와 도구 목록만 확인하고 전체 config·인증정보는 출력하지 않는다.

5. 다음 도구의 노출 여부를 확인한다.

    get_schema
    read_cypher
    write_cypher

write_cypher는 호출하지 않는다.

6. read-only smoke test를 실행한다.

    neo4j-official.read_cypher: RETURN 1 AS ok

가능하면 get_schema도 1회 호출한다. Neo4j 데이터 변경은 하지 않는다.

7. 다음 형식으로 보고한다.

    [NEO4J MCP CHECK | grok-pc2]
    - config scope: user
    - server: neo4j-official
    - wrapper path: verified / missing
    - initialize: PASS / FAIL
    - get_schema exposed: yes / no
    - read_cypher exposed: yes / no
    - write_cypher exposed: yes / no
    - read-only smoke RETURN 1: PASS / FAIL
    - data mutation: none
    - credentials exposed: no
    - remaining blocker: none or exact reason

## 운영 규칙

- Grok user scope만 변경하며 PC1·Codex 설정은 변경하지 않는다.
- write_cypher는 별도 승인 Order에서만 사용한다.
- grok mcp list에 서버가 이미 있으면 중복 등록하지 않는다.
