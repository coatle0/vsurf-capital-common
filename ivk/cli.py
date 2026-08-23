"""Command line interface for IVK Factory Kernel v0.1."""

from __future__ import annotations

import argparse
import json
import subprocess
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
    save_manifest,
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


def infer_regions(normalized: dict[str, Any]) -> list[str]:
    """Derive region packs from normalized seeds; Intake has no market field."""
    return list(dict.fromkeys(seed.get("market") or "us" for seed in normalized.get("validated_seeds", [])))


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
    selected_regions = args.region or infer_regions(normalize_intake(canonical))
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
            regions=selected_regions,
            registry=args.registry,
        )
    if not args.sector or not selected_regions:
        raise IntakeValidationError("planning requires --sector and at least one inferred region")
    return plan_run(
        args.runs_dir,
        run_id,
        graph_results=args.graph_results,
        registry_path=args.registry,
        sector=args.sector,
        regions=selected_regions,
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

    build = sub.add_parser(
        "build",
        help="Run Intake -> Plan -> Collection -> KE -> Review -> write batches in one command.",
    )
    add_execution_arguments(build, input_required=True)
    build.add_argument("--documents", type=Path, required=True)
    build.add_argument("--structure", type=Path)
    build.add_argument(
        "--receipt",
        type=Path,
        help="Optional live Neo4j write receipt; advances BATCH_READY to WRITE_CONFIRMED.",
    )
    build.add_argument(
        "--readback",
        type=Path,
        help="Optional live Neo4j read-back; requires --receipt and advances to VERIFIED.",
    )
    build.add_argument(
        "--execute-neo4j",
        action="store_true",
        help="Execute emitted batches, replay idempotency, and verify live Neo4j automatically.",
    )
    build.add_argument(
        "--neo4j-python",
        type=Path,
        default=Path(r"C:\lab\knowgraph\vendor\neo4j-mcp\.venv\Scripts\python.exe"),
        help="Python interpreter containing the official neo4j driver.",
    )

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
        if not args.graph_results or not args.sector:
            raise IntakeValidationError("plan requires --graph-results and --sector")
        root, manifest = load_manifest(args.runs_dir, args.run_id)
        selected_regions = args.region or infer_regions(read_json(root / manifest["artifacts"]["normalized"]))
        return plan_run(
            args.runs_dir,
            args.run_id,
            graph_results=args.graph_results,
            registry_path=args.registry,
            sector=args.sector,
            regions=selected_regions,
        )
    if args.command in {"run", "new", "add", "update", "expand"}:
        expected = None if args.command == "run" else args.command
        return run_from_input(args, expected)
    if args.command == "build":
        if not args.graph_results or not args.sector:
            raise IntakeValidationError("build requires --graph-results and --sector")
        if args.readback and not args.receipt:
            raise LifecycleError("build --readback requires --receipt")
        if args.execute_neo4j and (args.receipt or args.readback):
            raise LifecycleError(
                "build --execute-neo4j cannot be combined with external --receipt/--readback"
            )

        submitted = read_json(args.input)
        canonical = validate_intake(submitted)
        selected_regions = args.region or infer_regions(normalize_intake(canonical))
        manifest = initialize_run(args.input, args.runs_dir, args.run_id)
        run_id = manifest["run_id"]
        manifest = plan_run(
            args.runs_dir,
            run_id,
            graph_results=args.graph_results,
            registry_path=args.registry,
            sector=args.sector,
            regions=selected_regions,
        )
        root, manifest = load_manifest(args.runs_dir, run_id)
        plan = read_json(root / manifest["artifacts"]["source_plan"])

        raw = read_json(args.documents)
        documents = raw["documents"] if isinstance(raw, dict) and "documents" in raw else raw
        collection = collect_stage(plan, documents, run_id=run_id)
        manifest = persist_stage(
            args.runs_dir,
            run_id,
            "ingest-sources",
            {"source_collection": collection},
            next_command=f"python -m ivk ke --run-id {run_id}",
        )

        structure = read_json(args.structure) if args.structure else {}
        packets = ke_stage(plan, collection, structure=structure)
        packets["write_batches"] = write_batches(packets["write_manifest"])
        manifest = persist_stage(
            args.runs_dir,
            run_id,
            "ke",
            {**packets, "write_batches": packets["write_batches"]},
            next_command=f"python -m ivk review --run-id {run_id}",
        )
        validate_packets(packets)
        review_packet = packets["review"]
        review_packet["path_status"] = "REVIEW_READY"
        manifest = persist_stage(
            args.runs_dir,
            run_id,
            "review",
            {"review": review_packet},
            next_command=f"python -m ivk emit-write-batches --run-id {run_id}",
        )

        write_manifest = packets["write_manifest"]
        batches = write_batches(write_manifest)
        write_manifest["neo4j_write_status"] = "batches_emitted_not_written"
        manifest = persist_stage(
            args.runs_dir,
            run_id,
            "emit-write-batches",
            {"write_batches": batches, "write_manifest": write_manifest},
            next_command=f"python -m ivk confirm-write --run-id {run_id} --receipt <write_receipt.json>",
        )

        if args.execute_neo4j:
            if not args.neo4j_python.is_file():
                raise LifecycleError(f"Neo4j Python interpreter not found: {args.neo4j_python}")
            receipt_path = root / "write_receipt.json"
            readback_path = root / "readback.json"
            executor = Path(__file__).resolve().parents[1] / "scripts" / "ivk_neo4j_executor.py"
            completed = subprocess.run(
                [
                    str(args.neo4j_python),
                    str(executor),
                    "--batches", str(root / "write_batches.json"),
                    "--receipt", str(receipt_path),
                    "--readback", str(readback_path),
                    "--run-id", run_id,
                    "--vc-id", packets["ke"]["value_chain"]["id"],
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            if completed.returncode != 0:
                message = (completed.stderr or completed.stdout or "unknown executor error").strip()
                raise LifecycleError(f"live Neo4j execution failed: {message}")
            args.receipt = receipt_path
            args.readback = readback_path

        if args.receipt:
            receipt = read_json(args.receipt)
            validate_write_receipt(
                receipt,
                run_id=run_id,
                expected_batches=[item["name"] for item in batches],
            )
            write_manifest["neo4j_write_status"] = "write_confirmed"
            write_manifest["write_receipt"] = receipt
            manifest = persist_stage(
                args.runs_dir,
                run_id,
                "confirm-write",
                {"write_receipt": receipt, "write_manifest": write_manifest},
                next_command=f"python -m ivk verify --run-id {run_id} --readback <readback.json>",
            )

        if args.readback:
            readback = read_json(args.readback)
            validate_readback(
                readback,
                run_id=run_id,
                vc_id=packets["ke"]["value_chain"]["id"],
            )
            report = {
                "ok": True,
                "run_id": run_id,
                "proof": "live_readback",
                "readback": readback,
                "write_receipt": read_json(root / "write_receipt.json"),
            }
            manifest = persist_stage(
                args.runs_dir,
                run_id,
                "verify",
                {"verify": report, "readback": readback},
                next_command="done",
            )

        manifest["build_summary"] = {
            "input_operation": canonical["operation"],
            "terminal_status": manifest["status"],
            "live_write_proven": bool(args.receipt),
            "live_readback_proven": bool(args.readback),
        }
        root, _ = load_manifest(args.runs_dir, run_id)
        save_manifest(root, manifest)
        return manifest
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
