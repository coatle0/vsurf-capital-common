발행일: 2026-08-17
발신: COO (via ORDER 100 intake)
수신: grok
상태: 진행 중
도구: 없음

---

번호: 147
제목: grok_dart_tikr_live_call_check
목적: 향후 작업에서 dart·tikr MCP를 실사용해야 한다. 146번에서 dart는 30초 타임아웃으로 미접속이었다(부하 문제인지 구조적 문제인지 미확정). 이번엔 dart 단독 접속 여부와, dart·tikr 둘 다 실제 read-only 호출까지 성공하는지 확인한다.
작업:
1. dart MCP 접속을 시도한다. slack/telegram-mcp 등 다른 서버는 이번에 함께 붙이지 않아도 된다(동시 접속 부하 배제 목적).
2. dart 접속 성공 시, 임의의 read-only 조회 도구 1개를 실제로 호출한다(예: 회사 검색 등 조회성 기능 — 데이터 변경 없는 것만).
3. tikr MCP로 tikr_search_company 를 실제 호출해 삼성전자 또는 임의 종목 1개를 조회한다(146번에서 목록만 확인했으니 이번엔 실호출까지).
4. 각각 호출 성공 여부, 응답 시간, 반환된 데이터 일부(민감정보 제외)를 기록한다.
5. dart가 이번에도 타임아웃되면 정확한 에러 메시지와 재시도 여부를 기록한다.
6. reports/147_report.md 에 Report §0 형식으로 남기되 첫 줄에 Run-ID: RUN-147-01 을 포함한다.
금지: write 계열 도구(slack_send_message, tg_send 등)는 절대 호출하지 않는다. dart/tikr의 read-only 조회 외 다른 작업 금지.
DoD: reports/147_report.md 존재, dart·tikr 각각의 접속·실호출 성공/실패 명시, 응답 데이터 일부 포함, Slack 3줄 회신 도착.
