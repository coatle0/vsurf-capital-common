# ORDER 108 — Slack 글루 서명 종단 테스트

목적: Slack이 `project:` 필드 끝에 발신 서명을 붙이는 실제 수신 경로에서
consumer와 dispatcher가 프로젝트 경로를 정상적으로 복원하는지 검증한다.

작업:

1. `C:\lab\vsurf_capital\common\structure_map.md`의 첫 줄을 읽는다.
2. 저장소 파일은 수정하지 않는다.
3. 결과 요약에 읽은 첫 줄과 `signature parser pipeline ok`를 기록한다.

DoD:

- Slack ACK가 한 번 게시된다.
- REJECTED 없이 Order가 `COMPLETED`된다.
- 실행 결과에 `signature parser pipeline ok`가 포함된다.
