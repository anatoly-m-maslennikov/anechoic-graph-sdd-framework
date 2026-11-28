"""Read and validate legacy candidate schema assets."""

import hashlib
import json
from pathlib import Path
from pydantic import ConfigDict
from pydantic.dataclasses import dataclass

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.content.carrier_compat__pub import (
    header_value,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.carriers.role_form_schema import (
    load_role_form,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.carriers.header.header_constraints__shared import (
    load_header_constraints,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.carriers.content.content_constraints__shared import (
    load_content_constraints,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.sources.placement.placement_model import (
    load_placement,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.carriers.header_relation_rules import (
    load_header_relation_rules,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.carriers.header_ordering import (
    load_header_ordering,
)
from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.FEATURE_IWE_CONSOLE_BACKEND__shared import (
    load_image_schema,
)
from FEATURE_PROGRAMMATIC.FEATURE_FORMAL_MODEL_ENGINE.FEATURE_FORMAL_MODEL_ENGINE__shared import (
    Atom,
    DEPENDENCIES_CLAIM_SHA256,
    dependencies_are_distinct,
    verify_packaged_dependencies_check,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests.declarations.legacy_work_report_model import (
    verify_work_report_target,
)


@dataclass(
    config=ConfigDict(strict=True, extra="forbid", hide_input_in_errors=True),
    frozen=True,
)
class CandidateSchema:
    workbench: object
    role_form: object
    header_constraints: object
    content_constraints: object
    placement: object = None
    atom_dependencies_check: bool = False
    work_report_target: dict | None = None
    header_relation_rules: dict | None = None
    atom_population_model: bool = False
    header_ordering: list | None = None

    def header(self, mode):
        return self.workbench.header(mode)

    @property
    def content(self):
        return self.workbench.content

    def validate_role_form(self, role, form):
        self.role_form.validate(role, form)

    def validate_atom_dependencies(self, metadata):
        present, values = header_value(metadata, "topics.dependencies")
        if not present:
            return
        if (
            isinstance(values, dict)
            and set(values) <= {"continuant", "occurrent"}
            and all(isinstance(group, list) for group in values.values())
        ):
            values = [item for group in values.values() for item in group]
        if not isinstance(values, list) or any(
            type(value) is not str for value in values
        ):
            raise ValueError("Topic Dependencies require a list of strings.")
        if not dependencies_are_distinct(Atom(tuple(values))):
            raise ValueError("Topic Dependencies must be distinct.")


class _MemoryAsset:
    def __init__(self, payload):
        self.payload = payload

    def is_symlink(self):
        return False

    def is_file(self):
        return True

    def read_bytes(self):
        return json.dumps(
            self.payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode()


def _canonical(payload):
    return json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode()


def load_candidate_schema(path: Path):
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError("candidate schema is missing or is a symlink")
    try:
        payload = json.loads(path.read_bytes())
        _validate_candidate_payload(payload)
        workbench = load_image_schema(_MemoryAsset(payload["workbench"]))
        source_pins = payload["workbench"]["sources"]
        source_ids = {pin["atom_id"] for pin in source_pins}
        check = _validate_dependency_pin(payload, source_pins)
        work_report_target = payload.get("work_report_target")
        if "work_report_target" in payload:
            verify_work_report_target(work_report_target)
        if (
            "atom_population_model" in payload
            and payload["atom_population_model"] is not True
        ):
            raise ValueError("Invalid Atom population model")
        return _decode_candidate_schema(
            payload, workbench, source_ids, check, work_report_target
        )
    except (
        OSError,
        KeyError,
        TypeError,
        UnicodeError,
        json.JSONDecodeError,
    ) as error:
        raise ValueError(f"invalid candidate schema: {error}") from error


def _validate_candidate_payload(payload):
    required = {
        "schema_version",
        "workbench",
        "role_form",
        "header_constraints",
        "content_constraints",
        "digest",
    }
    optional = {
        "placement",
        "atom_dependencies_check",
        "work_report_target",
        "header_relation_rules",
        "atom_population_model",
        "header_ordering",
    }
    if (
        not isinstance(payload, dict)
        or not required <= payload.keys() <= required | optional
    ):
        raise ValueError("invalid candidate schema shape")
    digest = payload.pop("digest")
    if (
        payload["schema_version"] != 2
        or type(payload["schema_version"]) is not int
    ):
        raise ValueError("unsupported candidate schema version")
    if digest != hashlib.sha256(_canonical(payload)).hexdigest():
        raise ValueError("candidate schema digest mismatch")


def _decode_candidate_schema(
    payload, workbench, source_ids, check, work_report_target
):
    return CandidateSchema(
        workbench,
        load_role_form(payload["role_form"], source_ids),
        load_header_constraints(payload["header_constraints"], source_ids),
        load_content_constraints(payload["content_constraints"], source_ids),
        load_placement(payload["placement"])
        if "placement" in payload
        else None,
        check,
        work_report_target,
        load_header_relation_rules(payload["header_relation_rules"])
        if "header_relation_rules" in payload
        else None,
        payload.get("atom_population_model", False),
        load_header_ordering(payload["header_ordering"])
        if "header_ordering" in payload
        else None,
    )


def _validate_dependency_pin(payload, source_pins):
    check = "atom_dependencies_check" in payload
    if check:
        pin = payload["atom_dependencies_check"]
        if (
            not isinstance(pin, dict)
            or set(pin) != {"claim_sha256", "source"}
            or pin["claim_sha256"] != DEPENDENCIES_CLAIM_SHA256
            or source_pins.count(pin["source"]) != 1
        ):
            raise ValueError("Invalid reviewed Atom Dependencies check")
        verify_packaged_dependencies_check()
    return check
