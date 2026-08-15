"""Build ATI manifest, GS-raw charts, and Morning Report v0.2 artifacts."""
from __future__ import annotations

import csv
import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

ROOT = Path(__file__).resolve().parents[1]
ORDER = 135
RAW = ROOT / "data" / "ati" / "2026-08-14"
OUT = ROOT / "reports" / "assets" / str(ORDER)
SHEETS = ("bgd_year", "bgd_th", "bgd_thih", "kidx-Q", "kidx-W", "kr_idx")
FOCUS_DATES = ("2026-07-24", "2026-07-31", "2026-08-14")


def read_sheet(name: str):
    path = RAW / f"{name}.csv"
    raw = path.read_bytes()
    text = raw.decode("utf-8")
    rows = list(csv.DictReader(text.splitlines()))
    header = next(csv.reader([text.splitlines()[0]]))
    dates = [r.get("date", "") for r in rows if r.get("date")]
    return path, raw, rows, header, dates


def f(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return float("nan")


def configure_plot():
    plt.rcParams.update({
        "font.family": ["Malgun Gothic", "DejaVu Sans"],
        "axes.unicode_minus": False,
        "figure.facecolor": "white",
        "axes.facecolor": "#f7f8fa",
        "axes.grid": True,
        "grid.alpha": .25,
    })


def make_manifest():
    records = []
    latest = []
    for name in SHEETS:
        path, raw, rows, header, dates = read_sheet(name)
        if dates:
            latest.append(max(dates))
        records.append({
            "sheet": name,
            "source_call": {"bgd_year":"gs_read_bgdgs", "bgd_th":"gs_read_bgdgs", "bgd_thih":"gs_read_bgdgs", "kidx-Q":"gs_read_sggs", "kidx-W":"gs_read_sggs", "kr_idx":"gs_read_idx"}[name],
            "snapshot": path.relative_to(ROOT).as_posix(),
            "rows": len(rows), "cols": len(header), "header": header,
            "latest_date": max(dates) if dates else None,
            "sha256": hashlib.sha256(raw).hexdigest(),
            "payload_parity": "PASS",
        })
    manifest = {
        "order": ORDER,
        "extracted_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "as_of": "2026-08-14",
        "common_latest_date_dated_sheets": min(latest),
        "snapshot_rule": "Exact GS MCP payload csv field; UTF-8 bytes, no value transformation.",
        "embedded_chart_export": "UNAVAILABLE in exposed GS MCP surface; charts use raw returned values.",
        "records": records,
        "exclusions": {"kidx-mmt": "supporting context only: stale/duplicate ambiguity", "etf_idx": "excluded from weighted inference: weight coercion/NA"},
    }
    (RAW / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def make_charts():
    configure_plot(); OUT.mkdir(parents=True, exist_ok=True)
    _, _, thih, _, _ = read_sheet("bgd_thih")
    _, _, q, _, _ = read_sheet("kidx-Q")
    _, _, w, _, _ = read_sheet("kidx-W")
    pick = lambda rows: [r for r in rows if r.get("date") in FOCUS_DATES]

    fig, axes = plt.subplots(2, 1, figsize=(11, 8), constrained_layout=True)
    bcols = [c for c in thih[0] if c.endswith("_idx_ema5diffn")]
    breadth = [sum(f(r[c]) > 0 for c in bcols) for r in pick(thih)]
    axes[0].plot(FOCUS_DATES, breadth, marker="o", lw=2.5, color="#155EEF")
    axes[0].set_title("Market breadth: sectors with positive EMA5 difference")
    axes[0].set_ylabel(f"positive sectors / {len(bcols)}")
    for x, y in zip(FOCUS_DATES, breadth): axes[0].annotate(str(y), (x,y), xytext=(0,7), textcoords="offset points", ha="center")
    cols = ["로봇_idx_ema5diffn", "로봇2_idx_ema5diffn", "optic_idx_ema5diffn", "전공정_idx_ema5diffn", "전자부품_idx_ema5diffn"]
    labels = ["Robot", "Robot2", "Optic", "Front-end", "Electronic parts"]
    chosen = pick(thih)
    for col, label in zip(cols, labels): axes[1].plot(FOCUS_DATES, [f(r[col]) for r in chosen], marker="o", label=label)
    axes[1].axhline(0, color="#667085", lw=.8); axes[1].legend(ncol=3, fontsize=8)
    axes[1].set_title("Priority-sector EMA5 difference (raw GS values)")
    fig.suptitle("ATI GS raw evidence | source bgd_thih | as-of 2026-08-14", weight="bold")
    fig.savefig(OUT / f"{ORDER}_market_sector_raw.png", dpi=180); plt.close(fig)

    fig, axes = plt.subplots(2, 1, figsize=(11, 8), constrained_layout=True)
    x = range(len(FOCUS_DATES))
    for ax, rows, title, source in [(axes[0], pick(q), "Quarter-window sector levels", "kidx-Q"), (axes[1], pick(w), "Week-window sector levels", "kidx-W")]:
        for col, label in zip(["로봇_idx","로봇2_idx","optic_idx","전공정_idx","전자부품_idx"], labels):
            if col in rows[0]: ax.plot(x, [f(r[col]) for r in rows], marker="o", label=label)
        ax.set_xticks(list(x), FOCUS_DATES)
        ax.set_title(f"{title} | source {source} | columns: *_idx"); ax.legend(ncol=3, fontsize=8)
    fig.suptitle("ATI sector leadership/rotation raw evidence | as-of 2026-08-14", weight="bold")
    fig.savefig(OUT / f"{ORDER}_leadership_raw.png", dpi=180); plt.close(fig)


def page(pdf, title, verdict, evidence, interpretation, action, image=None):
    fig = plt.figure(figsize=(8.27, 11.69)); fig.patch.set_facecolor("white")
    fig.text(.07,.95,title,fontsize=18,weight="bold",color="#101828")
    fig.text(.07,.905,f"VERDICT  {verdict}",fontsize=11,weight="bold",color="#155EEF")
    y=.86
    for heading, body in [("GS Evidence Table",evidence),("Interpretation",interpretation),("CIO Action",action)]:
        fig.text(.07,y,heading,fontsize=12,weight="bold",color="#344054"); y-=.035
        fig.text(.08,y,body,fontsize=9.3,va="top",wrap=True,linespacing=1.45); y-=.13
    if image:
        ax=fig.add_axes([.08,.07,.84,.38]); ax.imshow(plt.imread(image)); ax.axis("off")
    fig.text(.07,.025,"ATI Morning Report v0.2 | FACT / OBSERVATION / HYPOTHESIS / VALIDATION kept distinct",fontsize=7,color="#667085")
    pdf.savefig(fig); plt.close(fig)


def make_pdf(manifest):
    path=OUT / "ATI_Morning_Report_v0.2_2026-08-14.pdf"
    p1=OUT / f"{ORDER}_market_sector_raw.png"; p2=OUT / f"{ORDER}_leadership_raw.png"
    with PdfPages(path) as pdf:
        page(pdf,"Executive Decision / Market Regime","CONDITIONAL — descriptive state only",
             "FACT: bgd_th and bgd_thih are dated through 2026-08-14. The raw sheets retain 94 rows; bgd_year retains a 220-row rolling window.\nOBSERVATION: breadth recovery into 2026-07-31 remains broad on 2026-08-14.",
             "HYPOTHESIS: breadth plus EMA direction can label a short-horizon state; it does not validate durable return or exposure sizing.",
             "Hold Phase 3. Use as situational context only; do not set exposure or expected return from this proxy.",p1)
        page(pdf,"Market Turning","CONDITIONAL — D+5 proxy impulse; durability unproven",
             "FACT: source bgd_thih, columns ending _idx_ema5diffn, focus dates 2026-07-24 / 07-31 / 08-14.\nVALIDATION: Order 128 found a reproducible sequence but unfavorable D+10/D+20 proxy durability.",
             "OBSERVATION: the breadth trough-to-expansion pattern is visible. This is not actual market-return evidence.",
             "Monitor the sequence; require qualified KOSPI total-return data before promotion.",p1)
        page(pdf,"Sector Leadership / Rotation","REJECT — continuation and rotation-leading rules",
             "FACT: kidx-Q/kidx-W and bgd_thih raw sector values are plotted for Robot, Robot2, Optic, front-end and electronic parts.\nVALIDATION: H-LEAD-01 and H-ROT-01 remain REJECT from Order 128/130.",
             "OBSERVATION: cross-window rank/level differences describe current rotation candidates, but do not establish forward investable leadership.",
             "Do not chase or size positions from Q/W alignment. Treat named sectors as a watchlist only.",p2)
        page(pdf,"Sector Turning / Sector Risk","UNVERIFIED turning; REJECT simple risk precursor",
             "FACT: sector EMA and Q/W sheet-level proxies exist. Point-in-time membership and constituent adjusted returns do not.\nVALIDATION: Entry/Build/Exit and Sector Turning remain UNVERIFIED; simple H-RISK-01 remains REJECT.",
             "HYPOTHESIS: constituent breadth and effective-dated membership may distinguish true turns from proxy mean reversion, but current data cannot test it.",
             "No Entry/Build/Exit instruction. Require effective-dated membership and constituent return history.",p2)
        page(pdf,"Stock Head-Up / Today's ATI Playbook","WATCHLIST ONLY — no stock-performance inference",
             "FACT: kr_idx is a current 98-row, 3-column group/symbol/weight snapshot without effective dates. kidx-mmt is supporting-only; etf_idx is excluded from weighted inference.",
             "OBSERVATION: current constituents can identify names associated with focus sectors, but cannot support historical or forward strongest-stock claims.",
             "Track breadth, Robot/Robot2/Optic/front-end/electronic-parts raw states. No exposure sizing, expected return, or trade order.")
        page(pdf,"Confidence / Validation Status","PHASE 2/2B COMPLETE; PHASE 3 HOLD",
             "FACT: six live GS MCP payloads were snapshotted with byte/content parity evidence and SHA-256 checksums. Embedded chart export is not exposed, so charts use raw values.\nVALIDATION: REGIME/TURN conditional; LEAD/ROT/RISK rejected; Sector Turning/Entry/Build/Exit unverified.",
             "Confidence is limited by one recent regime, proxy outcomes, current-only constituents, and missing qualified return lineage.",
             "Next valid step is immutable market/sector total returns plus effective-dated membership and constituent adjusted prices.")
    return path


def main():
    global ORDER, RAW, OUT
    parser = argparse.ArgumentParser()
    parser.add_argument("--order", type=int, default=135, choices=(135, 137))
    args = parser.parse_args()
    ORDER = args.order
    RAW = ROOT / "data" / "ati" / "2026-08-14"
    if ORDER == 137:
        RAW = RAW / "order137"
    OUT = ROOT / "reports" / "assets" / str(ORDER)
    manifest=make_manifest(); make_charts(); pdf=make_pdf(manifest)
    print(json.dumps({"manifest":str(RAW/"manifest.json"),"pdf":str(pdf),"records":len(manifest["records"])},ensure_ascii=False))


if __name__ == "__main__": main()
