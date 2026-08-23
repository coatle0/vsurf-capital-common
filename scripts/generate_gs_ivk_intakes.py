"""Generate IVK intake JSON files from normalized GS index CSV snapshots."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path


def slugify(value: str) -> str:
    value = re.sub(r"_idx$", "", value, flags=re.IGNORECASE)
    value = re.sub(r"[^0-9A-Za-z가-힣]+", "_", value).strip("_").lower()
    if not value:
        raise ValueError("group name cannot produce an empty slug")
    return value


def read_groups(path: Path) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = defaultdict(list)
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != ["group", "symbol", "weight"]:
            raise ValueError(f"unexpected CSV contract: {reader.fieldnames}")
        for row in reader:
            group = row["group"].strip()
            symbol = row["symbol"].strip()
            if not group or not symbol:
                raise ValueError("group and symbol must not be empty")
            if symbol in groups[group]:
                raise ValueError(f"duplicate symbol within {group}: {symbol}")
            groups[group].append(symbol)
    return dict(groups)


def build_intake(*, market: str, sheet: str, group: str, seeds: list[str]) -> dict:
    label = re.sub(r"_idx$", "", group, flags=re.IGNORECASE)
    market_name = "US" if market == "us" else "Korea"
    return {
        "contract_version": "ivk-intake-1.0",
        "operation": "new",
        "target_vc": None,
        "name": f"{market_name} {label} Ecosystem",
        "seed": seeds,
        "frame": "matrix",
        "thesis": (
            f"{group} 구성 기업은 공통 산업·수요 동인에 노출될 가능성이 있으며, "
            "기업별 제품·기능·실적 차이를 비교해 실제 Value Chain 연결, 병목 및 수혜 강도를 검증한다."
        ),
        "questions": [
            "각 seed 기업의 핵심 제품, 기능 및 Value Chain 역할은 무엇인가?",
            "기업들이 공유하는 수요동인과 End Market은 무엇인가?",
            "핵심 공정·제품·기술 병목은 어디에 있는가?",
            "병목의 직접 및 간접 수혜기업은 누구인가?",
            "최근 5분기 실적, 사업부, 재고, 마진 및 증설에서 가설이 확인되는가?",
            "추가 조사하거나 제외해야 할 인접 기업과 연결은 무엇인가?",
        ],
        "scope": [
            "value_chain",
            "products",
            "processes",
            "technologies",
            "end_markets",
            "financials",
            "segment_results",
            "inventory",
            "capex",
            "earnings_call",
            "counter_evidence",
            "link_expansion",
        ],
        "known_links": [],
        "limitations": [
            f"{sheet}의 {group} 편입은 조사 출발점이며 기업 간 공급·경쟁 관계를 입증하지 않는다.",
            "Seed는 최종 Value Chain 경계가 아니며 evidence에 따라 추가·제외할 수 있다.",
            "모든 관계는 공시, 어닝콜 또는 신뢰할 수 있는 원문 근거로 검증해야 한다.",
            "근거와 review 없이 후보를 confirmed로 자동 승격하지 않는다.",
        ],
        "references": [f"gs://signals/{sheet}/{group}"],
        "options": {
            "periods": 5,
            "auto_expand": True,
            "write_policy": "approval_required",
        },
    }


def write_intakes(*, market: str, sheet: str, csv_path: Path, output_dir: Path) -> list[Path]:
    written: list[Path] = []
    output_dir.mkdir(parents=True, exist_ok=True)
    for group, seeds in read_groups(csv_path).items():
        target = output_dir / f"{market}_{slugify(group)}.json"
        payload = json.dumps(
            build_intake(market=market, sheet=sheet, group=group, seeds=seeds),
            ensure_ascii=False,
            indent=2,
        ) + "\n"
        if target.exists() and target.read_text(encoding="utf-8") != payload:
            raise FileExistsError(f"refusing to overwrite changed intake: {target}")
        target.write_text(payload, encoding="utf-8")
        written.append(target)
    return written


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--us-csv", type=Path, required=True)
    parser.add_argument("--kr-csv", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    files = []
    files += write_intakes(
        market="us", sheet="us_idx", csv_path=args.us_csv, output_dir=args.output_dir
    )
    files += write_intakes(
        market="kr", sheet="kr_idx", csv_path=args.kr_csv, output_dir=args.output_dir
    )
    print(json.dumps({"ok": True, "files": len(files)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
