"""Compile a Model and retain its last admitted generation on failure."""

from hashlib import sha256
import json
import shutil
import sys
from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints, model_validator

from ....FEATURE_MODEL_VALIDATION.FEATURE_MODEL_VALIDATION__shared import (
    open_admitted_model,
    open_serialized_model,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.sources.sources__shared import (
    mark_startup_timing,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    PROJECT_SUPPORT.PROJECT_SELECTION.\
    PROJECT_SELECTION__shared import (
    resolve_native_project,
)
from ..active_model_sources import compile_active_model_rows
from ..compiler import write_model_records
from ._model_ingestion_diagnostics import _diagnose


class ModelRow(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    source_path: str
    exact_ref: str
    metadata: dict
    body: str


class ModelInputs(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    rows: list[ModelRow]
    has_c9: bool
    issues: list[dict]
    accepted_model: dict | None
    force_rebuild: bool = False
    compiler_sha256: (
        Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")] | None
    ) = None
    spec_rows: list[dict] | None = None
    manifest_path: str | None = None

    @model_validator(mode="after")
    def _validate_snapshot(self):
        if (self.spec_rows is None) != (self.manifest_path is None):
            raise ValueError(
                "Spec snapshot and pinned Manifest path must be "
                "supplied together"
            )
        return self


def _inputs_sha256(inputs):
    rows = [
        row.model_dump()
        for row in sorted(inputs.rows, key=lambda row: row.source_path)
    ]
    witness = {
        "compiler_sha256": inputs.compiler_sha256,
        "has_c9": inputs.has_c9,
        "rows": rows,
    }
    return sha256(
        json.dumps(witness, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _records(inputs, node_locations, node_metadata):
    return compile_active_model_rows(
        [row.model_dump() for row in inputs.rows],
        has_c9=inputs.has_c9,
        node_locations=node_locations,
        node_metadata=node_metadata,
    )


def _restore(directory, accepted):
    if accepted is None:
        write_model_records(directory, None)
        return
    with open_serialized_model(accepted):
        pass
    package = directory / "anechoic_runtime_model"
    package.mkdir()
    for name, source in accepted["module_sources"].items():
        (package / name).write_text(source, encoding="utf-8")
    (directory / "model.json").write_text(
        json.dumps(accepted, sort_keys=True), encoding="utf-8"
    )


def _reuse(directory, inputs, fallback):
    witness = (
        _inputs_sha256(inputs)
        if fallback is None
        and not inputs.issues
        and inputs.compiler_sha256 is not None
        else None
    )
    if (
        witness is not None
        and not inputs.force_rebuild
        and inputs.accepted_model is not None
        and inputs.accepted_model.get("model_inputs_sha256") == witness
    ):
        try:
            _restore(directory, inputs.accepted_model)
        except (
            AttributeError,
            ImportError,
            RuntimeError,
            ValueError,
            TypeError,
            KeyError,
            SyntaxError,
        ):
            inputs.accepted_model = None
        else:
            mark_startup_timing("model_ready", mode="reused")
            return witness, sha256(
                (directory / "model.json").read_bytes()
            ).hexdigest()
    return witness, None


def _stage(directory, inputs, diagnostics, fallback=None):
    witness, digest = _reuse(directory, inputs, fallback)
    if digest is not None:
        return digest
    try:
        if fallback is not None:
            raise ValueError(str(fallback))
        if inputs.issues:
            raise ValueError(
                "Model source ingestion failed: "
                + json.dumps(inputs.issues, default=str)
            )
        node_locations, node_metadata = {}, {}
        write_model_records(
            directory,
            _records(inputs, node_locations, node_metadata),
            node_locations=node_locations,
            node_metadata=node_metadata,
        )
        digest = _serialize(directory, witness)
        reused = False
    except (
        OSError,
        AttributeError,
        ImportError,
        RuntimeError,
        ValueError,
        TypeError,
        KeyError,
        SyntaxError,
    ) as error:
        _diagnose(inputs, diagnostics, fallback, error)
        for child in directory.iterdir():
            shutil.rmtree(
                child
            ) if child.is_dir() and not child.is_symlink() else child.unlink()
        _restore(directory, inputs.accepted_model)
        digest = _serialize(directory)
        reused = inputs.accepted_model is not None
    mark_startup_timing("model_ready", mode="reused" if reused else "built")
    return digest


def _serialize(directory, witness=None):
    path = directory / "model.json"
    raw = path.read_bytes()
    descriptor = json.loads(raw)
    with open_admitted_model(
        directory, descriptor["model_sha256"], sha256(raw).hexdigest()
    ) as model:
        descriptor["ticket_labels"] = model.ticket_labels
    descriptor["module_sources"] = {
        name: (directory / "anechoic_runtime_model" / name).read_text(
            encoding="utf-8"
        )
        for name in descriptor["modules"]
    }
    if any(
        sha256(source.encode("utf-8")).hexdigest()
        != descriptor["modules"][name]
        for name, source in descriptor["module_sources"].items()
    ):
        raise ValueError("Model modules changed during serialization")
    if witness is not None:
        descriptor["model_inputs_sha256"] = witness
    path.write_text(json.dumps(descriptor, sort_keys=True), encoding="utf-8")
    return sha256(path.read_bytes()).hexdigest()


def _structure(args, digest, compile_structure, inputs, compile_snapshot):
    descriptor = json.loads((args.generation / "model.json").read_bytes())
    with open_admitted_model(
        args.generation, descriptor["model_sha256"], digest
    ) as model:
        if inputs.spec_rows is not None:
            if compile_snapshot is None:
                raise ValueError("Spec snapshot compiler is unavailable")
            return compile_snapshot(
                args, model, inputs.spec_rows, inputs.manifest_path
            )
        selection = resolve_native_project(
            args.project_root,
            args.control_root,
            validate_manifest=model.validate_manifest,
            require_atom_state=model.requires_atom_state,
            require_atom_header=model.requires_atom_header,
            require_manifest_summary=model.declares_summary(
                "Project Manifest"
            ),
        )
        if selection.manifest_sha256 != args.project_manifest_sha256:
            raise ValueError(
                "Project Manifest changed. Restart to apply its settings."
            )
        return compile_structure(selection, model)


def _check_generation(directory):
    if (
        directory.is_symlink()
        or not directory.is_dir()
        or directory.resolve(strict=True) != directory
        or any(directory.iterdir())
    ):
        raise ValueError(
            "Model generation must be an empty canonical directory"
        )


def compile_ingested(args, raw, compile_structure, *, compile_snapshot=None):
    diagnostics = []
    try:
        inputs = ModelInputs.model_validate(raw)
        _check_generation(args.generation)
        digest = _stage(args.generation, inputs, diagnostics)
        try:
            snapshot = _structure(
                args, digest, compile_structure, inputs, compile_snapshot
            )
        except (OSError, RuntimeError, TypeError, ValueError) as error:
            if diagnostics:
                raise
            digest = _stage(
                args.generation, inputs, diagnostics, fallback=error
            )
            snapshot = _structure(
                args, digest, compile_structure, inputs, compile_snapshot
            )
        mark_startup_timing("structure_ready", mode="built")
        return {
            "structure": snapshot,
            "model_descriptor_sha256": digest,
            "model_diagnostics": diagnostics,
        }
    except (
        OSError,
        AttributeError,
        ImportError,
        RuntimeError,
        TypeError,
        ValueError,
        KeyError,
        SyntaxError,
    ) as error:
        return {
            "error": {"code": "model_compile_failed", "message": str(error)},
            "model_diagnostics": diagnostics,
        }


def compile_ingested_cli(args, compile_structure, *, compile_snapshot=None):
    try:
        result = compile_ingested(
            args,
            json.load(sys.stdin),
            compile_structure,
            compile_snapshot=compile_snapshot,
        )
    except (OSError, ValueError, TypeError) as error:
        result = {
            "error": {"code": "model_compile_failed", "message": str(error)},
            "model_diagnostics": [],
        }
    print(
        json.dumps(result, separators=(",", ":"), sort_keys=True),
        file=sys.stderr if "error" in result else sys.stdout,
    )
    if "error" in result:
        raise SystemExit(1)
