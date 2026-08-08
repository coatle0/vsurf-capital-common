# ORDER 002 — PC2 clone + 왕복 실증 + Order 도구 칸 신설

발행: 2026-08-07 | 발신: CAO (CIO 승인) | 수신: Bill (PC2 / 일부 PC1)
상태: 미착수
도구: 없음 (git·파일만. MCP 불요)

## 착수 전
`git pull` 실행. 최신 정본 확보 후 시작.

## 목적
Order·board·정본이 PC 경계를 넘어 실제 도착함을 실증.
+ Order 실행 시 불필요한 MCP 콜드스타트 제거 (도구 칸 신설).

## 작업

### A. PC2 (주군 접근 가능 시)
1. `gh auth login` 완료 여부 확인 (미인증 시 보고 후 중단, 이 항목만)
2. 기존 `C:\lab\vsurf_capital\common\` → `common_old\` 로 **이름 변경** (삭제 금지)
3. `gh repo clone coatle0/vsurf-capital-common C:\lab\vsurf_capital\common`
4. `common_old\` 와 신규 `common\` 파일 목록 비교 → PC2 단독 존재 파일 **목록만** 보고 (이동·삭제 금지)
5. `claude remote-control` 기동 + `/config` 에서 전 세션 자동 활성화·알림 ON

### B. 왕복 실증
6. PC2에서 `board.md` 파이프 행 갱신 → commit → push
7. PC1에서 `git pull` → 해당 변경 반영 확인

### C. PC1
8. `AGENT_RULES.md` 에 **Order 도구 칸** 규약 추가:
   - Order 본문에 `도구:` 행 필수. 비었으면 MCP 없이 실행(`--strict-mcp-config`).
   - 필요한 MCP만 명시 (예: `도구: investment-kg, neo4j`).
9. Order 표준 양식에 `착수 전 pull` / `종료 시 push` 를 앞뒤 고정 행으로 명시

## 금지
- 자격증명·토큰 값 출력 (존재 여부만)
- `common_old\` 삭제·파일 이동
- 한 항목이 막히면 **그 항목만** 건너뛰고 나머지 완료 후 보고 (통째 중단 금지)

## DoD
PC2 커밋이 PC1에서 pull로 확인됨 (왕복 1회 성립).

## 종료 시
`board.md` 파이프 행 갱신 → push → TG 1줄 발행.
보고: 양 PC 경로, 왕복 성공 여부, PC2 단독 파일 목록, remote-control 활성 여부, 미완 항목.
