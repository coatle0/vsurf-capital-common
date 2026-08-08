# CAO HANDOVER — 2026-08-08 v1

> CIO Assist Office | VSURF Capital
> 세션: 통신구조 재설계 → Order 배달 파이프 구축 → 실증 완료

---

## §0 1줄 핵심

**통신 채널(Slack/Redis) 도입을 전부 기각하고, 병목의 실체를 "Order 배달의 불연속"으로 재정의 — git 저장소 + `orders\` + `board.md` 로 파이프를 세우고 ORDER 001·002 로 PC 간 왕복·모바일 원격까지 실증 완료.**

---

## §1 본 세션 트리거

- 주군: "지금의 TG 기반 통신방식을 바꾸는 방안으로 첨부문서 검토해줘" (Slack 기반 멀티에이전트 협업 구조 문서)
- 이후 주군 자기 진단: **"order 나오고 bill에게 보내는 구간에서 불연속 발생, context 손실"**
- 이 진단이 세션 전체의 축을 바꿈.

---

## §2 핵심 결정

### 2-1. 도구 도입 전면 기각

| 후보 | 기각 사유 |
|---|---|
| Slack (공식 @Claude) | 클라우드 세션 + GitHub repo 상대. **PC2 로컬 Bill 제어 불가.** CLAUDE.md·MCP·정본 미탑재 |
| Slack (커뮤니티 브리지) | tmux 키 입력 주입, macOS 검증 한정. 주군 = Windows |
| Slack Events 수신기 | 설계 3번 "담당 에이전트를 깨움" 이 미정의. Desktop 앱은 외부 이벤트로 기동 불가 |
| Redis Streams / MQTT | **소비자 부재.** 브로커에 쌓여도 Bill 은 프롬프트 앞에 멈춰 있음 |
| stdio MCP 원격 다리 | 기계 경계 못 넘음 + 접근 불가 PC2 에서 사망 감지 불가 |

→ **최종 도입 부품 = 0.** git 저장소 1개만 신설.

### 2-2. 병목 재정의

- 통신 수단 문제 아님. **"Order 가 주군 손을 거쳐야 Bill 에게 닿는다"** 는 구조가 병목.
- 실측 물증: TG 에 Order 는 멀쩡히 발행되어 있으나 **디스크에 산출 폴더 0** (`daily_state\` `ax_sector\` 미생성).
- STI-G1 33행 검토 13일 정지 = 게으름 아님. 구조가 매번 주의를 뜯어간 결과.

### 2-3. 해법 3층 구조

```
바닥: git 저장소 (coatle0/vsurf-capital-common, PRIVATE)
      - orders\        = 할 일
      - board.md       = 현재 상태 (3줄 상한)
      - AGENT_RULES.md = 공유 규약
      - handover\      = 세션 인수인계 풀본
가운데: Remote Control (폰/웹 → PC2 Bill 실시간)
껍데기: TG (알림·짧은 지시. 명령 운반 역할은 파일에 이양)
```

- 조직도(COO→GM→Bill) **유지**. TG **유지**. 바뀐 것은 Order 가 놓이는 자리 하나.
- TG = 알림/이력, 파일 = 작업 지시. 읽는 자가 다르므로 분리.

### 2-4. board 설계 (구 `task_board_v3` 0/20 실패 교훈)

| 실패 요인 | 대응 |
|---|---|
| HTML = 에이전트가 못 고침 | **마크다운.** 기계가 쓰는 자리 |
| 20줄 = 역산 발생 | **3줄 하드 상한** |
| 갱신 주체 불명 | `쥔 자` = 점유 표시. 착수 시 이름, 종료 시 비움 |
| DCOS 유물(부서·5 Pillars) | 미탑재 |

---

## §3 산출물

### 신설 정본 (전부 절대경로)
- `C:\lab\vsurf_capital\common\board.md` — 상태판 3줄 상한 + 규약 6항
- `C:\lab\vsurf_capital\common\orders\` — Order 파일 자리
- `C:\lab\vsurf_capital\common\orders\001_git_init.md`
- `C:\lab\vsurf_capital\common\orders\002_pc2_clone.md`
- `C:\lab\vsurf_capital\common\AGENT_RULES.md` — orders·board 규약 + 도구 칸 + pull/push 고정 행 + **절대경로 규약**
- `C:\lab\vsurf_capital\common\handover\` — 본 파일
- `C:\lab\CLAUDE.md` — AGENT_RULES 참조 1줄 추가

### 저장소
- `coatle0/vsurf-capital-common` (PRIVATE)
- 저장소 루트 = `C:\lab\vsurf_capital\common\` **만**
- **Bill 실행 루트(`C:\lab`) 와 저장소 루트는 별개** — Order 본문 경로는 반드시 절대경로
- 커밋 계보: `b89f356` → `df4463e` → `7497c8d` → `a03c110`(PC2) → `07f3afe` → `7c52194`

### idea_inbox
- **I-021** — "Order 전달 불연속 제거 — orders 파일 + board 상태판" / H-Frame (I-006 Multi Session 계보)

### TG 발행
- #375 ORDER 001 발행 / #377 001·002 종결 / #378 handover slim

---

## §4 결정 요약 표

| # | 결정 | 근거 |
|---|---|---|
| 1 | Slack 도입 기각 | 로컬 Bill 제어 불가. 순이득이 스레드 1개로 좁혀짐 → 파일이 대체 |
| 2 | Redis/MQTT 기각 | 소비자 부재. 히스토리·분리·신원은 git/폴더/파일이 이미 수행 |
| 3 | git 저장소 = 바닥 | 6 에이전트의 유일한 공통분모 = 파일 |
| 4 | 저장소 범위 = `common\` 만 | 상위 루트에 vendor repo·.venv·미디어 혼재 |
| 5 | board 3줄 상한 | 20줄 판이 0/20 으로 죽은 실측 |
| 6 | Order `도구:` 칸 신설 | MCP 콜드스타트 제거. 미기재 시 `--strict-mcp-config` → 실측 69초 |
| 7 | pull/push 고정 행 | Bill 은 history 없음. 지침이 아니라 Order 안에 있어야 지켜짐 |
| 8 | **절대경로 강제** | 상대경로 시 Bill 이 `C:\lab` 에서 실행되어 `.git` 미인식 (실측 오류) |
| 9 | 한 항목 막히면 그 항목만 skip | 001 1회차에서 통째 중단 발생 (커밋 0) |
| 10 | 무인 스케줄러 = 보류 | G1 1건 수동 검증 후 착수 |

---

## §5 v다음 우선순위

1. **STI-G1 쟁점 4건 판정** — 13일 정지. IVK 확산 게이트 하드락(#Unst-031 §4). ORDER 003. 파이프 첫 실전 손님.
2. **SA-0 Anchor 최소 청산룰** — CIO 직할. G-A 미해제로 SA-4 이후 전부 무효.
3. PC2 단독 파일 14개 저장소 편입 (UNST-004 스크리닝·재고배치·`pc2_setup\`)
4. PC2 PowerShell 프로필 `--dangerously-skip-permissions` 제거
5. 세션 자동명(`gosu-agile-sun`) PC 식별 규약

---

## §6 미결

- **Codex 경로 미검증** — Bill Bash → Codex 호출이 신 저장소 구조 위에서 미확인
- **무인 루프 부재** — 주군이 찌르지 않으면 여전히 안 돎. PC2 스케줄러 미구현
- **모바일 실증 얕음** — `git log` 1줄만. Order 통째 실행은 미시행
- PC1 2.1.220 / PC2 2.1.224 버전 불일치 (PC1 업그레이드 시 Desktop 앱 종료 필요)

---

## §7 다음 세션 첫 행동

**ORDER 003 발행 — STI-G1 쟁점 4건.**

- 쟁점: ①Yamaichi Test Socket/finished 분류 ②WinWay 동일 처리 ③비핵심 Other 처분 ④합계행 rollup 제외
- 형식: 주군이 폰에서 승인/보류만 찍는 구조 (33행 통독 불요)
- 이후 Bill 이 승인 행만 적재 → 반증쿼리 3종 → board 갱신 → TG 1줄
- **이 1건으로 오늘 세운 파이프 전체가 동시 검증됨**

---

## §8 풀본 매핑

- 본 파일: `C:\lab\vsurf_capital\common\handover\CAO_handover_20260808_v1.md`
- 저장소: `coatle0/vsurf-capital-common`
- TG: #375, #377, #378

---

## 부기 — 자기 진단 (페르소나 8번)

- 12턴을 배관 논의로 소모. 병목은 주군이 직접 진술하기 전까지 특정 못 함. **CAO 가 먼저 "무엇이 끊기는가"를 물었어야 했음.**
- 실행 단계 오류: 인자 문법 3회, `remote-control` 을 CLI 인자로 오안내 1회, handover 를 저장소 밖에 배치 1회(주군 지적으로 정정).
- 주군의 "2시간이 낭비가 아니다" 지적 = 타당. 불연속을 "작은 것"으로 셈한 것이 CAO 오산.
- 그러나 **도구 0개 도입**으로 종결. 검토 후 전량 기각이 본 세션의 실질 성과.

---

*— CAO handover 20260808 v1 —*
