"""Read-only checker for reports/NNN_report.md's Report §0 (reports/README.md).

Required fields, in order: 상태, 좌표, PC1 경로, 커밋, 요약. This validates
structure only -- it does not judge whether the content is true, and it
never modifies anything. PEV runner step 4 (2026-08-22).
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

COMMON_ROOT = Path(r"C:\lab\vsurf_capital\common")
REPORTS_DIR = COMMON_ROOT / "reports"
REQUIRED_FIELDS = ("상태", "좌표", "PC1 경로", "커밋", "요약")
VALID_STATUS_VALUES = ("DONE", "FAIL", "부분완료")
FIELD_RE = re.compile(r"^-\s*(상태|좌표|PC1 경로|커밋|요약)\s*:\s*(.+?)\s*$", re.MULTILINE)


@dataclass
class ValidationResult:
    path: str
    passed: bool
    missing_fields: list[str]
    status_value: str | None
    status_value_recognized: bool


def find_report_path(order_id: str) -> Path | None:
    candidates = sorted(REPORTS_DIR.glob(f"{order_id}_*.md"))
    if len(candidates) == 1:
        return candidates[0]
    return None


def validate_report(path: Path) -> ValidationResult:
    text = path.read_text(encoding="utf-8")
    fields = dict(FIELD_RE.findall(text))
    missing = [name for name in REQUIRED_FIELDS if name not in fields]
    status_value = fields.get("상태")
    status_recognized = status_value in VALID_STATUS_VALUES if status_value else False
    passed = not missing and status_recognized
    return ValidationResult(
        path=str(path), passed=passed, missing_fields=missing,
        status_value=status_value, status_value_recognized=status_recognized,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--order-id", help="report is reports/<order-id>_*.md")
    source.add_argument("--path", help="explicit report file path")
    args = parser.parse_args(argv)

    if args.path:
        path = Path(args.path)
    else:
        path = find_report_path(args.order_id)
        if path is None:
            print(f"NOT FOUND: reports/{args.order_id}_*.md does not resolve to exactly one file")
            return 2

    if not path.is_file():
        print(f"NOT FOUND: {path}")
        return 2

    result = validate_report(path)
    print(f"PASS: {result.path}" if result.passed else f"FAIL: {result.path}")
    if result.missing_fields:
        print(f"  missing fields: {', '.join(result.missing_fields)}")
    if result.status_value and not result.status_value_recognized:
        print(f"  상태 value not recognized: {result.status_value!r} (expected one of {VALID_STATUS_VALUES})")
    return 0 if result.passed else 1


if __name__ == "__main__":
    sys.exit(main())
