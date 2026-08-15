"""Minimal, review-gated IVK v2 causal records used by Order 127."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

VALID_STATUS = {"fact", "inference", "hypothesis"}
VALID_REVIEW = {"pending", "accepted", "rejected", "deferred"}


@dataclass(frozen=True)
class CausalRecord:
    id: str
    kind: str
    company_id: str
    period: str
    affected_metric: str
    direction: str
    lag: str
    source: str
    evidence: str
    confidence: float
    counter_evidence: str
    status: str
    review_status: str = "pending"

    def validate(self) -> None:
        if self.kind not in {"EarningsDriverLink", "Bottleneck", "BeneficiaryAssessment"}:
            raise ValueError(f"unsupported causal kind: {self.kind}")
        if self.status not in VALID_STATUS or self.review_status not in VALID_REVIEW:
            raise ValueError("invalid status or review_status")
        if not self.source.strip() or not self.evidence.strip():
            raise ValueError("source and evidence are required")
        if not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be between 0 and 1")
        if self.review_status == "accepted" and self.status != "fact":
            raise ValueError("inference/hypothesis cannot be auto-accepted")


def load_records(path: str | Path) -> list[CausalRecord]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    records = [CausalRecord(**item) for item in raw]
    for record in records:
        record.validate()
    ids = [record.id for record in records]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate causal record id")
    return records


def query(records: Iterable[CausalRecord], *, company_id: str | None = None,
          kind: str | None = None) -> list[dict]:
    return [asdict(r) for r in records
            if (company_id is None or r.company_id == company_id)
            and (kind is None or r.kind == kind)]
