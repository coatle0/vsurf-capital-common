// Review-gated migration/loader template. Execute only after human approval.
CREATE CONSTRAINT causal_assertion_id IF NOT EXISTS
FOR (n:CausalAssertion) REQUIRE n.id IS UNIQUE;

// $rows must already pass scripts/ivk_v2.py validation.
UNWIND $rows AS row
WITH row WHERE row.kind IN ['EarningsDriverLink','Bottleneck','BeneficiaryAssessment']
  AND row.status IN ['fact','inference','hypothesis']
  AND row.review_status IN ['pending','accepted','rejected','deferred']
  AND row.source IS NOT NULL AND trim(row.source) <> ''
  AND row.evidence IS NOT NULL AND trim(row.evidence) <> ''
  AND NOT (row.status IN ['inference','hypothesis'] AND row.review_status='accepted')
MERGE (a:CausalAssertion {id: row.id})
SET a.kind=row.kind, a.company_id=row.company_id, a.period=row.period,
    a.affected_metric=row.affected_metric, a.direction=row.direction, a.lag=row.lag,
    a.source=row.source, a.evidence=row.evidence, a.confidence=row.confidence,
    a.counter_evidence=row.counter_evidence, a.status=row.status,
    a.review_status=row.review_status;

// Read path keeps facts and analysis explicitly separated.
MATCH (a:CausalAssertion {company_id:$company_id})
RETURN a.kind AS kind, a.status AS epistemic_status,
       a.review_status AS review_status, a.period AS period,
       a.affected_metric AS affected_metric, a.direction AS direction,
       a.lag AS lag, a.source AS source, a.evidence AS evidence,
       a.confidence AS confidence, a.counter_evidence AS counter_evidence
ORDER BY kind, period;
