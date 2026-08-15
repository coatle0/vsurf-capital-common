// Read-only dry-run. $rows is data/127_causal_prototypes.json after Python validation.
UNWIND $rows AS row
MATCH (c:Company {id:row.company_id})
OPTIONAL MATCH (c)-[exposure:EXPOSED_TO]->(driver:EndMarket {name:'DRAM / HBM'})
OPTIONAL MATCH (c)-[operation:OPERATES_IN]->(process:Process)
OPTIONAL MATCH (c)-[production:PRODUCES]->(product)
WITH row,c,driver,exposure,collect(DISTINCT {
  process:process.name, source:operation.source_url, status:operation.status}) AS processes,
  collect(DISTINCT {product:product.name, source:production.source_url,
  status:production.status}) AS products
RETURN c.id AS company_id,c.name AS company,
       driver.name AS demand_driver,exposure.source_url AS demand_source,
       exposure.status AS demand_status,
       row.kind AS causal_stage,row.affected_metric AS metric,
       row.source AS causal_source,row.evidence AS causal_evidence,
       row.status AS epistemic_status,row.review_status AS review_status,
       row.confidence AS confidence,row.counter_evidence AS counter_evidence,
       processes,products
ORDER BY company_id,causal_stage;
