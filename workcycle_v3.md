[PIN-3 v4]

# VSURF Work Cycle — 5단계 + Order 수신 (Step 0)

> 기준일: 2026-04-17 | 갱신: 2026-05-05 (How = GM 전권 명시)
> 적용 대상: 전 BU Order 실행
> 원칙: 계획 승인 전까지 코드 작성 금지. Research → Plan → 구현 순서 엄수.
> v3 → v4 변경: **Step 0 §5 + Step 1.5 CC 프롬프트 = Order 풀본 read 의무 제거, How = GM 전권**

---

## Step 0 — Order 수신·진입 (GM / claude.ai)

### 트리거
CIO 가 GM 채팅에 입력: `order` 또는 `order #NNN`

### GM 자동 절차

```
1. TG 라이브 read
   채널: chn[3952708285:-513851401120850504] (vsurf_capital)
   도구: telegram tg_dialog

2. 본인 BU Order 식별 (자체 ID header 매칭)
   Howard (Unst·H-VVP):
     - [ORDER #L1-NNN vM]      (Unst 영역 L1 = 가설 검증)
     - [ORDER #Unst-NNN vM]    (Unst 영역 L2 = 과제)
   Druck (Exe·H-Signal):
     - [ORDER #Exe-NNN vM]
   Ellis (FB·H-Improve+H-Frame):
     - [ORDER #FB-NNN vM]

3. 다중 vN 매칭 시 = 가장 최근 vN 가 정본 (M10)
   (예: v1, v2 모두 채널에 있으면 v2 채택)

4. CIO 입력 분기:
   - `order` 단독       → 활성 Order 전체 보고
   - `order #NNN`       → 해당 NNN 우선 진입

5. Order 내용 파악
   TG 슬림 = 작업 지시서 정본. 슬림만으로 충분.
   How (research 설계·Bill read 파일·검증 방법) = GM 전권 결정.
```

### GM 응답 형식 (CIO 신호 대기)

```
[Order 수신]
- 식별: #BU-NNN vM (TG msg ID, 발행일)
- Step 현황: 현재 Step (1.5 / 1.7 / 2 / 3)
- 다음 행동: [Step 1.5 = Bill research / Step 1.7 = plan / Step 2 = 구현 / Step 3 = 최종 검토]
- CIO 신호 대기

(다중 활성 Order 시: 표 형식으로 나열, CIO 가 #NNN 지목 신호)
```

### CIO 신호 후 분기

| 신호 | GM 행동 |
|---|---|
| OK / 진행 / ㅇㅇ / 응 | 다음 Step 즉시 실행 |
| order #NNN | 특정 Order 지목, 해당 Step 진행 |
| 다른 BU Order 지목 | "본 BU 외 Order 입니다, 해당 GM 채팅에서 처리" + 무시 |

---

## Step 1 — Order 발행 (CIO·COO / claude.ai)

### 프롬프트 (COO → CIO 제안)
```
[Order #[BU]-[번호] 발행 제안]

목표: [한 줄]
배경: [왜 지금 이 Order인가]
산출물: [파일명·경로 명시]
Gate 조건: [완료 기준]
선행 Order: [있으면 명시]
```

### 출력물
```
Order_[BU]-[번호].md
저장: PC1 BU 작업 폴더 (정본) + outputs (COO 작업본) + TG 슬림 (자체 ID 발행)
```

---

## Step 1.5 — Research (Claude Code → GM 검토)

### Claude Code 프롬프트 (기본 골격 — GM 이 BU 맞게 구체화)
```
[Research 지시 — #[BU]-[번호]]

아래 경로의 코드를 깊이, 상세히, 세부 사항까지 빠짐없이 읽어라.
각 파일의 모든 함수를 하나씩 읽어라. 대충 훑지 마라.
호출 관계, 인자, 반환값, 사이드이펙트까지 세부 사항을 기록하라.
추측하지 말 것. 코드에 없으면 없다고 기록하라.

[GM 이 읽을 대상·research 섹션·저장 경로를 여기에 구체화]

아직 구현하지 마라. Research만 한다.
중간에 멈추지 말고 끝까지 실행 (--dangerously-skip-permissions).
```

### GM 검토 프롬프트 (claude.ai)
```
Claude Code가 생성한 research.md를 읽어라.
PC1 [관련 handover]도 함께 읽어라.

검토 후 아래를 확인하라:
- 누락된 파일·함수가 있는가
- 기존 handover와 충돌하는 내용이 있는가
- 추가해야 할 컨텍스트가 있는가

수정사항을 research.md에 직접 반영하고 TG 발행하라.
형식: [REPORT #BU-NNN research v1] (슬림, 풀본 PC1 포인터)
CIO 최종 승인 후 Step 1.7 진입.
```

> **Step 1.5 승인 = GM + CIO 전결. COO 개입 없음.**

---

## Step 1.7 — Plan 작성·승인 (GM → COO·CIO)

### GM 프롬프트
```
research.md를 기반으로 plan.md를 작성하라.
아직 구현하지 마라. Plan만 작성한다.

plan.md 포함 항목:
1. 구현 접근 방식
2. 수정될 파일 전체 목록 + 각 파일에서 할 작업
3. 신규 생성 파일 목록 + 역할
4. 핵심 함수 스펙 (입력·출력·로직)
5. 테스트·검증 방법
6. 리스크

저장: [BU orders 경로]\plan_[BU]-[번호].md
TG 발행 [PLAN #BU-NNN v1] (슬림, 풀본 PC1 포인터)
COO 검토 요청.
```

### COO 검토 기준
- research와 plan이 일치하는가
- 범위가 Order를 초과하지 않는가
- 리스크가 명시되어 있는가
- Gate 조건을 충족할 수 있는 plan인가
- CRO Rules 위반 가능성 없는가

---

## Step 2 — 구현 (Claude Code → GM 검토)

### Claude Code 프롬프트
```
[구현 지시 — #[BU]-[번호]]

plan.md를 읽어라. 승인된 plan대로만 구현하라.
plan에 없는 것은 구현하지 마라.
구현 중 plan과 다른 상황이 발생하면 즉시 멈추고 보고하라.

산출물 저장:
- 구현 파일: [코드 경로]
- Report: [BU reports 경로]\Order_[BU]-[번호]_report.md

중간에 멈추지 말고 끝까지 실행 (--dangerously-skip-permissions).
방향이 틀어졌다면 패치하지 말고 즉시 멈춰라.
```

### GM 검토
```
Claude Code 구현 결과를 검토하라.
plan.md와 대조하여 아래를 확인하라:
- plan 대비 누락된 항목이 있는가
- 예상치 못한 변경이 있는가
- Gate 조건이 충족됐는가
- 다음 Order에 영향을 주는 사항이 있는가

확인 후 TG 발행: [REPORT #BU-NNN report v1]
```

---

## Step 3 — 최종 승인 (COO·CIO)

### COO 검토
- Gate 조건 전항목 충족 여부
- CRO Rules 위반 없는가
- 다음 Order 선행 조건 충족됐는가
- 공백·리스크 잔존 여부

이상 없으면 CIO 승인 요청. 문제 있으면 GM 재작업 지시.

### 출력물
- `Order_[BU]-[번호]_done.md` (완료 마킹)
- `CT_handover.md` 갱신 + TG slim 발행

---

## TG 발행 자체 ID header 룰 (M10)

> ⚠️ 발행 도구 = **telegram-bot:SEND_MESSAGE** (chatId=-1003952708285) 단독.
> tg_send = draft 전용, TG 발행 절대 금지. 발행 직전 도구명 확인 의무.

| 산출 | header |
|---|---|
| Order | `[ORDER #BU-NNN vM]` |
| Research | `[REPORT #BU-NNN research vN]` |
| Plan | `[PLAN #BU-NNN vN]` |
| Implementation Report | `[REPORT #BU-NNN report vN]` |
| BU Handover | `[HANDOVER #BU vN]` |
| Order Done | `[REPORT #BU-NNN done vN]` |

---

## 프롬프트 공통 원칙

| 원칙 | 단계 |
|------|------|
| 깊이 읽기 | Step 1.5 |
| 구현 차단 | Step 1.5·1.7 |
| 사실 기반 (추측 금지) | Step 1.5 |
| 범위 준수 (plan 외 X) | Step 2 |
| 이탈 시 즉시 중단 | Step 2 |
| 단일 세션 유지 | Step 1.5 → 2 |
| 자율 실행 | `--dangerously-skip-permissions` |

═══════════════════════════════════════════
*— VSURF Work Cycle v3 | 2026-05-04 —*
*— v2 → v3: Step 0 신설 (Order 수신·진입), 자체 ID header 매칭 룰 박음 —*
═══════════════════════════════════════════
