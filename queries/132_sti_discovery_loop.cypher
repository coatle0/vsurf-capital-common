// Order 132 read-only canonical graph queries. No write clauses are permitted.

// Representative-company demand/process/product paths with relationship sources.
MATCH (c:Company)
WHERE c.id IN ['company:form','company:tse','company:winway']
OPTIONAL MATCH (c)-[e:EXPOSED_TO]->(d:EndMarket)
OPTIONAL MATCH (c)-[o:OPERATES_IN]->(p:Process)
OPTIONAL MATCH (c)-[r:PRODUCES]->(x)
OPTIONAL MATCH (x)-[part:PART_OF]->(parent:Product)
RETURN c.id AS company_id,c.name AS company,
       collect(DISTINCT {demand:d.name,source:e.source_url,status:e.status}) AS demands,
       collect(DISTINCT {process:p.name,source:o.source_url,status:o.status}) AS processes,
       collect(DISTINCT {product:x.name,labels:labels(x),source:r.source_url,
                         status:r.status,parent:parent.name,part_source:part.source_url}) AS products
ORDER BY company;

// Assertion guard. Evidence is represented by the cited source_url in the current live schema.
MATCH (a)-[r]->(b)
WHERE type(r) IN ['DRIVES','EXPOSED_TO','OPERATES_IN','PRODUCES','PART_OF','COMPETES_WITH']
RETURN count(r) AS assertions,
       sum(CASE WHEN coalesce(r.source_url,'')='' THEN 1 ELSE 0 END) AS missing_source,
       sum(CASE WHEN r.status='confirmed' THEN 1 ELSE 0 END) AS confirmed;

// Duplicate endpoint/type tuples; expected zero rows.
MATCH (a)-[r]->(b)
WITH a,b,type(r) AS relation_type,count(*) AS n
WHERE n > 1
RETURN a.id AS from_id,b.id AS to_id,relation_type,n;
