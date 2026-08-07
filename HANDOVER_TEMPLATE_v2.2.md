# HANDOVER TEMPLATE v2.2

> VSURF Capital | handover 작성 표준
> 발효: 2026-05-08 | 직전: v2.1 (2026-05-08, β1~β3 박음)
> v2.1 → v2.2: review 위험 3건 처방 (badge game / hindsight contamination / wrapper obesity)
> 정본 위치: PC1 `C:\lab\vsurf_capital\common\HANDOVER_TEMPLATE_v2.2.md`
> 적용 범위: COO + Howard + Druck + Ellis (4 BU 동일 + BU 차별 §)

---

## §A. 본 template 사용 룰

```
1. 11 섹션 표준 (§0 ~ §11)
2. §5 / §6 = mind continuity 의무 (state continuity § 외 별도 박음)
3. 0건 시 해당 § 삭제 (강제 박음 X, "해당 없음" 명시 금지)
4. BU 별 lineage 유형 차별 적용 (§5 박음 시)
5. 풀본 = .md, 슬림판 = TG ≤4000자
6. 자체 ID 헤더 의무 ([HANDOVER #BU vN])
7. 검증 레벨 / Risk Register / Cycle Position 의무 (§5 박음 시)
8. ★ §5 = "당시 판단 기준" (decision-time, 결정 시점 정보만)
   ★ §6 = "사후 평가" (post-hoc, hindsight 박음 OK)
   ★ 두 § 중복 박음 금지 = hindsight contamination 방지
9. ★ L-level 명시 시 4 항목 동반 의무 (badge game 방지) — §D 의무 박음
10. ★ Risk Register = R1~R5 표준 + RX emergent slot (고정 taxonomy 위험 처방) — §F 의무 박음
11. ★ Anti-obesity 룰 — §G 의무 박음
```

---

## §0. 본 세션 핵심 (1줄)

[본 세션 = 무엇을 박았는가, 1줄.]

---

## §1. 본 세션 트리거

[배경 / CIO 발화 / 직전 세션 잔여 / 외부 사건.]

---

## §2. 본 세션 핵심 결정

### 2.1 [결정 1]
[정의 / 결정 본문]

### 2.2 [결정 2]
...

→ 결정 박음, 근거 = §5 박음 (분리).

---

## §3. 본 세션 산출물

### 3.1 [산출물 1]
- 위치: PC1 / outputs / TG
- 크기 / 라인
- Drive 동기화: ✅ / ⚠️ / ❌
- TG 발행: msg N

---

## §4. 결정 (요약 표)

| # | 결정 | 비고 |
|---|---|---|
| 1 | [결정 1] | [근거 §5.X 참조] |

→ 표 = 빠른 인지. 근거 = §5 별도.

---

## §5. Reasoning Lineage ★ "당시 판단 기준" (decision-time)

**작성 룰**: 결정 시점에 알았던 정보만 박음. 사후 정보 박음 금지 (hindsight contamination 방지). 사후 박음 = §6.

### 5.1 채택 가설 / 결정 — 왜
- 채택 결정 ID
- 핵심 근거 (정량 / 정성 1줄)
- 통제 변수 + 통과 검증 (PSM·통제 회귀·robustness)
- ★ **검증 레벨 (L0~L4) + 4 항목 동반 의무** — §D 박음
  - confidence % (0~100%)
  - evidence count
  - counter-evidence count
  - falsification condition
- 잔존 의혹 (있을 시)

### 5.2 폐기 가설 / 옵션 — 왜
- 폐기 결정 ID
- 폐기 근거 (artifact / 표본 부족 / 정합 깨짐 / 의존성 / 비용)
- 부분 잔존 가능성 (Idea Inbox 이관 / 다음 사이클 재검토)

### 5.3 Rejected Alternatives — 왜 채택 안 했는가
- 본 세션 검토했으나 채택·발주 안 한 옵션
- 거절 근거
- 향후 조건부 부활 트리거 (있을 시)

### 5.4 Cycle Interpretation
- ★ 본 결정 시점 사이클 위치 (early / mid / late / euphoric / distressed) 의무 — §E 박음
- 본 사이클 의존 결정 명시 (regime mismatch 위험 박음)
- 다음 사이클 재검증 의무 항목

### 5.5 Risk Weighting — 왜 이 리스크를 중요하게 봤는가
- ★ Risk Register R1~R5 + RX 명시 의무 — §F 박음
- 본 세션 우선 처리 리스크 (≤3건)
- 우선 근거 (영향 크기 × 발생 가능성 × 가역성)
- 후순위 리스크 명시 (의도적 미처리)
- ★ RX (emergent) = 본 세션 발견 신규 risk

→ **0건 시 해당 sub-§ 삭제.**

---

## §6. Review ★ "사후 평가" (post-hoc, hindsight OK)

**작성 룰**: 사후 정보 박음 OK. 결정 시점에 몰랐던 것 박음 = 본 § 가치. §5 와 중복 금지.

### 6.1 잘 맞은 가설 / 결정 — 무엇이 / 왜 (≤3건)

### 6.2 틀린 가설 / 결정 — 무엇이 / 왜 / 무엇을 다르게 했어야 (≤3건)

### 6.3 예상 밖 신호 — 무엇이 / 왜 의외였나 / 의미 (≤3건)

### 6.4 과최적화 위험 — 본 세션 과적합 가능 영역
- data dredging
- cherry-picking
- 표본 한정 일반화
- regime 의존 결과
- p-hacking 의혹

### 6.5 다음 검증 필요성 — 본 세션 잔존 의혹 → Order 후보 (Idea Inbox 등재)

→ **0건 시 해당 sub-§ 삭제.**

---

## §7. v다음 우선순위

| 우선 | 항목 | 비고 |
|---|---|---|
| ★★★ | [항목 1] | |
| ★★ | [항목 2] | |
| ★ | [항목 3] | |

---

## §8. 미결

### 8.1 본 세션 잔여 (즉시)
[CIO 결정 대기 / Know 업로드 / 미진입 작업 등]

### 8.2 활성 Order 큐 (PIN-6 vN 포인터)
| Order ID | BU | Step | 상태 |
|---|---|---|---|
| | | | |

### 8.3 등재 의무 (idea_inbox / hypothesis_tree)
[본 세션 발견·박음 항목 중 정본 등재 미진행분]

---

## §9. 본 세션 핵심 학습

[≤5건. mind continuity 정본 영역.]

---

## §10. 다음 세션 첫 행동

| 옵션 | 내용 | 예상 시간 |
|---|---|---|
| (A) | [후보 1] | |
| (B) | [후보 2] | |
| (C) | [후보 3] | |

권고: **(X) → (Y) → (Z)**. [근거 1줄.]

---

## §11. 풀본 매핑 (있을 시)

| 슬림판 § | 풀본 위치 |
|---|---|

→ 슬림판 ≤4000자 초과 시 풀본 포인터 의무.

---

## §B. BU 별 §5 lineage 유형 (차별)

### Howard (Unst·인식)
- 가설 채택·폐기 lineage
- VVP·VVD·top5 정합 추적 (universe 본질)
- regime 한정 박음 (강세·중립·약세)
- jackpot 정의 의존성
- robustness 통제 변수 누적

### Druck (Exe·실행)
- 진입·청산 결정 lineage
- 사이클 위치 해석 (early / mid / late / euphoric / distressed) — §E 의무
- CRO Rules R1~R4 정합
- 라이브 vs 사후 재구성 정합
- frame 의존성 (1m / 분봉 / d+30)

### Ellis (FB·개선)
- feedback 누적 lineage
- 같은 mistake 패턴 추적 (≥3 → Order 권고 / ≥4 → H-Improve 자식)
- 분기별 cross-BU review 누적
- 마찰 비용 (수수료 / 슬리피지 / 세금 / 기회비용)
- skill vs luck 분리

### COO (CT·운영)
- 시스템 룰 갱신 lineage
- structure_map 좌표 갱신
- BU 간 의존성 박음
- wrapper / template 갱신
- userMemories 박음

---

## §D. 검증 레벨 5단계 + 4 항목 동반 의무 (★ §5.1 의무, badge game 방지)

### 5단계 정의

```
L0 observation     — 데이터 패턴 발견 (단일 관찰, 통계 미수행)
L1 correlation     — 통계적 연관 (lift / r2 / p-value)
L2 causal candidate — 통제 변수 후 효과 잔존 (PSM / 회귀 통제 / robustness)
L3 repeatable edge — 다른 표본·기간 재현 (out-of-sample / cross-validation)
L4 regime robust   — 강세·약세·중립 모두 통과 (cycle 독립)
```

### ★ L-level 명시 시 4 항목 동반 의무

```
L-level 단독 라벨 금지. 다음 4 항목 동반 박음 의무:

1. confidence % (0~100%)
2. evidence count
3. counter-evidence count
4. falsification condition
```

### VSURF 현재 매핑 예 (2026-05-08)

```
L1-010 (VVP_50): L4 한정 / confidence 70%
  evidence: PSM 3.99× / forward 3.02× / 결합 4.98~13×
  counter-evidence: 약세 미검증
  falsification: 약세 사이클 검증 시 lift <2× → L3 강등

L1-012 (VVD-Independence): L2 / confidence 60%
  evidence: G-DEF-4 r0 통제 후 VVD coef 0.7677 (p=1.33e-6)
  counter-evidence: B vs A lift 1.241 (P2 경계), 강세·중립만
  falsification: vvd_sigma 통제 후 VVD 효과 0 = artifact 확정

1m VVP timing: L1 / confidence 50%
  evidence: correlation +1.25%, p=10^-39
  counter-evidence: bid4 cushion 0.96% (실 alpha 0.29%), 16일 라이브
  falsification: 호가 cushion 분리 후 alpha <0.1% = 환영
```

---

## §E. Cycle Position 5단계 (★ §5.4 의무)

```
early       — 사이클 초기 (jackpot 빈도 LOW, 변동성 RISING)
mid         — 사이클 중기 (jackpot 빈도 MID, 변동성 STABLE)
late        — 사이클 말기 (jackpot 빈도 HIGH 후 DROP, 변동성 RISING)
euphoric    — 광기 국면 (jackpot EXTREME, 변동성 EXTREME, crowdedness HIGH)
distressed  — 위기 국면 (jackpot LOW, 변동성 EXTREME, liquidity DROP)
```

→ v9 확장 후보: macro / sector / liquidity / narrative cycle 분리.

---

## §F. Risk Register R1~R5 + RX OPEN slot (★ §5.5 의무)

```
R1 crowdedness risk        — top5(Q) 후행 진입 위험
R2 liquidity illusion      — bid4 cushion 등 호가 환영
R3 narrative contamination — 본인 가설 1년 산물 신뢰 편향
R4 regime mismatch         — 강세 한정 = 약세 일반화 위험
R5 survivorship distortion — 살아남은 표본 한정

RX emergent risk slot:
- 본 세션 발견 신규 risk (R1~R5 매핑 안 되는 영역)
- 명명: RX-{BU}-{N}
- RX 누적 ≥3 = R6 표준화 후보 (Ellis 분기별 review)
```

---

## §G. ★ Anti-obesity 룰 (wrapper obesity 처방)

```
원칙:
1. "프로토콜 준수" 보다 "판단" 우선
2. 0건 시 § 삭제 = obesity 방지 도구
3. 의문 시 = 박지 말고 보고
4. fake lineage / forced reasoning 감지 시 → §6.4 과최적화 위험 박음
5. template = 도구, 목적 X

자가 검증: 본 §X = 실제 사고 기록인가? 형식 채우기인가?
분기별 (Ellis): fake formalization ≥30% → template 갱신 권고
```

---

## §C. v2.1 → v2.2 변경

```
+ §A.8 §5/§6 분리 (decision-time vs post-hoc, hindsight contamination 방지)
+ §A.9 L-level 4 항목 동반 의무 (badge game 방지)
+ §A.10 Risk RX emergent slot
+ §A.11 Anti-obesity 룰
+ §5.1 L-level 4 항목 동반 의무
+ §5.5 RX emergent slot 박음
+ §6 사후 평가 명시
+ §D L-level 4 항목 + VSURF 매핑 정정
+ §F RX OPEN slot 신설
+ §G Anti-obesity § 신설
- (변경 없음) §0~§11 / §B / §E
```

═══════════════════════════════════════════
*— HANDOVER TEMPLATE v2.2 | VSURF Capital | 2026-05-08 —*
*— "박음 = 도구, 목적 X. decision-time lineage + post-hoc review 분리." —*
═══════════════════════════════════════════
