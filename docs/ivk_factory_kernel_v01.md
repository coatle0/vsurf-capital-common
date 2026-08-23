# IVK Factory Kernel v0.1

Kernel v0.1 is the minimal execution harness used to unblock Phase 2. It is not the Phase 3 full CLI release.

## Commands

```powershell
python -m ivk validate --input intakes\new\us_optic.json

python -m ivk new `
  --input intakes\new\us_optic.json `
  --run-id IVK-20260823-US-OPTIC-001 `
  --sector optical_communications `
  --region us

python -m ivk status --run-id IVK-20260823-US-OPTIC-001

python -m ivk resume `
  --run-id IVK-20260823-US-OPTIC-001 `
  --graph-results artifacts\kernel_v01\us_optic_existing_graph.json
```

`new`, `add`, `update`, and `expand` are operation-enforcing aliases of `run`. `init` validates and creates an immutable run snapshot. `plan` consumes captured `neo4j-official.read_cypher` rows. A run without those rows becomes `BLOCKED` with reason `MISSING_GRAPH_RESULTS`; `resume` continues from the stored pack selection.

After `PLANNED`, VC-neutral lifecycle stages are:

```powershell
python -m ivk collect --run-id <id> --documents <collection.json>
python -m ivk ke --run-id <id> --structure <structure.json>
python -m ivk review --run-id <id>
python -m ivk write --run-id <id>
python -m ivk verify --run-id <id>
python -m ivk enrich --run-id <id> --financials <tikr.json> --ticker <TICKER>
python -m ivk benchmark --run-id <id> --scores <axes.json>
python -m ivk repair --run-id <id>
```

`write` emits MERGE-only batches. It does not call Neo4j. Tickers, sector terms, and VC nicknames belong in Intake/Blueprint/Pack/artifact JSON, not in `ivk/lifecycle.py`.

## Canonical run artifacts

```text
runs/<run_id>/
  manifest.json
  submitted_input.json
  intake.json
  normalized.json
  existing_graph.json
  blueprint.json
  source_plan.json
```

The manifest uses contract `ivk-run-0.1` and records status, last completed stage, blockers, the next command, artifact paths, hashes, and exact pack selection.

## Current boundary

Kernel v0.1 stops at `PLANNED`. Source collection, causal KE, graph diff, governed Neo4j write, read-back, quality scoring, and final reporting remain the Phase 2 execution path. No command in Kernel v0.1 writes to Neo4j.

Large or transient run data under `collection/raw`, `cache`, `tmp`, and `logs` is ignored by Git. Core input, manifest, Blueprint, Source Plan, review, and report artifacts remain eligible for explicit review and commit.
