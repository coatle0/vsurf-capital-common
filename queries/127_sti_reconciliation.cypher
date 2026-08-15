// Canonical read path: live Neo4j. investment-kg must read this same database.
// 11-company HBM exposure coverage (expected: 11 rows).
MATCH (c:Company)-[e:EXPOSED_TO]->(:EndMarket {name:'DRAM / HBM'})
RETURN c.id AS company_id, c.name AS company, e.source_url AS source, e.status AS status
ORDER BY company;

// HBM process/product/component coordinates. Missing coordinates remain explicit;
// this query never creates an unsupported edge.
MATCH (c:Company)-[:EXPOSED_TO]->(:EndMarket {name:'DRAM / HBM'})
OPTIONAL MATCH (c)-[:OPERATES_IN]->(p:Process {name:'Wafer Test Cell'})
OPTIONAL MATCH (c)-[:PRODUCES]->(product:Product {name:'Probe Card'})
OPTIONAL MATCH (c)-[:PRODUCES]->(component:Component)-[:PART_OF]->(pc:Product {name:'Probe Card'})
RETURN c.id, c.name, p.name, product.name, component.name, pc.name ORDER BY c.name;

// Relationship quality gates for assertion-bearing edges.
MATCH (a)-[r]->(b)
WHERE type(r) IN ['DRIVES','EXPOSED_TO','OPERATES_IN','PRODUCES','PART_OF','COMPETES_WITH']
RETURN count(r) AS assertions,
       sum(CASE WHEN coalesce(r.source_url,'')='' THEN 1 ELSE 0 END) AS missing_source,
       sum(CASE WHEN r.status='confirmed' THEN 1 ELSE 0 END) AS auto_confirmed;

// Duplicate endpoint/type tuples (expected: no rows).
MATCH (a)-[r]->(b) WITH a,b,type(r) AS rel_type,count(*) AS n
WHERE n > 1 RETURN a.id,b.id,rel_type,n;

// Active REQUIRES assertions: source-less legacy edges are explicitly disabled.
MATCH (a)-[r:REQUIRES]->(b)
WHERE coalesce(r.disabled,false)=false
  AND coalesce(r.source_url,'')<>'' AND coalesce(r.evidence,'')<>''
RETURN a.id AS from_id,b.id AS to_id,r.source_url AS source,r.evidence AS evidence;
