"""Fetch 사업의 개요 for consensus-uncovered QoQ TOP100."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, r"C:\autoai\dart-toolkit")
import dart_batch as B  # noqa: E402

ROWS = json.loads(Path(r"C:\lab\vsurf_capital\common\data\skill_top100_table.json").read_text(encoding="utf-8"))
OUT = Path(r"C:\lab\vsurf_capital\common\data\skill_top100_biz.json")


def preview(md: str, n: int = 700) -> str:
    t = " ".join((md or "").split())
    return t[:n]


def main() -> None:
    existing = {}
    if OUT.exists():
        existing = {r["code"]: r for r in json.loads(OUT.read_text(encoding="utf-8"))}

    results = []
    data = [r for r in ROWS if r[0] != "#"]
    for rank, name, code, date, q2, q1, qoq in data:
        ticker = code.replace("A", "")
        if ticker in existing and existing[ticker].get("biz"):
            results.append(existing[ticker])
            continue
        rec = {
            "rank": int(rank),
            "name": name,
            "code": ticker,
            "date": date,
            "q2": q2,
            "q1": q1,
            "qoq": qoq,
        }
        try:
            ov = B.company_overview(ticker).get("data") or {}
            rec["induty_code"] = ov.get("induty_code")
            rec["corp_cls"] = ov.get("corp_cls")
        except Exception as e:
            rec["overview_error"] = str(e)
        try:
            sec = B.report_section(ticker, 2026, "1. 사업의 개요", reprt_code="11012", mode="children")
            md_path = sec.get("markdown_file")
            text = Path(md_path).read_text(encoding="utf-8", errors="replace") if md_path else ""
            rec["biz"] = preview(text)
            rec["rcept_no"] = sec.get("rcept_no")
        except Exception as e:
            rec["biz_error"] = str(e)
            # fallback
            try:
                sec = B.report_section(ticker, 2026, "2. 주요 제품 및 서비스", reprt_code="11012", mode="children")
                md_path = sec.get("markdown_file")
                text = Path(md_path).read_text(encoding="utf-8", errors="replace") if md_path else ""
                rec["biz"] = preview(text)
                rec["biz_src"] = "주요 제품"
            except Exception as e2:
                rec["biz2_error"] = str(e2)
        results.append(rec)
        print(f"{rank} {name} biz={bool(rec.get('biz'))}", flush=True)
        time.sleep(0.2)
        if int(rank) % 10 == 0:
            OUT.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    OUT.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote", OUT, "n", len(results))


if __name__ == "__main__":
    main()
