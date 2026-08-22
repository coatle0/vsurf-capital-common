"""Acquire GS MCP payloads, persist dated raw snapshots, and build ATI v0.3."""
from __future__ import annotations

import csv
import hashlib
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.font_manager import FontProperties

ROOT = Path(__file__).resolve().parents[1]
GS_TOOLKIT = Path(r"C:\autoai\gs-toolkit")
sys.path.insert(0, str(GS_TOOLKIT))
import gs_batch  # noqa: E402

CALLS = {
    "bgd_year": gs_batch.read_bgdgs_sheet,
    "bgd_th": gs_batch.read_bgdgs_sheet,
    "bgd_thih": gs_batch.read_bgdgs_sheet,
    "kidx-Q": gs_batch.read_sggs_sheet,
    "kidx-W": gs_batch.read_sggs_sheet,
    "kr_idx": gs_batch.read_gs_idx,
}
DATED = ("bgd_year", "bgd_th", "bgd_thih", "kidx-Q", "kidx-W")
SECTORS = ("로봇", "로봇2", "optic", "전공정", "전자부품")
FONT_PATH = Path(r"C:\Windows\Fonts\malgun.ttf")
FONT = FontProperties(fname=str(FONT_PATH)) if FONT_PATH.exists() else None
BOLD = FontProperties(fname=str(Path(r"C:\Windows\Fonts\malgunbd.ttf"))) if Path(r"C:\Windows\Fonts\malgunbd.ttf").exists() else FONT


def rows_from_csv(text: str) -> list[dict[str, str]]:
    return list(csv.DictReader(text.splitlines()))


def num(value: str | None) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float("nan")


def acquire() -> dict[str, dict]:
    results: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = {pool.submit(fn, sheet): sheet for sheet, fn in CALLS.items()}
        for future in as_completed(futures):
            sheet = futures[future]
            result = future.result()
            if not result.get("ok") or not result.get("csv"):
                raise RuntimeError(f"GS read failed for {sheet}: {result.get('error')}")
            results[sheet] = result
            print(f"GS_OK {sheet} rows={result['rows']} cols={result['cols']}", flush=True)
    return results


def latest_date(text: str) -> str:
    dates = [row.get("date", "") for row in rows_from_csv(text) if row.get("date")]
    if not dates:
        raise ValueError("dated sheet has no date values")
    return max(dates)


def persist(results: dict[str, dict]) -> tuple[str, Path, dict]:
    as_of = min(latest_date(results[name]["csv"]) for name in DATED)
    raw_dir = ROOT / "data" / "ati" / as_of / "v03_raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    records = []
    for sheet in CALLS:
        payload = results[sheet]["csv"]
        path = raw_dir / f"{sheet}.csv"
        path.write_text(payload, encoding="utf-8", newline="")
        reread = path.read_text(encoding="utf-8")
        if reread != payload:
            raise RuntimeError(f"snapshot parity failed: {sheet}")
        records.append({
            "sheet": sheet,
            "tool": CALLS[sheet].__name__,
            "rows": results[sheet]["rows"],
            "cols": results[sheet]["cols"],
            "latest_date": latest_date(payload) if sheet in DATED else None,
            "path": path.relative_to(ROOT).as_posix(),
            "sha256": hashlib.sha256(payload.encode("utf-8")).hexdigest(),
            "payload_parity": "PASS",
        })
    manifest = {
        "contract": "ati-raw-snapshot-1.0",
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "as_of": as_of,
        "source": "GS MCP csv payload",
        "mcp_persistence": "temporary CSV deleted after payload read; this directory is the durable snapshot",
        "records": records,
    }
    (raw_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return as_of, raw_dir, manifest


def select_dates(rows: list[dict[str, str]], as_of: str) -> list[str]:
    dates = sorted({r["date"] for r in rows if r.get("date") and r["date"] <= as_of})
    if len(dates) < 11:
        return dates[-3:]
    return [dates[-11], dates[-6], dates[-1]]


def rank_map(row: dict[str, str]) -> dict[str, int]:
    pairs = [(key.removesuffix("_idx"), num(value)) for key, value in row.items() if key.endswith("_idx")]
    pairs = [(name, value) for name, value in pairs if value == value]
    pairs.sort(key=lambda x: x[1], reverse=True)
    return {name: index + 1 for index, (name, _) in enumerate(pairs)}


def configure_plot() -> None:
    plt.rcParams.update({
        "axes.unicode_minus": False,
        "figure.facecolor": "white",
        "axes.facecolor": "#F8FAFC",
        "axes.grid": True,
        "grid.alpha": 0.22,
        "font.size": 10,
    })


def make_charts(as_of: str, raw_dir: Path, out_dir: Path) -> tuple[Path, Path, dict]:
    configure_plot()
    thih = rows_from_csv((raw_dir / "bgd_thih.csv").read_text(encoding="utf-8"))
    q = rows_from_csv((raw_dir / "kidx-Q.csv").read_text(encoding="utf-8"))
    w = rows_from_csv((raw_dir / "kidx-W.csv").read_text(encoding="utf-8"))
    dates = select_dates(thih, as_of)
    by_date = {r["date"]: r for r in thih}
    breadth_cols = [key for key in thih[0] if key.endswith("_idx_ema5diffn")]
    breadth = [sum(num(by_date[d].get(key)) > 0 for key in breadth_cols) for d in dates]

    latest = by_date[dates[-1]]
    ema5 = [num(latest.get(f"{sector}_idx_ema5diffn")) for sector in SECTORS]
    ema20 = [num(latest.get(f"{sector}_idx_ema20diffn")) for sector in SECTORS]

    fig, axes = plt.subplots(2, 1, figsize=(11, 8), constrained_layout=True)
    axes[0].plot(dates, breadth, marker="o", lw=3, color="#2563EB")
    axes[0].set_ylim(0, len(breadth_cols) + 2)
    axes[0].set_ylabel(f"EMA5 양수 섹터 수 / {len(breadth_cols)}", fontproperties=FONT)
    axes[0].set_title("시장 상승 참여 폭 — 숫자가 클수록 더 많은 섹터가 단기 상승", fontproperties=BOLD)
    for x, y in zip(dates, breadth):
        axes[0].annotate(f"{y}/{len(breadth_cols)}", (x, y), xytext=(0, 8), textcoords="offset points", ha="center", fontproperties=FONT)
    x = range(len(SECTORS)); width = 0.36
    axes[1].bar([i - width / 2 for i in x], ema5, width, label="EMA5 차이: 최근 방향", color="#2563EB")
    axes[1].bar([i + width / 2 for i in x], ema20, width, label="EMA20 차이: 중기 방향", color="#94A3B8")
    axes[1].axhline(0, color="#0F172A", lw=1)
    axes[1].set_xticks(list(x), SECTORS, fontproperties=FONT)
    axes[1].set_ylabel("GS 원자료 차이값 (0 위=상승, 0 아래=하락)", fontproperties=FONT)
    axes[1].set_title(f"관심 섹터 방향 — {as_of}", fontproperties=BOLD)
    axes[1].legend(prop=FONT)
    fig.suptitle("질문 1: 시장 회복이 넓은가, 어떤 섹터가 꺾이는가?", fontproperties=BOLD, fontsize=15)
    breadth_path = out_dir / f"ATI_v03_breadth_{as_of}.png"
    fig.savefig(breadth_path, dpi=180); plt.close(fig)

    q_row = max((r for r in q if r.get("date") and r["date"] <= as_of), key=lambda r: r["date"])
    w_row = max((r for r in w if r.get("date") and r["date"] <= as_of), key=lambda r: r["date"])
    q_rank, w_rank = rank_map(q_row), rank_map(w_row)
    qv = [q_rank.get(s) for s in SECTORS]; wv = [w_rank.get(s) for s in SECTORS]
    fig, ax = plt.subplots(figsize=(11, 6), constrained_layout=True)
    y = list(range(len(SECTORS)))
    for yi, qr, wr in zip(y, qv, wv):
        if qr is None or wr is None: continue
        ax.plot([qr, wr], [yi, yi], color="#CBD5E1", lw=5, zorder=1)
        ax.scatter(qr, yi, s=110, color="#64748B", label="Q 순위: 중기" if yi == 0 else None, zorder=2)
        ax.scatter(wr, yi, s=110, color="#F97316", label="W 순위: 최근" if yi == 0 else None, zorder=2)
        ax.text(qr, yi + .18, str(qr), ha="center", fontsize=9)
        ax.text(wr, yi - .28, str(wr), ha="center", fontsize=9)
    ax.set_yticks(y, SECTORS, fontproperties=FONT)
    ax.set_xlim(24, 0)
    ax.set_xlabel("섹터 순위 — 오른쪽일수록 강함 (1위가 최강)", fontproperties=FONT)
    ax.set_title("질문 2: 중기 강도(Q)와 최근 강도(W)가 같은 방향인가?", fontproperties=BOLD, fontsize=15)
    ax.legend(prop=FONT, loc="lower right")
    rank_path = out_dir / f"ATI_v03_rank_{as_of}.png"
    fig.savefig(rank_path, dpi=180); plt.close(fig)

    facts = {
        "dates": dates,
        "breadth": breadth,
        "breadth_total": len(breadth_cols),
        "ema5": dict(zip(SECTORS, ema5)),
        "ema20": dict(zip(SECTORS, ema20)),
        "q_rank": dict(zip(SECTORS, qv)),
        "w_rank": dict(zip(SECTORS, wv)),
    }
    return breadth_path, rank_path, facts


def add_text(fig, x: float, y: float, text: str, size: float = 10, bold: bool = False, color: str = "#0F172A") -> None:
    fig.text(x, y, text, fontsize=size, fontproperties=BOLD if bold else FONT, color=color, va="top", linespacing=1.5)


def build_pdf(as_of: str, out_dir: Path, manifest: dict, chart1: Path, chart2: Path, facts: dict) -> Path:
    pdf_path = out_dir / f"ATI_Morning_Report_v0.3_{as_of}.pdf"
    latest_breadth = facts["breadth"][-1]
    breadth_ratio = latest_breadth / facts["breadth_total"]
    if breadth_ratio >= .75:
        breadth_state = "상승 참여 폭이 넓음"
        breadth_action = "시장 환경은 우호적이지만, 이 값만으로 신규 노출을 확대하지 않는다."
    elif breadth_ratio <= .25:
        breadth_state = "상승 참여 폭이 급격히 위축"
        breadth_action = "신규 추격을 보류하고 기존 노출의 위험 요인을 우선 점검한다."
    else:
        breadth_state = "상승 참여 폭이 혼조"
        breadth_action = "섹터별 확인 전 시장 전체 방향으로 일반화하지 않는다."
    weakening = [s for s in SECTORS if facts["ema5"][s] < 0 <= facts["ema20"][s]]
    best_recent = min((r, s) for s, r in facts["w_rank"].items() if r is not None)[1]
    with PdfPages(pdf_path) as pdf:
        fig = plt.figure(figsize=(8.27, 11.69)); fig.patch.set_facecolor("white")
        add_text(fig, .07, .95, "ATI Morning Report v0.3", 21, True)
        add_text(fig, .07, .905, f"기준일 {as_of} | GS MCP raw snapshot 기반", 10, False, "#475569")
        add_text(fig, .07, .84, "한눈에 보는 결론", 15, True, "#1D4ED8")
        add_text(fig, .08, .79, f"시장: {facts['breadth_total']}개 중 {latest_breadth}개 섹터만 EMA5 양수 — {breadth_state}.", 12, True)
        add_text(fig, .08, .72, f"최근 강도: {best_recent}의 W 순위가 관심 섹터 중 가장 높음.", 12, True)
        risk_text = ", ".join(weakening) if weakening else "EMA5<0·EMA20≥0 조합 없음"
        add_text(fig, .08, .65, f"경계: {risk_text} — 중기는 양수지만 최근 방향이 꺾인 조기경보.", 12, True, "#B45309")
        add_text(fig, .07, .54, "오늘의 행동", 15, True, "#1D4ED8")
        add_text(fig, .08, .49, f"WATCHLIST ONLY. {breadth_action} 이 자료만으로 비중·목표수익률·매매 주문을 확정하지 않는다.", 12, True)
        add_text(fig, .07, .36, "읽는 법", 15, True, "#1D4ED8")
        add_text(fig, .08, .31, "EMA5/20 차이값: 0보다 크면 해당 기간의 상승 방향, 0보다 작으면 하락 방향.\nQ/W 순위: 1위가 가장 강함. Q는 중기, W는 최근 흐름을 비교하는 관찰값.\nCONDITIONAL은 상태 설명만 허용하며, 미래수익이나 매매 유효성을 뜻하지 않음.", 10.5)
        add_text(fig, .07, .14, "검증 상태: Regime/Turning CONDITIONAL | Leadership/Rotation/Risk 규칙 REJECT | Entry/Build/Exit UNVERIFIED", 9.5, True, "#7C2D12")
        pdf.savefig(fig); plt.close(fig)

        for title, image, meaning, action in [
            ("시장 참여 폭과 섹터 방향", chart1, "위 차트는 시장 회복의 폭, 아래 차트는 관심 섹터의 최근·중기 방향을 보여준다.", "회복 폭은 시장 환경 판단에만 사용. 최근 음수 전환 섹터는 추격하지 않고 원인 확인."),
            ("Q/W 순위 충돌", chart2, "Q와 W가 가까우면 중기·최근 흐름이 일치한다. W가 Q보다 강하면 최근 가속, 약하면 최근 둔화다.", "순위는 후보 선별용이다. forward return 검증 전에는 매수·매도 규칙으로 승격하지 않는다."),
        ]:
            fig = plt.figure(figsize=(8.27, 11.69)); fig.patch.set_facecolor("white")
            add_text(fig, .07, .95, title, 18, True)
            add_text(fig, .07, .895, f"무엇을 묻나: {meaning}", 10.5, True, "#1D4ED8")
            ax = fig.add_axes([.07, .27, .86, .56]); ax.imshow(plt.imread(image)); ax.axis("off")
            add_text(fig, .07, .21, f"CIO Action: {action}", 10.5, True)
            add_text(fig, .07, .105, f"Source: GS MCP raw snapshot | as-of {as_of} | 계산·단위 정의는 차트 안에 표시", 8.5, False, "#64748B")
            pdf.savefig(fig); plt.close(fig)

        fig = plt.figure(figsize=(8.27, 11.69)); fig.patch.set_facecolor("white")
        add_text(fig, .07, .95, "데이터 계보와 한계", 18, True)
        add_text(fig, .07, .88, "Raw 보존", 14, True, "#1D4ED8")
        add_text(fig, .08, .835, "GS MCP는 임시 CSV를 생성하고 payload로 읽은 뒤 삭제한다. v0.3는 반환 payload를 날짜별 UTF-8 CSV로 그대로 저장하고 SHA-256과 행·열 수를 manifest에 기록했다.", 10.5)
        add_text(fig, .07, .70, "사용 데이터", 14, True, "#1D4ED8")
        summary = "\n".join(f"• {r['sheet']}: {r['rows']}행 × {r['cols']}열, parity {r['payload_parity']}" for r in manifest["records"])
        add_text(fig, .08, .655, summary, 9.5)
        add_text(fig, .07, .40, "현재 한계", 14, True, "#1D4ED8")
        add_text(fig, .08, .355, "• Q/W·EMA는 상태 관찰값이며 수익률이 아니다.\n• 유효일자별 섹터 구성, 구성종목 수정주가, 시장·섹터 total return이 부족하다.\n• 따라서 Exposure sizing, 기대수익, Entry/Build/Exit 규칙은 검증되지 않았다.\n• 차트는 설명을 돕지만 REJECT된 규칙을 되살리지 않는다.", 10.5)
        add_text(fig, .07, .14, "품질 판정: raw lineage PASS | 차트 단위·읽는 법 PASS | 투자규칙 검증 HOLD", 10.5, True, "#7C2D12")
        pdf.savefig(fig); plt.close(fig)
    return pdf_path


def main() -> None:
    results = acquire()
    as_of, raw_dir, manifest = persist(results)
    out_dir = ROOT / "reports" / "assets" / "ati_v03" / as_of
    out_dir.mkdir(parents=True, exist_ok=True)
    chart1, chart2, facts = make_charts(as_of, raw_dir, out_dir)
    pdf = build_pdf(as_of, out_dir, manifest, chart1, chart2, facts)
    audit = {"as_of": as_of, "raw_dir": str(raw_dir), "pdf": str(pdf), "facts": facts}
    (out_dir / "audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "as_of": as_of, "pdf": str(pdf), "raw_dir": str(raw_dir)}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
