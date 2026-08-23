"""Command line interface for IVK Factory Kernel v0.1."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from scripts.ivk_factory import FactoryValidationError
from scripts.ivk_new_intake import IntakeValidationError, normalize_intake, validate_intake

from .kernel import (
    KernelError,
    block_for_graph,
    initialize_run,
    load_manifest,
    plan_run,
    read_json,
    resume_run,
)
from .lifecycle import (
    LifecycleError,
    benchmark_stage,
    collect_stage,
    extract_reported_periods,
    ke_stage,
    normalize_document,
    persist_stage,
    require_status,
    validate_packets,
    validate_readback,
    validate_write_receipt,
    write_batches,
)


EXIT_INPUT = 2
EXIT_CAPABILITY = 3
DEFAULT_RUNS = Path("runs")
DEFAULT_REGISTRY = Path("registry/ivk_factory_packs.json")


def emit(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def add_execution_arguments(parser: argparse.ArgumentParser, *, input_required: bool) -> None:
    if input_required:
        parser.add_argument("--input", type=Path, required=True)
        parser.add_argument("--run-id")
    parser.add_argument("--runs-dir", type=Path, default=DEFAULT_RUNS)
    parser.add_argument("--graph-results", type=Path)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--sector")
    parser.add_argument("--region", action="append")


def run_from_input(args: argparse.Namespace, expected_operation: str | None = None) -> dict[str, Any]:
    submitted = read_json(args.input)
    canonical = validate_intake(submitted)
    if expected_operation and canonical["operation"] != expected_operation:
        raise IntakeValidationError(
            f"command {expected_operation} requires operation={expected_operation}, got {canonical['operation']}"
        )
    manifest = initialize_run(args.input, args.runs_dir, args.run_id)
    run_id = manifest["run_id"]
    if not args.graph_results:
        return block_for_graph(
            args.runs_dir,
            run_id,
            sector=args.sector,
            regions=args.region,
            registry=args.registry,
        )
    if not args.sector or not args.region:
        raise IntakeValidationError("planning requires --sector and at least one --region")
    return plan_run(
        args.runs_dir,
        run_id,
        graph_results=args.graph_results,
        registry_path=args.registry,
        sector=args.sector,
        regions=args.region,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ivk", description="IVK Factory Kernel v0.1")
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate")
    validate.add_argument("--input", type=Path, required=True)

    init = sub.add_parser("init")
    init.add_argument("--input", type=Path, required=True)
    init.add_argument("--runs-dir", type=Path, default=DEFAULT_RUNS)
    init.add_argument("--run-id")

    plan = sub.add_parser("plan")
    plan.add_argument("--run-id", required=True)
    add_execution_arguments(plan, input_required=False)

    for command in ("run", "new", "add", "update", "expand"):
        command_parser = sub.add_parser(command)
        add_execution_arguments(command_parser, input_required=True)

    status = sub.add_parser("status")
    status.add_argument("--run-id", required=True)
    status.add_argument("--runs-dir", type=Path, default=DEFAULT_RUNS)

    resume = sub.add_parser("resume")
    resume.add_argument("--run-id", required=True)
    add_execution_arguments(resume, input_required=False)

    def add_run(parser_obj: argparse.ArgumentParser) -> None:
        parser_obj.add_argument("--run-id", required=True)
        parser_obj.add_argument("--runs-dir", type=Path, default=DEFAULT_RUNS)

    ingest = sub.add_parser("ingest-sources", help="Ingest/normalize document JSON. Does not fetch sources.")
    add_run(ingest)
    ingest.add_argument("--documents", type=Path, required=True)
    collect = sub.add_parser("collect", help="Alias of ingest-sources")
    add_run(collect)
    collect.add_argument("--documents", type=Path, required=True)

    ke = sub.add_parser("ke")
    add_run(ke)
    ke.add_argument("--structure", type=Path)

    review = sub.add_parser("review", help="Packet recheck only. Does not approve.")
    add_run(review)
    review.add_argument("--reviewed-by")
    review.add_argument("--decision")
    review.add_argument("--receipt", type=Path)

    emit = sub.add_parser("emit-write-batches", help="Emit MERGE batches. Does not write Neo4j.")
    add_run(emit)
    write = sub.add_parser("write", help="Alias of emit-write-batches unless --receipt is passed")
    add_run(write)
    write.add_argument("--receipt", type=Path)

    confirm = sub.add_parser("confirm-write", help="Confirm live Neo4j write from a receipt")
    add_run(confirm)
    confirm.add_argument("--receipt", type=Path, required=True)

    verify = sub.add_parser("verify", help="VERIFIED only with live read-back JSON")
    add_run(verify)
    verify.add_argument("--readback", type=Path)

    bench = sub.add_parser("benchmark")
    add_run(bench)
    bench.add_argument("--scores", type=Path, required=True)
    bench.add_argument("--score-kind", required=True, choices=["self-score", "independent-score"])
    bench.add_argument("--scorer", required=True)
    bench.add_argument("--rubric-version", default="order-142-v1")
    bench.add_argument("--evidence", required=True)

    enrich = sub.add_parser("enrich", help="Artifact-only financial enrichment; not graph write")
    add_run(enrich)
    enrich.add_argument("--financials", type=Path, action="append", required=True)
    enrich.add_argument("--ticker", action="append", required=True)

    normalize = sub.add_parser("normalize-evidence", help="Re-normalize collection documents")
    add_run(normalize)
    repair = sub.add_parser("repair", help="Alias of normalize-evidence")
    add_run(repair)
    return parser


def dispatch(args: argparse.Namespace) -> dict[str, Any]:
    if args.command == "validate":
        canonical = validate_intake(read_json(args.input))
        return {"ok": True, "canonical": canonical, "normalized": normalize_intake(canonical)}
    if args.command == "init":
        return initialize_run(args.input, args.runs_dir, args.run_id)
    if args.command == "plan":
        if not args.graph_results or not args.sector or not args.region:
            raise IntakeValidationError("plan requires --graph-results, --sector, and --region")
        return plan_run(
            args.runs_dir,
            args.run_id,
            graph_results=args.graph_results,
            registry_path=args.registry,
            sector=args.sector,
            regions=args.region,
        )
    if args.command in {"run", "new", "add", "update", "expand"}:
        expected = None if args.command == "run" else args.command
        return run_from_input(args, expected)
    if args.command == "status":
        return load_manifest(args.runs_dir, args.run_id)[1]
    if args.command == "resume":
        return resume_run(
            args.runs_dir,
            args.run_id,
            graph_results=args.graph_results,
            registry_path=args.registry,
            sector=args.sector,
            regions=args.region,
        )
    root, manifest = load_manifest(args.runs_dir, args.run_id)
    command = args.command
    if command == "collect":
        command = "ingest-sources"
    elif command == "repair":
        command = "normalize-evidence"
    elif command == "write" and getattr(args, "receipt", None):
        command = "confirm-write"
    elif command == "write":
        command = "emit-write-batches"
    require_status(manifest, command)
    plan = read_json(root / manifest["artifacts"]["source_plan"])
    if command == "ingest-sources":
        raw = read_json(args.documents)
        documents = raw["documents"] if isinstance(raw, dict) and "documents" in raw else raw
        collection = collect_stage(plan, documents, run_id=args.run_id)
        return persist_stage(
            args.runs_dir, args.run_id, "ingest-sources", {"source_collection": collection},
            next_command=f"python -m ivk ke --run-id {args.run_id}",
        )
    if command == "ke":
        collection = read_json(root / manifest["artifacts"].get("source_collection", "source_collection.json"))
        structure = read_json(args.structure) if args.structure else {}
        packets = ke_stage(plan, collection, structure=structure)
        packets["write_batches"] = write_batches(packets["write_manifest"])
        return persist_stage(
            args.runs_dir, args.run_id, "ke",
            {**packets, "write_batches": packets["write_batches"]},
            next_command=f"python -m ivk review --run-id {args.run_id}",
        )
    if command == "review":
        packets = {
            "evidence": read_json(root / "evidence_packet.json"),
            "ke": read_json(root / "ke_packet.json"),
            "write_manifest": read_json(root / "write_manifest.json"),
            "review": read_json(root / "review.json"),
        }
        validate_packets(packets)
        review = packets["review"]
        review["path_status"] = "REVIEW_READY"
        if args.reviewed_by and args.decision and args.receipt:
            receipt = read_json(args.receipt)
            review["approval"] = {
                "reviewed_by": args.reviewed_by,
                "decision": args.decision,
                "receipt": receipt,
            }
        elif args.reviewed_by or args.decision or args.receipt:
            raise LifecycleError("review approval requires --reviewed-by, --decision, and --receipt together")
        return persist_stage(
            args.runs_dir, args.run_id, "review", {"review": review},
            next_command=f"python -m ivk emit-write-batches --run-id {args.run_id}",
        )
    if command == "emit-write-batches":
        manifest_json = read_json(root / "write_manifest.json")
        batches = write_batches(manifest_json)
        manifest_json["neo4j_write_status"] = "batches_emitted_not_written"
        return persist_stage(
            args.runs_dir, args.run_id, "emit-write-batches",
            {"write_batches": batches, "write_manifest": manifest_json},
            next_command=f"python -m ivk confirm-write --run-id {args.run_id} --receipt <write_receipt.json>",
        )
    if command == "confirm-write":
        receipt = read_json(args.receipt)
        batches = read_json(root / "write_batches.json")
        validate_write_receipt(receipt, run_id=args.run_id, expected_batches=[item["name"] for item in batches])
        write_manifest = read_json(root / "write_manifest.json")
        write_manifest["neo4j_write_status"] = "write_confirmed"
        write_manifest["write_receipt"] = receipt
        return persist_stage(
            args.runs_dir, args.run_id, "confirm-write",
            {"write_receipt": receipt, "write_manifest": write_manifest},
            next_command=f"python -m ivk verify --run-id {args.run_id} --readback <readback.json>",
        )
    if command == "verify":
        if not args.readback:
            raise LifecycleError("verify requires --readback live Neo4j JSON; local packets cannot set VERIFIED")
        if manifest.get("status") != "WRITE_CONFIRMED":
            raise LifecycleError("verify rejected: WRITE_CONFIRMED receipt is required")
        packets = {
            "evidence": read_json(root / "evidence_packet.json"),
            "ke": read_json(root / "ke_packet.json"),
            "write_manifest": read_json(root / "write_manifest.json"),
            "review": read_json(root / "review.json"),
        }
        validate_packets(packets)
        readback = read_json(args.readback)
        validate_readback(readback, run_id=args.run_id, vc_id=packets["ke"]["value_chain"]["id"])
        report = {
            "ok": True,
            "run_id": args.run_id,
            "proof": "live_readback",
            "readback": readback,
            "write_receipt": read_json(root / "write_receipt.json"),
        }
        return persist_stage(
            args.runs_dir, args.run_id, "verify", {"verify": report, "readback": readback},
            next_command="done",
        )
    if command == "benchmark":
        scores = read_json(args.scores)
        axes = scores["axes"] if isinstance(scores, dict) else scores
        quality = benchmark_stage(
            axes, run_id=args.run_id, score_kind=args.score_kind,
            scorer=args.scorer, rubric_version=args.rubric_version, evidence=args.evidence,
        )
        return persist_stage(
            args.runs_dir, args.run_id, "benchmark", {"quality": quality},
            next_command=manifest.get("next_command") or f"python -m ivk review --run-id {args.run_id}",
            status=manifest.get("status"),
        )
    if command == "enrich":
        if len(args.financials) != len(args.ticker):
            raise LifecycleError("--financials and --ticker must be paired")
        rows = []
        for path, ticker in zip(args.financials, args.ticker, strict=True):
            rows.extend(extract_reported_periods(read_json(path), ticker=ticker, limit=5))
        payload = {
            "contract_version": "ivk-financial-enrichment-0.1",
            "run_id": args.run_id,
            "enrichment_kind": "ARTIFACT_ENRICHED",
            "periods": rows,
            "segment_status": "blocked-with-reason",
            "segment_reason": "TIKR asRptSegData payload was empty; no segment nodes written.",
            "write_policy": "artifact_only_not_graph_enriched",
        }
        return persist_stage(
            args.runs_dir, args.run_id, "enrich", {"financials": payload},
            next_command=f"python -m ivk ke --run-id {args.run_id}",
        )
    if command == "normalize-evidence":
        collection = read_json(root / "source_collection.json")
        collection["documents"] = [normalize_document(doc) for doc in collection["documents"]]
        return persist_stage(
            args.runs_dir, args.run_id, "normalize-evidence", {"source_collection": collection},
            next_command=f"python -m ivk ke --run-id {args.run_id}",
        )
    raise KernelError(f"unsupported command: {args.command}")


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        emit(dispatch(build_parser().parse_args()))
    except (IntakeValidationError, FactoryValidationError, LifecycleError) as exc:
        emit({"ok": False, "reason_code": "INPUT_VALIDATION", "message": str(exc)})
        raise SystemExit(EXIT_INPUT) from exc
    except KernelError as exc:
        emit({"ok": False, "reason_code": "KERNEL_ERROR", "message": str(exc)})
        raise SystemExit(EXIT_CAPABILITY) from exc
    except KeyboardInterrupt as exc:
        emit({"ok": False, "reason_code": "CANCELLED", "message": "interrupted"})
        raise SystemExit(130) from exc


if __name__ == "__main__":
    main()
