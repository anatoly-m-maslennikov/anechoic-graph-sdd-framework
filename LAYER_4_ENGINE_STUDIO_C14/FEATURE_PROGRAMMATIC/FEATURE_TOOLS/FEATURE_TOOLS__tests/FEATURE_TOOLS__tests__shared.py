"Build the legacy candidate schema for regression tests with staged sources."

from __future__ import annotations

import argparse
from pydantic import ConfigDict as ConfigDict
from pydantic.dataclasses import dataclass as dataclass
import hashlib
import json
from pathlib import Path
import sys

TOOLS = Path(__file__).resolve().parents[1]
WORKBENCH = TOOLS.parent.parent / "IWE_CONSOLE_C43/APP_IWE_CONSOLE"
sys.path.insert(0, str(TOOLS.parents[2]))
sys.path.insert(0, str(TOOLS.parent))
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(WORKBENCH))

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.PROJECT_SUPPORT.PROJECT_SELECTION.PROJECT_SELECTION__shared import (  # noqa: E402
    resolve_project,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.carriers.content.content_constraints__shared import (  # noqa: E402
    compile_content_constraints,
    load_content_constraints as load_content_constraints,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.carriers.atom_population import (  # noqa: E402
    compile_atom_population_model,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.carriers.header.header_constraints__shared import (  # noqa: E402
    compile_header_constraints,
    load_header_constraints as load_header_constraints,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.carriers.header_ordering import (  # noqa: E402
    compile_header_ordering,
    load_header_ordering as load_header_ordering,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.sources.placement.placement_model import (  # noqa: E402
    compile_placement,
    load_placement as load_placement,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.carriers.role_form_schema import (  # noqa: E402
    compile_role_form,
    load_role_form,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.content.carrier_compat__pub import (  # noqa: E402
    canonical_role_name,
    carrier_read_view as carrier_read_view,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.carriers__shared import (  # noqa: E402
    carrier_status_folder as carrier_status_folder,
    matches_named_value as matches_named_value,
    named_value_token,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.content.carrier_read__pub import (  # noqa: E402
    parse_carrier as parse_carrier,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.content.carrier_compat__pub import (  # noqa: E402
    header_value,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model.notation.subject_notation_types import (  # noqa: E402
    SubjectNotationError,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model.notation.subject_notation_expression import (  # noqa: E402
    parse_subject_expression,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model.notation.subject_notation_render import (  # noqa: E402
    render_subject,
)
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import compile_content_schema  # noqa: E402
from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.FEATURE_IWE_CONSOLE_BACKEND__shared import (  # noqa: E402
    compile_schema,
    load_image_schema as load_image_schema,
    schema_asset,
)

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.sources.placement.placement_sources import (  # noqa: E402
    bootstrap_rows,
    inventory,
    read_selected,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.carriers.header_relation_rules import (  # noqa: E402
    compile_header_relation_rules,
    load_header_relation_rules as load_header_relation_rules,
)
from FEATURE_PROGRAMMATIC.FEATURE_FORMAL_MODEL_ENGINE.FEATURE_FORMAL_MODEL_ENGINE__shared import (  # noqa: E402
    Atom as Atom,
    DEPENDENCIES_CLAIM_SHA256,
    dependencies_are_distinct as dependencies_are_distinct,
    verify_packaged_dependencies_check,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    FEATURE_TOOLS__tests.declarations.legacy_work_report_model import (  # noqa: E402
    compile_work_report_target,
    verify_work_report_target as verify_work_report_target,
)


from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    FEATURE_TOOLS__tests.lifecycle._candidate_schema_read import (  # noqa: E402
    CandidateSchema as CandidateSchema,
    _MemoryAsset as _MemoryAsset,
    _canonical as _canonical,
    _validate_dependency_pin as _validate_dependency_pin,
    load_candidate_schema as load_candidate_schema,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    FEATURE_TOOLS__tests.lifecycle._candidate_schema_declarations import (  # noqa: E402
    _candidate_declarations as _candidate_declarations,
    _candidate_row as _candidate_row,
)

_DEPENDENCIES_SUBJECT = (
    "ANECHOIC_MODEL <+ Atom.Header.Context.Topics.Dependencies"
)


def _reject_unreviewed_dependencies(
    row, body, iter_formal_claims, parse_native_model_claim
):
    for code in iter_formal_claims(body.decode("utf-8")):
        if "dependencies_are_distinct" in code:
            parsed = parse_native_model_claim(code)
            if (
                parsed
                and (parsed.get("instance_check") or {}).get("name")
                == "dependencies_are_distinct"
            ):
                raise ValueError(
                    f"{row['source_path']}: Atom Dependencies check requires {_DEPENDENCIES_SUBJECT}"
                )


def _dependencies_declaration(rows):
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model.formal_claim__pub import (
        iter_formal_claims,
    )
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model.claims.native_model_claim__pub import (
        parse_native_model_claim,
    )

    selected = None
    for row in rows:
        _, subject = header_value(row["header_json"], "topics.main_subject")
        canonical = None
        if isinstance(subject, str):
            try:
                canonical = render_subject(parse_subject_expression(subject))
            except SubjectNotationError:
                pass
        body = row["_content_bytes"]
        if canonical == _DEPENDENCIES_SUBJECT:
            if selected is not None:
                raise ValueError(
                    f"Multiple Current Declarations for {_DEPENDENCIES_SUBJECT}"
                )
            selected = row
        elif b"dependencies_are_distinct" in body:
            _reject_unreviewed_dependencies(
                row, body, iter_formal_claims, parse_native_model_claim
            )
    if selected is None:
        return None
    blocks = tuple(
        iter_formal_claims(selected["_content_bytes"].decode("utf-8"))
    )
    if not blocks:
        return None
    if (
        len(blocks) != 1
        or hashlib.sha256(blocks[0].encode()).hexdigest()
        != DEPENDENCIES_CLAIM_SHA256
    ):
        raise ValueError(
            f"{selected['source_path']}: Atom Dependencies differs from the reviewed Python Claim"
        )
    verify_packaged_dependencies_check()
    return selected["source_path"]


def compile_candidate_schema(
    root: Path, placement_selection: Path | None = None
) -> bytes:  # noqa: C901
    """Compile Active Requirement/Declaration carriers from this root only."""
    root = Path(root)
    if not root.is_dir():
        raise ValueError(f"{root}: staged model root is not a directory")
    rows, relation_rows = _candidate_declarations(root)
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model.model_catalog__pub import (
        bindings_from_workbench_rows,
    )

    dependencies_source = _dependencies_declaration(rows)
    model_class_bindings = bindings_from_workbench_rows(rows)
    for row in rows:
        row["_model_class_bindings"] = model_class_bindings
    workbench = json.loads(
        schema_asset(rows, compile_schema(rows, compile_content_schema(rows)))
    )
    payload = {
        "schema_version": 2,
        "workbench": workbench,
        "role_form": compile_role_form(rows),
        "header_constraints": compile_header_constraints(rows),
        "content_constraints": compile_content_constraints(rows),
    }
    _add_candidate_optional_fields(
        payload, rows, relation_rows, workbench, dependencies_source
    )
    _add_candidate_placement(root, placement_selection, rows, payload)
    payload["digest"] = hashlib.sha256(_canonical(payload)).hexdigest()
    return _canonical(payload) + b"\n"


def _add_candidate_optional_fields(
    payload, rows, relation_rows, workbench, dependencies_source
):
    if work_report_target := compile_work_report_target(rows):
        payload["work_report_target"] = work_report_target
    if header_relation_rules := compile_header_relation_rules(
        rows + relation_rows
    ):
        payload["header_relation_rules"] = header_relation_rules
    if header_ordering := compile_header_ordering(rows):
        payload["header_ordering"] = header_ordering
    if compile_atom_population_model(rows):
        payload["atom_population_model"] = True
    if dependencies_source is not None:
        (pin,) = (
            pin
            for pin in workbench["sources"]
            if pin["path"] == dependencies_source
        )
        payload["atom_dependencies_check"] = {
            "claim_sha256": DEPENDENCIES_CLAIM_SHA256,
            "source": pin,
        }


def _add_candidate_placement(root, placement_selection, rows, payload):
    if placement_selection is None:
        delivery_rows = bootstrap_rows(inventory(root))
    else:
        selection_path = Path(placement_selection)
        if selection_path.is_symlink() or not selection_path.is_file():
            raise ValueError("placement selection is missing or is a symlink")
        try:
            selection = json.loads(selection_path.read_bytes())
        except (UnicodeError, json.JSONDecodeError) as error:
            raise ValueError(
                f"invalid placement selection: {error}"
            ) from error
        delivery_rows = read_selected(root, selection)
    roles = load_role_form(
        payload["role_form"], {row["id"] for row in rows}
    ).roles
    required_statuses = _candidate_required_statuses(rows, roles)
    placement = compile_placement(
        delivery_rows, rows, roles, required_statuses
    )
    if placement is not None:
        payload["placement"] = placement
    elif placement_selection is not None and required_statuses is not None:
        raise ValueError(
            "Placement selection has no authoritative placement rules"
        )


def _candidate_required_statuses(rows, roles):
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
        ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import (
        status_memberships,
    )

    status_memberships_by_role = set()
    for row in rows:
        status_memberships_by_role.update(
            (role, value)
            for role, _, value in status_memberships(
                row["_content_bytes"].decode("utf-8")
            )
        )
    required_statuses = None
    if status_memberships_by_role:
        required_statuses = {
            named_value_token(canonical_role_name(role)): {
                value
                for declared_role, value in status_memberships_by_role
                if declared_role is None
                or canonical_role_name(declared_role)
                == canonical_role_name(role)
            }
            for role in roles
        }
    return required_statuses


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--placement-selection", type=Path)
    args = parser.parse_args()
    try:
        payload = compile_candidate_schema(
            args.model_root, args.placement_selection
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(payload)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Candidate schema build failed: {error}\n")


def select_legacy_project(root, control_root):
    return resolve_project(root, control_root)


if __name__ == "__main__":
    main()
