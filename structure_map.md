# VSURF Structure Map v1
> 발효: 2026-05-08 | CIO 손그림 (2026-05-08 0816) 정본화
> 정본 위치: PC1 `C:\lab\vsurf_capital\common\structure_map.md`
> 아카이브: Drive (PC2/PC3 접근용)
> 갱신 권한: COO Desktop Commander (CIO 결정 후) / GM = read only

---

## §0. 본질

VSURF = **학습하는 운영체제** (continuously updating decision OS).

- Order = 작업 (process)
- Report = 상태 변화 (state transition)
- structure_map = 시스템 topology (본 파일)
- wrapper = scheduler
- feedback = gradient update

모든 Order·Report·결과 = 본 map 의 **칸 좌표** 로 환원되어야 한다.

---

## §1. 골격 (CIO 손그림)

```
[입력 소스]                                                
                                                            
Telegram     ─┐                                            
Earning Call ─┤                                            
Blog         ─┼──→  [Pool] ──→ [Screening] ──→ [Entry] ──→ [EXIT]
X            ─┤      (입구)    [Monitoring]    [Position]
Report       ─┘                                  [Build]
                       ↑              ↑              ↑      ↑
                       │              │              │      │
                       └──────[Feedback / 복기]──────┴──────┘
```

**5 칸 (가로)** + **입력 소스 5종** + **Feedback 회귀 (3 화살표)**.

---

## §2. 칸 상태 enum (6종, 의무)

| 기호 | 의미 | 운영 |
|---|---|---|
| ✅ | 채움 — 가설 검증 완료, 운영 채택 | 정식 사용 |
| ⚠️ | 부분 — 강세 한정 등 조건부 | 한계 박음 후 사용 |
| ⏳ | 검증 중 — 활성 Order 진행 | 결과 대기 |
| ❌ | 비채택 — 검증 후 폐기 | 이력 보존, 재발주 금지 |
| □ | 빈 칸 — 미설계 | Order 후보 |
| 🔍 | 탐색 중 — 호기심 발주, 칸 갱신 보장 X | exploration channel |

→ **🔍 = 학습 OS 핵심.** 호기심만으로 Order 발주 정당화 좌표.

---

## §3. 칸별 현황 (2026-05-08 기준)

### 3.1 입력 소스

| 채움 | 소스 | 가설/Order ID | 비고 |
|---|---|---|---|
| ✅ | VVD pool (vvd_spike=TRUE) | H-VVD-Independence | L1-012 강세·중립 ⚠️ YES |
| ⏳ | top5(Q) 단독 | (#L1-016 대기) | 입구 단독 alpha 미검증 |
| □ | Telegram | - | 미설계 |
| □ | Earning Call | - | 미설계 |
| □ | Blog | - | 미설계 |
| □ | X (트위터) | - | 미설계 |
| □ | Report | - | 미설계 |

### 3.2 Pool — Step A 입구

| 항목 | 상태 | 가설/Order ID |
|---|---|---|
| 입구 정의 (단독/합집합/교집합) | ★★★ □ 미확정 | #L1-016 미발주 |
| A(top5) baseline jackpot | □ | #L1-016 |
| B(VVD) baseline jackpot | ⚠️ 부분 | L1-012 |
| C(교집합) jackpot | ⚠️ marginal | L1-012 G-DEF-3 |
| A∪B∪C(합집합) jackpot | □ | #L1-016 |
| panel B 11개월 재생성 | □ | 별건 |

### 3.3 Screening / Monitoring — Step B/C/D

| 항목 | 상태 | 가설/Order ID |
|---|---|---|
| VVP_M ≥ 50 단독 alpha | ✅ | L1-010 PSM 3.99× |
| RS ≥ 1.10 단독 alpha | ✅ | forward 3.02× |
| VVP+RS 결합 alpha | ✅ | 4.98~13× |
| VVD 누적 8회+ pool (보조) | ✅ | |
| vvd_sigma 강도 | ⚠️ | L1-012 부수 발견, 운영 미반영 |
| monitoring rule (d+5 외) | □ | 학습 영역 |
| monitoring 인프라 | ★★ □ | #L1-011 미발주 |
| 매월 정합 점검 절차 | □ | |

### 3.4 Entry / Position Build — Step E

| 항목 | 상태 | 가설/Order ID |
|---|---|---|
| 1U sizing 정의 | ★★ □ | 미정 |
| 진입 timing (1m VVP) | ✅ | +1.25% alpha, p=10^-39 |
| 체결 실패 진단 | ⏳ | #Exe-008 Step 1.7 대기 |
| rt_name 사후 재구성 가능성 | ⏳ | #Exe-007 Step 1.5 대기 |
| 신호 체계 대안 6건 | 🔍 | #Exe-019 Step 1.5 대기 |
| 시간대 OFF | □ | #Exe-016 후보 |
| 국면 가동 게이트 | □ | #Exe-014 결과 모호 |

### 3.5 EXIT — Step F

| 항목 | 상태 | 가설/Order ID |
|---|---|---|
| d+30 고정 (S0) | ✅ | 채택 |
| 손절선 자동화 | ★ □ | #Exe-001 미발주 (CRO R1 위반) |
| 청산 자동화 | ★ □ | #Exe-001 미발주 (CRO R1 위반) |
| 다른 청산 rule | ❌ | RS컷/정배열역전/복합 = jackpot 손실 |

### 3.6 Feedback — 복기 (Ellis FB BU)

| 항목 | 상태 | 비고 |
|---|---|---|
| Pool 회귀 (입구 검증 결과 → Pool 재정의) | □ | Ellis 미가동 |
| Monitoring 회귀 (운영 결과 → spec 수정) | □ | Ellis 미가동 |
| Entry/EXIT 회귀 (체결·청산 결과 → rule 수정) | □ | Ellis 미가동 |
| 칸 갱신 0 Order 누적 모니터링 | □ | **신규 책무** (분석 중독 감지) |
| 같은 실수 패턴 ≥3 → Order 권고 | □ | Ellis R&R 박힘 |

---

## §4. 칸 의존성 그래프

| 변경 칸 | 영향 받는 인접 칸 | 자동 트리거 |
|---|---|---|
| Pool 입구 | Screening 게이트 spec, Monitoring 표본 | #L1-016 결과 → #L1-011 spec 재검토 의무 |
| Screening 게이트 | Entry universe, EXIT 적용 범위 | VVP/RS 임계값 변경 → 라이브 영향 평가 |
| Entry rule | Position Build sizing, EXIT 매핑 | #Exe-001 결정 → 1U 정의 재검토 |
| EXIT rule | Position Build (d+30 가정 변경 시) | S0 변경 시 sizing 재계산 |
| Feedback 갱신 | 전 단계 (Pool/Screening/Entry/EXIT) | 분기별 structure_map 전체 review |
| 입력 소스 추가 | Pool 입구 정의 | 새 소스 alpha 검증 Order 의무 |

---

## §5. 빈 칸 우선순위 (2026-05-08)

| 우선 | 칸 | 가설/Order |
|---|---|---|
| ★★★ | Pool 입구 정의 | #L1-016 미발주 |
| ★★ | EXIT 손절·청산 자동화 | #Exe-001 미발주 (CRO R1 위반) |
| ★★ | Monitoring 인프라 | #L1-011 미발주 |
| ★★ | Entry 체결 실패 진단 | #Exe-008 Step 1.7 대기 |
| ★ | 1U sizing 정의 | 미정 |
| ★ | 약세장 일반화 | #L1-014 backfill 후 |
| ★ | Feedback 활성화 | Ellis BU 가동 |

---

## §6. 갱신 트리거

| 시점 | 갱신 의무자 | 작업 |
|---|---|---|
| Order 발주 시 | GM | §0 구조 좌표 명시 (검증/탐색 유형) |
| Step 3 Report 종결 시 | GM | 칸 상태 갱신 (✅/⚠️/❌/0) + 인접 칸 영향 보고 |
| handover 작성 시 | GM | §빈 칸 우선순위 갱신 |
| 분기별 review | Ellis FB | 전체 map review + 누적 패턴 보고 |

---

## §7. 본 map 사용 룰

```
1. 모든 GM (Howard/Druck/Ellis) + COO = 결과 수신 시 자동 점검 5건:
   (1) 본 결과 = 어느 칸 갱신?
   (2) 인접 칸 영향: 다음 어느 칸 진행 가능?
   (3) 놓친 빈 칸: 본 Order 가 다루지 않은 영역?
   (4) 다음 Order 후보: 빈 칸 ★ 우선순위 기반
   (5) CIO remind: 위 4건 중 결정 필요 항목

2. Order §0 의무:
   - 검증 대상 칸 명시
   - 유형: 검증 (칸 갱신 강한 의도) / 탐색 (호기심 🔍)

3. Report §0 의무:
   - 칸 상태 갱신 (✅/⚠️/❌/0)
   - "칸 갱신 0" 도 정상 결과 (탐색 Order 시)

4. 호기심 Order 정당:
   - 🔍 좌표로 등록
   - 칸 갱신 보장 X 명시
   - exploration channel 차단 금지

5. 분석 중독 방지:
   - 개별 Order 사전 검열 X
   - Ellis FB BU 가 누적 패턴 모니터링 O
   - 같은 GM 칸 갱신 0 Order ≥3 누적 → 패턴 경고
```

---

## §8. v0 → v1 변경

```
+ CIO 손그림 정본화 (2026-05-08 0816)
+ 칸 상태 6종 (🔍 = exploration channel)
+ 칸 의존성 그래프 (§4)
+ 빈 칸 우선순위 (§5)
+ 갱신 트리거 (§6)
+ 사용 룰 5건 (§7)
```

═══════════════════════════════════════════
*— Structure Map v1 | VSURF Capital | 2026-05-08 —*
*— "VSURF = 학습 OS. 모든 작업은 본 map 의 칸 좌표로 환원된다." —*
═══════════════════════════════════════════
