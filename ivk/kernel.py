"""Agent-neutral run state and orchestration for IVK Factory Kernel v0.1."""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.ivk_factory import PackRegistry, build_source_plan
from scripts.ivk_new_intake import build_blueprint, normalize_intake, validate_intake


RUN_CONTRACT = "ivk-run-0.1"


class KernelError(RuntimeError):
    """A deterministic IVK Kernel execution error."""


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise KernelError(f"file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise KernelError(f"invalid JSON: {path}: {exc}") from exc


def write_json_atomic(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f".{path.name}.tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)


def content_hash(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def make_run_id(normalized: dict[str, Any]) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f")
    slug = normalized["identity"]["slug"][:40] or "unnamed"
    return f"IVK-{stamp}-{normalized['operation']}-{slug}"


def run_dir(runs_dir: Path, run_id: str) -> Path:
    if not run_id or run_id in {".", ".."} or any(char in run_id for char in "\\/:"):
        raise KernelError("run_id must be a safe directory name")
    return runs_dir / run_id


def load_manifest(runs_dir: Path, run_id: str) -> tuple[Path, dict[str, Any]]:
    root = run_dir(runs_dir, run_id)
    manifest = read_json(root / "manifest.json")
    if manifest.get("contract_version") != RUN_CONTRACT or manifest.get("run_id") != run_id:
        raise KernelError(f"invalid run manifest: {root / 'manifest.json'}")
    return root, manifest


def save_manifest(root: Path, manifest: dict[str, Any]) -> None:
    manifest["updated_at"] = now_iso()
    write_json_atomic(root / "manifest.json", manifest)


def initialize_run(input_path: Path, runs_dir: Path, run_id: str | None = None) -> dict[str, Any]:
    submitted = read_json(input_path)
    canonical = validate_intake(submitted)
    normalized = normalize_intake(canonical)
    selected_run_id = run_id or make_run_id(normalized)
    root = run_dir(runs_dir, selected_run_id)
    if root.exists():
        raise KernelError(f"run already exists: {selected_run_id}")
    root.mkdir(parents=True)
    write_json_atomic(root / "submitted_input.json", submitted)
    write_json_atomic(root / "intake.json", canonical)
    write_json_atomic(root / "normalized.json", normalized)
    created = now_iso()
    manifest = {
        "contract_version": RUN_CONTRACT,
        "run_id": selected_run_id,
        "operation": canonical["operation"],
        "target_vc": canonical["target_vc"],
        "value_chain": normalized["identity"],
        "status": "VALIDATED",
        "last_completed_stage": "validate",
        "next_command": f"python -m ivk plan --run-id {selected_run_id} --graph-results <path> --sector <sector> --region <region>",
        "blockers": [],
        "artifacts": {
            "submitted_input": "submitted_input.json",
            "intake": "intake.json",
            "normalized": "normalized.json",
            "intake_sha256": content_hash(canonical),
        },
        "pack_selection": None,
        "created_at": created,
        "updated_at": created,
    }
    save_manifest(root, manifest)
    return deepcopy(manifest)


def block_for_graph(
    runs_dir: Path,
    run_id: str,
    *,
    sector: str | None,
    regions: list[str] | None,
    registry: Path | None,
) -> dict[str, Any]:
    root, manifest = load_manifest(runs_dir, run_id)
    manifest["status"] = "BLOCKED"
    manifest["last_completed_stage"] = "validate"
    manifest["blockers"] = [{
        "reason_code": "MISSING_GRAPH_RESULTS",
        "message": "captured neo4j-official.read_cypher rows are required",
        "retryable": True,
    }]
    manifest["pack_selection"] = {
        "sector": sector,
        "regions": regions or [],
        "registry": str(registry) if registry else None,
    }
    manifest["next_command"] = f"python -m ivk resume --run-id {run_id} --graph-results <path>"
    save_manifest(root, manifest)
    return deepcopy(manifest)


def plan_run(
    runs_dir: Path,
    run_id: str,
    *,
    graph_results: Path,
    registry_path: Path,
    sector: str,
    regions: list[str],
) -> dict[str, Any]:
    root, manifest = load_manifest(runs_dir, run_id)
    canonical = read_json(root / manifest["artifacts"]["intake"])
    graph = read_json(graph_results)
    if not isinstance(graph, list):
        raise KernelError("graph_results must contain a JSON row array")
    write_json_atomic(root / "existing_graph.json", graph)
    blueprint = build_blueprint(canonical, graph)
    write_json_atomic(root / "blueprint.json", blueprint)
    manifest["status"] = "GRAPH_CHECKED"
    manifest["last_completed_stage"] = "graph_check"
    manifest["blockers"] = []
    manifest["artifacts"].update({
        "existing_graph": "existing_graph.json",
        "blueprint": "blueprint.json",
        "graph_snapshot_sha256": content_hash(graph),
    })
    save_manifest(root, manifest)

    frame = blueprint["normalized"].get("primary_frame")
    if not frame:
        raise KernelError("planning requires a frame; update intake must provide one in Kernel v0.1")
    registry = PackRegistry(registry_path)
    selection = registry.select(frame=frame, sector=sector, regions=regions)
    source_plan = build_source_plan(blueprint, selection)
    write_json_atomic(root / "source_plan.json", source_plan)
    manifest["status"] = "PLANNED"
    manifest["last_completed_stage"] = "plan"
    manifest["next_command"] = "external source collection / Phase 2 quality run"
    manifest["pack_selection"] = {
        "sector": sector,
        "regions": regions,
        "registry": str(registry_path),
        "manifest": selection.manifest(),
    }
    manifest["artifacts"]["source_plan"] = "source_plan.json"
    save_manifest(root, manifest)
    return deepcopy(manifest)


def resume_run(
    runs_dir: Path,
    run_id: str,
    *,
    graph_results: Path | None = None,
    registry_path: Path | None = None,
    sector: str | None = None,
    regions: list[str] | None = None,
) -> dict[str, Any]:
    _, manifest = load_manifest(runs_dir, run_id)
    if manifest["status"] in {"PLANNED", "COMPLETED"}:
        return deepcopy(manifest)
    if not graph_results:
        return block_for_graph(
            runs_dir, run_id, sector=sector, regions=regions, registry=registry_path
        )
    saved = manifest.get("pack_selection") or {}
    final_sector = sector or saved.get("sector")
    final_regions = regions or saved.get("regions") or []
    final_registry = registry_path or (Path(saved["registry"]) if saved.get("registry") else None)
    if not final_sector or not final_regions or not final_registry:
        raise KernelError("resume requires sector, region, and registry selection")
    return plan_run(
        runs_dir,
        run_id,
        graph_results=graph_results,
        registry_path=final_registry,
        sector=final_sector,
        regions=final_regions,
    )
