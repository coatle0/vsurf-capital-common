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
    raise KernelError(f"unsupported command: {args.command}")


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        emit(dispatch(build_parser().parse_args()))
    except (IntakeValidationError, FactoryValidationError) as exc:
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
