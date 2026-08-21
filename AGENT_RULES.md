# AGENT_RULES — common\ 저장소 규약

> 저장소 루트: `C:\lab\vsurf_capital\common\` (PC1/PC2 공유, git 동기화 대상)
> 자격증명·세션·PC별 설정은 본 저장소 밖 유지 (`.gitignore` 참조).

## Orders (`orders/`)

- 상세 포맷·intake·dispatcher·executor·복구 규칙의 단일 정본은 `C:\lab\vsurf_capital\common\ORDER_PROTOCOL.md`다.
- 파일명은 `NNN_주제.md`(3자리 순번), 필수 머리말은 발행일 / 발신 / 수신 / 상태 / 도구다.
- 본문은 목적 → 대상/범위 → 작업(번호별) → 금지 → DoD 순으로 작성하고 경로는 절대경로를 사용한다.
- `도구:`는 필요한 도구를 기록하는 선언이다. 현재 dispatcher의 범용 MCP 자동 주입을 뜻하지 않으며 실제 지원 범위는 `ORDER_PROTOCOL.md` §4·§6을 따른다.
- 상태값: 미착수 → 진행 중 → 완료 (또는 부분완료 + 미완 항목 명시).
- 수신자는 작업 항목 중 하나가 막히면 그 항목만 건너뛰고 나머지를 완료한 뒤 보고 (통째로 중단 금지).

## Board (`board.md`)

- 정본 1개, 로그 아님. **3줄 상한.**
- `쥔 자` = 점유 표시. 비어있으면 착수 가능, 이름이 있으면 손대지 않음.
- 착수: pull → `쥔 자`에 이름 기입 → push.
- 종료: `지금 단계`·`산출물`·`다음 행동`·`갱신` 교체 → `쥔 자` 비움 → push → 해당 행 1줄 TG 발행.
- 줄은 삭제하지 않고 다음 단계로 민다. 4번째 진입은 기존 1건 종결 후에만.
- 매일 1회 3줄 전문 TG 발행 (무변동이어도 생존 신호로 발행).
- 완료·미착수 발주분은 `orders/` 참조.

## Git 동기화

- 저장소 루트 = `common\` 만 (상위 `vsurf_capital\` 제외).
- PC 간 pull → 작업 → push 순환. 충돌 시 board.md `쥔 자` 규약으로 선점 확인.
- 커밋 전 `.gitignore` 대상(`.venv/`, `__pycache__/`, `*.session`, `.env`, `*.bak_*`, `_*.txt`, `.~lock*`) 포함 여부 확인.

## Slack 실행 Order

- `[EXECUTE ORDER NNN]` 메시지는 일반 대화가 아니라 Git 정본 실행 신호다.
- 신규 발주는 `ORDER_PROTOCOL.md` §5의 `[EXECUTE ORDER 100]` + `ORDER BODY` 형식만 사용한다. 필수 Slack 필드는 `executor`(`codex`/`claude`/`grok`/`available`)와 `project`이며 외부 메시지에 `order:` 필드를 넣지 않는다.
- durable inbox consumer와 dispatcher가 정본 등록·검증·executor 실행·검증·Git 최종화·Slack thread 회신을 담당한다. executor는 prompt 지시대로 commit/push하지 않는다.
- REJECTED/FAILED를 임의 우회하지 않는다. credential/token 값을 출력하거나 저장하지 않는다.
- `CONTINUE`, `APPROVE`, `HOLD`, `RETRY`, `CANCEL`은 상태 저장과 스레드 연결 구현이 완료되기 전까지 자동 실행하지 않는다.
