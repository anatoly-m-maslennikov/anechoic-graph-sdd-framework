"""Fingerprint artifacts and validate the admitted generation hint."""

import json
from hashlib import sha256
from pathlib import Path
from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    InstanceOf,
    ValidationError,
    model_validator,
)

_GRAPH_ANALYZERS = (
    "realization_graph.py",
    "analysis/python_code_units.py",
    "web_analysis/web_code_units.ts",
    "web_analysis/web_export_aliases.ts",
    "web_analysis/web_import_review.ts",
)


class _ReuseHint(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    base_generation: str = Field(min_length=1)
    inputs: InstanceOf[dict]
    endpoints: InstanceOf[dict]
    graph_config: Any
    carrier_hashes: Any = None
    folder_hashes: Any = None
    status_domains: dict[str, list[str]] | None = None

    @model_validator(mode="after")
    def _checkpoint_fields(self):
        if self.status_domains is not None and (
            set(self.status_domains) != {"S", "T", "P", "C"}
            or any(
                not values
                or len(set(values)) != len(values)
                or any(not value or value != value.strip() for value in values)
                for values in self.status_domains.values()
            )
            or self.status_domains["P"] != self.status_domains["C"]
        ):
            raise ValueError("Invalid admitted Status domains")
        if (
            "folder_hashes" in self.model_fields_set
            and "carrier_hashes" not in self.model_fields_set
        ):
            raise ValueError("Folder hashes require a carrier checkpoint")
        return self


def _reuse_hint(value):
    try:
        return _ReuseHint.model_validate(value)
    except ValidationError:
        return None


def digest(value):
    return sha256(
        json.dumps(
            value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode()
    ).hexdigest()


def reusable_graph(graph):
    return graph is None or all(
        row[-1] != "Lean check failed"
        for row in graph.get("state_effect_findings", ())
    )


def carrier_schema():
    engine = Path(__file__).resolve().parents[2]
    folders = (
        engine / "FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ADAPTERS_C30",
        engine / "ARCHITECTURE_ANALYSIS_C73/CODE_AND_SPEC_METRICS_C76",
    )
    files = sorted(
        path for folder in folders for path in folder.rglob("*.py")
        if not any(part.endswith("__tests") for part in path.parts)
    )
    if any(not folder.is_dir() for folder in folders) or not files:
        return None
    try:
        return digest(
            [
                [
                    path.relative_to(engine).as_posix(),
                    sha256(path.read_bytes()).hexdigest(),
                ]
                for path in files
            ]
        )
    except OSError:
        return None


def artifact_inputs(
    binding, config, *, watcher_guarded=False, defer_graph=False
):
    from ..manifest_build_CS4.manifest_build_CS4__shared import (
        manifest_input_signature,
    )

    manifest = manifest_input_signature(
        binding, watcher_guarded=watcher_guarded
    )
    schema = carrier_schema()
    if manifest is None or schema is None:
        return None
    if config is None:
        graph = "disabled"
    elif defer_graph:
        graph = "pending"
    else:
        from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IMPORT_GRAPH_C61.\
            RESOLUTION.graph_inputs import (
            graph_input_signature,
        )  # fmt: skip

        graph = graph_input_signature(Path(binding["root"]), config)
    if graph is None:
        return None
    if config is not None and not defer_graph:
        try:
            folder = Path(__file__).resolve().parents[1]
            analyzers = [
                sha256((folder / name).read_bytes()).hexdigest()
                for name in _GRAPH_ANALYZERS
            ]
        except OSError:
            return None
        graph = digest([graph, *analyzers])
    return {"manifest": manifest, "graph": graph, "carrier_schema": schema}


def _domain_option(reuse):
    return (
        {
            "domains": {
                key: set(values)
                for key, values in reuse.status_domains.items()
            }
        }
        if reuse.status_domains is not None
        else {}
    )
