// Order 133 minimal live write. Execute with parameter $rows loaded from
// data/133_winway_live_pilot.json through an approved write-capable Neo4j client.
// MERGE makes a retry idempotent; unsupported inference is kept pending.
UNWIND $rows AS row
MATCH (c:Company {id: row.company_id})
WITH c, row
WHERE row.kind IN ['EarningsDriverLink', 'Bottleneck', 'BeneficiaryAssessment']
  AND row.status IN ['fact', 'inference', 'hypothesis']
  AND row.review_status IN ['pending', 'accepted', 'rejected', 'deferred']
  AND row.source IS NOT NULL AND trim(row.source) <> ''
  AND row.evidence IS NOT NULL AND trim(row.evidence) <> ''
  AND NOT (row.status IN ['inference', 'hypothesis'] AND row.review_status = 'accepted')
MERGE (a:CausalAssertion {id: row.id})
SET a.kind = row.kind,
    a.company_id = row.company_id,
    a.period = row.period,
    a.affected_metric = row.affected_metric,
    a.direction = row.direction,
    a.lag = row.lag,
    a.source = row.source,
    a.evidence = row.evidence,
    a.confidence = row.confidence,
    a.counter_evidence = row.counter_evidence,
    a.status = row.status,
    a.review_status = row.review_status,
    a.order_id = '133'
MERGE (a)-[r:ASSERTED_FOR]->(c)
SET r.source = row.source, r.evidence = row.evidence, r.review_status = row.review_status;

// Post-write verification.
MATCH (a:CausalAssertion)-[r:ASSERTED_FOR]->(c:Company)
WHERE a.order_id = '133'
RETURN a.id AS id, a.kind AS kind, c.id AS company_id,
       a.source AS node_source, a.evidence AS node_evidence,
       r.source AS relationship_source, r.evidence AS relationship_evidence,
       a.review_status AS review_status
ORDER BY id;
