"""Validated native Manifest input shared by selection and MCP tests."""

from dataclasses import field

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.FEATURE_MODEL_VALIDATION.model_field_validation import validate_model_fields


@dataclass(config=ConfigDict(strict=True, extra="forbid", hide_input_in_errors=True))
class ProjectManifest:
    atom_id: str
    ref_id: str
    version: int
    tier: int = field(metadata={"allowed_values": (-1,)})
    name: str
    prefix: str
    parameters: dict[str, object] = field(default_factory=dict)
    lens_whitelist: list[str] | None = None


def validate_manifest(fields, component_id):
    if component_id != "C0":
        raise ValueError("Manifest must be contained by the Project")
    validate_model_fields(ProjectManifest, fields)
    return ProjectManifest(**fields)
