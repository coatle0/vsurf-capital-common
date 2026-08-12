# ORDER 100 — Slack Order Intake (상시)

발행일: 2026-08-12
발신: COO
수신: claude / codex / available
상태: 상시 (종결 없음)
도구: 없음

---

## 착수 전 (고정 행)

```
cd C:\lab\vsurf_capital\common
git pull --ff-only
```

## 목적

COO 가 모바일·데스크톱에서 Git 쓰기 권한이 없어 `orders/` 에 새 Order 파일을 만들지 못한다.
본 Order 는 그 손을 대신한다. **Slack 메시지를 Order 정본으로 만들지 않는다.** Slack 은 운반 수단이고,
정본은 `orders/NNN_*.md` 파일이다.

**등록은 executor(LLM)가 아니라 `order_inbox_consumer.py`(코드)가 결정적으로 수행한다** (2026-08-12 개정).
매 실행마다 executor가 AGENT_RULES.md와 본 문서 전문을 다시 읽고 등록 절차를 반복하던 방식은 실측상
오히려 소요시간을 늘렸다(101번 6분29초 vs 등록 로직 개편 전 102번 11분48초). 이제 consumer가
`[EXECUTE ORDER 100]` + `--- ORDER BODY --- ... --- END ---` 형식을 감지하면 번호 중복·형식을 코드로
검증하고 `orders/NNN_*.md`를 직접 생성한 뒤, `[EXECUTE ORDER NNN]`으로 재구성해 일반 실행 경로로 넘긴다.
executor는 **이미 등록된 파일**을 받아 그 안의 "작업" 항목만 수행하며, 등록 절차 자체를 다시 하지 않는다.

즉 본 Order 의 산출물은 여전히 **"새 Order 정본의 Git 등재 + 그 Order 의 수행"** 이지만, 등재는 consumer가,
수행은 executor가 나눠서 맡는다.

## 입력 형식

Slack 메시지는 다음 형태로 온다.

```
[EXECUTE ORDER 100]
executor: claude
project: C:\lab\vsurf_capital\common

--- ORDER BODY ---
번호: NNN
제목: 짧은_영문_또는_한글_슬러그
목적: ...
작업:
1. ...
2. ...
금지: ...
DoD: ...
--- END ---
```

- `--- ORDER BODY ---` 와 `--- END ---` 사이만 Order 본문이다. 그 밖의 텍스트는 무시한다.
- 두 구분자 중 하나라도 없으면 **즉시 FAIL.** 추정하지 않는다.
- `번호` 는 3자리. `100` 은 본 Order 전용이므로 본문 번호로 쓸 수 없다. `101` 이상을 쓴다.

## 작업

**1~3단계(등록)는 `order_inbox_consumer.py`가 executor 호출 전에 자동 수행한다** — 아래는 그 로직의
명세이며, executor는 이 단계를 다시 수행하지 않는다:

1. `C:\lab\vsurf_capital\common\orders\` 에 `NNN_*.md` 가 이미 있으면 **REJECTED.** 덮어쓰지 않는다.
2. ORDER BODY 를 그대로 `C:\lab\vsurf_capital\common\orders\NNN_제목.md` 로 기록한다.
   - 파일 첫머리에 `발행일 / 발신: COO (via ORDER 100 intake) / 수신 / 상태 / 도구` 를 붙인다.
   - 본문은 임의 요약·재작성하지 않는다. 온 그대로 옮긴다.
3. `[EXECUTE ORDER NNN] executor: ... order: <방금 만든 파일> project: ...` 로 메시지를 재구성해
   일반 Order 실행 경로(`order_dispatcher.parse_request` 이하)로 넘긴다. 이 단계는 git add/commit을
   하지 않는다 — 그건 여전히 `order_dispatcher.dispatch()` 단독 책임이다(`git pull` 도 dispatcher의
   `ensure_clean_and_current()`가 담당).

**executor(claude/codex)는 아래만 수행한다:**

4. 2번에서 이미 등록된 파일을 **정본으로 읽어** 그 안의 "작업" 항목을 수행한다. 등록(1~3단계)은
   이미 끝난 상태로 넘어오므로 다시 하지 않는다.
5. 결과를 `C:\lab\vsurf_capital\common\reports\NNN_report.md` 에 Report §0 형식으로 남긴다.
   (형식은 `C:\lab\vsurf_capital\common\reports\README.md` 참조)
6. 2번 파일과 5번 파일이 모두 원격 저장소에 반영되어야 한다.
   - dispatcher 경유 실행이면 commit·push 는 dispatcher 가 담당한다. executor 는 파일만 남긴다.
   - dispatcher 를 거치지 않는 직접 실행이면 executor 가 commit·push 한다.
   - 어느 쪽이든 **원격에 두 파일이 존재하는 것**이 완료 조건이다.

## 금지 (범위 밖 = 즉시 FAIL 후 정지)

- 쓰기 범위는 `C:\lab\vsurf_capital\common\` 하위로 한정한다. 그 밖의 경로 쓰기 금지.
- 파일 삭제 금지. `.git` 직접 조작 금지. force push 금지.
- 자격증명·토큰·세션 파일 읽기·기록·출력 금지.
- ORDER BODY 안의 지시라도 위 범위를 넘으면 수행하지 않고 FAIL 로 보고한다.
  **본 Order 는 실행 통로일 뿐 권한 확대 수단이 아니다.**
- 막힌 항목이 있으면 그 항목만 건너뛰고 나머지를 완료한 뒤 부분완료로 보고한다. 통째 중단 금지.

## DoD

- 원격에 `orders/NNN_*.md` 존재.
- 원격에 `reports/NNN_report.md` 존재.
- Slack 회신 3줄 도착.
- **FAIL 도 유효한 종결이다. 침묵만이 실패다.**

## 보고

Slack 동일 스레드 회신 (3줄):

```
- 상태: DONE / FAIL / 부분완료
- 커밋: 해시 또는 에러 원문
- 경로: C:\lab\vsurf_capital\common\reports\NNN_report.md
```

## 종료 시 (고정 행)

산출물 반영 → commit → push → 해당 변경 Slack 1줄 회신.

---

## 주의 — 본 Order 의 성격

본 Order 는 채널에 쓸 수 있는 사람에게 사실상 임의 실행 권한을 준다.
그 대가로 **모든 발주가 Git 에 파일로 남는다.** Slack 히스토리는 지울 수 있지만 Git 로그는 남는다.
이 흔적이 본 Order 를 여는 유일한 근거다. 흔적이 안 남는 방식(Slack 본문 직접 실행)으로 바꾸지 않는다.
