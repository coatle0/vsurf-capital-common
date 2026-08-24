# IVK Factory `build` command

`ivk build` is the deterministic one-command path from a validated Intake to Neo4j write batches. It reuses the same lifecycle contracts as the individual commands; it does not invent source data or claim that a database write occurred.

## Command

```powershell
python -m ivk build `
  --input examples/us_nuclear_validation_intake.json `
  --run-id IVK-YYYYMMDD-US-NUCLEAR-BUILD-001 `
  --runs-dir runs `
  --graph-results examples/us_nuclear_validation_graph.json `
  --documents examples/us_nuclear_validation_documents.json `
  --structure examples/us_nuclear_validation_structure.json `
  --sector nuclear `
  --region us
```

This performs Intake validation, normalization, Existing Graph Check import, pack selection, source-document normalization, Knowledge Engineering, review packet validation, and idempotent write-batch generation. Its terminal state is `BATCH_READY`.

To execute the approved MERGE batches and include live verification in the same build:

```powershell
python -m ivk build ... --execute-neo4j
```

The command uses the shared `neo4j-official` Python environment, reads credentials from process/user environment variables, executes every batch, replays the batches to test idempotency, performs live read-back, creates `write_receipt.json` and `readback.json`, and reaches `VERIFIED`. It never prints the password.

`--region` is optional. When omitted, IVK derives the required region packs from each normalized seed (`US`, `KR`, `JP`, `TW`) and composes a mixed-market Source Plan. Supplying region flags that omit a seed market is rejected. Korean company tasks use DART without TIKR; Japanese tasks add JPX fiscal-period handling; Taiwanese tasks add TWSE/TPEX identity resolution and monthly-revenue tracking.

The default shared interpreter is:

```text
C:\lab\knowgraph\vendor\neo4j-mcp\.venv\Scripts\python.exe
```

Override it with `--neo4j-python` if a PC uses another path. PC-specific credentials remain environment variables and are not stored in the repository.

If an authorized external executor has already run every batch against live Neo4j, the same command may instead receive its proof:

```powershell
python -m ivk build ... `
  --receipt write_receipt.json `
  --readback readback.json
```

Both proofs must use the same Run-ID. A receipt advances the run to `WRITE_CONFIRMED`; a valid live read-back advances it to `VERIFIED`. `--readback` without `--receipt` is rejected.

## Input boundary

The Intake JSON is the business request. The other JSON files are captured tool outputs:

- Intake is always mixed-market and has no `market` field: US tickers remain plain, and numeric Asian seeds use `KR:`, `JP:`, or `TW:`.

- `graph-results`: canonical `neo4j-official.read-cypher` result
- `documents`: TIKR, DART, GS, filings, earnings calls, or other source records with provenance
- `structure`: evidence-linked candidate companies, products, processes, end markets, drivers, and assertions
- `receipt`: actual Neo4j batch execution result
- `readback`: actual post-write Neo4j verification result

The CLI deliberately refuses to manufacture these artifacts. An MCP-capable agent or collection runner must create them before `build`. This preserves the distinction between a reproducible pipeline and an unsupported claim.

## Quality levels

- `BATCH_READY`: deterministic candidate VC is ready to write; no live-write claim.
- `VERIFIED`: live write receipt and read-back both passed.
- STI-grade: a separate quality gate requiring coverage targets for five-quarter financials, segments, inventory, provenance, and reviewed causal assertions. `VERIFIED` alone does not imply STI-grade.

`build` does not itself fetch the documents named by the Source Plan. Do not describe an Intake-only or company-overview-only run as “STI 70%.” That target requires source collection, evidence-linked structure, enrichment, and an STI-rubric benchmark artifact. Structural `VERIFIED` and investment-analysis coverage are independent dimensions.

## Enrichment integration

Before source collection, create the Universal/Unique contract with `python -m ivk prepare-enrichment`. The intended progression is:

```text
prepare-enrichment
  -> shared Universal coverage check
  -> missing-source tasks
  -> UniversalFact write
  -> frame-specific UniqueAssertion review
  -> EvidenceGap closure and revalidation
  -> build/write/read-back/benchmark
```

The command emits planning artifacts only. It never treats a frame inference as a confirmed fact and never implies Neo4j write completion. See `docs/ivk_universal_unique_enrichment.md`.

## Resume and safety

Run directories are immutable by Run-ID. Reusing an existing Run-ID is rejected. All graph mutations use emitted `MERGE` batches, and unsupported causal candidates remain pending. Financial time-series labels used by STI are outside the generic structural write scope.
