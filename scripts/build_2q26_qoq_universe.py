"""Rebuild 2026-08-13/14 반기보고서 QoQ sales universe from OpenDART.

Filter: listed (KOSPI/KOSDAQ), 1Q sales >= 50억원, compute 2Q = H1 - 1Q.
"""
from __future__ import annotations

import json
import os
import time
import urllib.parse
import urllib.request
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(r"C:\autoai\dart-toolkit\.env")
API_KEY = os.environ["OPEN_DART_API_KEY"]
OUT = Path(r"C:\lab\vsurf_capital\common\data\2q26_qoq_universe.json")
CACHE = Path(r"C:\lab\vsurf_capital\common\data\2q26_fin_cache.json")


def get(url: str, params: dict) -> dict:
    q = urllib.parse.urlencode(params)
    req = urllib.request.Request(
        f"{url}?{q}",
        headers={"User-Agent": "vsurf-research/1.0"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def list_filings() -> list[dict]:
    rows = []
    for cls in ("Y", "K"):
        page = 1
        while True:
            data = get(
                "https://opendart.fss.or.kr/api/list.json",
                {
                    "crtfc_key": API_KEY,
                    "bgn_de": "20260813",
                    "end_de": "20260814",
                    "pblntf_ty": "A",
                    "pblntf_detail_ty": "A002",
                    "corp_cls": cls,
                    "page_count": "100",
                    "page_no": str(page),
                },
            )
            if data.get("status") not in {"000", "013"}:
                raise RuntimeError(f"list fail {cls} p{page}: {data}")
            chunk = data.get("list") or []
            rows.extend(chunk)
            total = int(data.get("total_page") or 1)
            print(f"list {cls} page {page}/{total} +{len(chunk)}", flush=True)
            if page >= total or not chunk:
                break
            page += 1
            time.sleep(0.15)
    return rows


def pick_revenue(items: list[dict]) -> dict | None:
    if not items:
        return None
    # prefer 연결 매출액
    def score(row):
        name = str(row.get("account_nm") or "")
        fs = str(row.get("fs_div") or "")
        s = 0
        if name == "매출액":
            s += 10
        elif "매출" in name and "매출원가" not in name:
            s += 5
        if fs == "CFS":
            s += 3
        return s

    best = max(items, key=score)
    amt = str(best.get("thstrm_amount") or "").replace(",", "").replace("-", "")
    if amt == "":
        # allow negative sales? treat as None
        raw = str(best.get("thstrm_amount") or "").replace(",", "")
        try:
            val = int(raw)
        except ValueError:
            return None
    else:
        raw = str(best.get("thstrm_amount") or "").replace(",", "")
        try:
            val = int(raw)
        except ValueError:
            return None
    return {
        "account_nm": best.get("account_nm"),
        "fs_nm": best.get("fs_nm"),
        "fs_div": best.get("fs_div"),
        "amount": val,
    }


def fetch_fin(corp_code: str, reprt_code: str, cache: dict) -> dict | None:
    key = f"{corp_code}:{reprt_code}"
    if key in cache:
        return cache[key]
    data = get(
        "https://opendart.fss.or.kr/api/fnlttSinglAcnt.json",
        {
            "crtfc_key": API_KEY,
            "corp_code": corp_code,
            "bsns_year": "2026",
            "reprt_code": reprt_code,
        },
    )
    status = data.get("status")
    if status == "013":
        cache[key] = None
        return None
    if status != "000":
        cache[key] = {"error": data}
        return cache[key]
    picked = pick_revenue(data.get("list") or [])
    cache[key] = picked
    return picked


def main() -> None:
    cache = {}
    if CACHE.exists():
        cache = json.loads(CACHE.read_text(encoding="utf-8"))

    filings = list_filings()
    latest = {}
    for row in filings:
        code = (row.get("stock_code") or "").strip()
        if not code:
            continue
        name = row.get("corp_name")
        # skip amendments later only if we already have one; keep last rcept
        prev = latest.get(code)
        if prev is None or row.get("rcept_dt", "") >= prev.get("rcept_dt", ""):
            latest[code] = row

    print(f"unique listed filers: {len(latest)}", flush=True)
    results = []
    for i, (stock, row) in enumerate(latest.items(), 1):
        corp = row["corp_code"]
        h1 = fetch_fin(corp, "11012", cache)
        q1 = fetch_fin(corp, "11013", cache)
        time.sleep(0.12)
        if i % 25 == 0:
            CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
            print(f"fin {i}/{len(latest)}", flush=True)
        rec = {
            "stock_code": stock,
            "corp_code": corp,
            "corp_name": row.get("corp_name"),
            "corp_cls": row.get("corp_cls"),
            "rcept_dt": row.get("rcept_dt"),
            "report_nm": row.get("report_nm"),
            "h1": h1,
            "q1": q1,
        }
        if (
            isinstance(h1, dict)
            and isinstance(q1, dict)
            and "amount" in h1
            and "amount" in q1
            and h1.get("fs_div") == q1.get("fs_div")
        ):
            q2 = h1["amount"] - q1["amount"]
            rec["q2_amount"] = q2
            rec["q1_amount"] = q1["amount"]
            rec["h1_amount"] = h1["amount"]
            rec["fs_div"] = h1.get("fs_div")
            if q1["amount"] > 0:
                rec["qoq"] = q2 / q1["amount"] - 1
        results.append(rec)

    CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")

    eligible = [
        r
        for r in results
        if r.get("q1_amount") is not None
        and r["q1_amount"] >= 5_000_000_000
        and r.get("qoq") is not None
    ]
    eligible.sort(key=lambda x: x["qoq"], reverse=True)
    top100 = eligible[:100]
    payload = {
        "asof": "2026-08-18",
        "window": ["2026-08-13", "2026-08-14"],
        "unique_filers": len(latest),
        "eligible_1q_ge_50bn": len(eligible),
        "top100": top100,
        "all_eligible": eligible,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"eligible={len(eligible)} wrote {OUT}")
    for i, r in enumerate(top100[:15], 1):
        print(
            f"{i:3} {r['corp_name']:16} {r['stock_code']} "
            f"Q2={r['q2_amount']/1e8:.0f} Q1={r['q1_amount']/1e8:.0f} "
            f"QoQ={r['qoq']*100:.1f}%"
        )


if __name__ == "__main__":
    main()
