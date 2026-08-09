# AGENT_RULES — common\ 저장소 규약

> 저장소 루트: `C:\lab\vsurf_capital\common\` (PC1/PC2 공유, git 동기화 대상)
> 자격증명·세션·PC별 설정은 본 저장소 밖 유지 (`.gitignore` 참조).

## Orders (`orders/`)

- 파일명: `NNN_주제.md` (3자리 순번).
- 필수 필드: 발행일 / 발신 / 수신 / 상태 / **도구**.
- **도구 칸**: Order 본문에 `도구:` 행 필수.
  - 비었으면("도구: 없음") MCP 없이 실행 (`--strict-mcp-config`).
  - 필요한 MCP만 명시 (예: `도구: investment-kg, neo4j`).
  - 목적: Order 실행 시 불필요한 MCP 콜드스타트 제거.
- 본문 구성: **착수 전 pull(고정 행)** → 목적 → 범위 → 작업(번호별) → 금지 → DoD → 보고 → **종료 시 push(고정 행)**.
  - 착수 전 고정 행: `cd C:\lab\vsurf_capital\common` → `git pull`. 최신 정본 확보 후 시작.
  - 종료 시 고정 행: 산출물 반영 → commit → push → 해당 변경 TG 1줄 발행.
- **경로는 전부 절대경로로 기재.** Bill 실행 루트는 `C:\lab` 이고 저장소 루트는 `C:\lab\vsurf_capital\common\` 로 서로 다름.
  상대경로로 적으면 Bill 이 저장소를 인식하지 못함(실측: `.git` 미인식 오류 발생).
  - 예: `orders\003.md` (X) → `C:\lab\vsurf_capital\common\orders\003.md` (O)
  - Order 호출 지시도 절대경로로: `C:\lab\vsurf_capital\common\orders\003_xxx.md 읽고 실행`
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
- 필수 필드: `executor`, `order`, `project`. `project`는 `C:\lab` 아래 절대경로만 허용한다.
- PC2 OpenACP의 Codex 세션은 먼저 다음 Dispatcher를 실행한다.
  `python C:\lab\vsurf_capital\common\scripts\order_dispatcher.py --message-file <메시지파일> --execute`
- Dispatcher가 `REJECTED` 또는 `FAILED`를 반환하면 임의로 우회 실행하지 않고 같은 Slack 대화에 원인만 보고한다.
- Dispatcher 결과의 Order 번호, 상태, 실행자, commit, 검증 요약을 Slack에 회신한다. 토큰 값은 절대 표시하지 않는다.
- `CONTINUE`, `APPROVE`, `HOLD`, `RETRY`, `CANCEL`은 상태 저장과 스레드 연결 구현이 완료되기 전까지 자동 실행하지 않는다.
