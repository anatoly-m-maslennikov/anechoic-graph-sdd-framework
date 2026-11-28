"""Create and validate Project-owned Axiom and Applicable Principle Drafts."""

from datetime import datetime, timezone

import yaml

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.header.header__shared import (
    canonical_native_header,
    native_carrier_path,
    native_header_view,
    spec_lens_directories,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.sources.inventory.inventory__shared import (
    revalidate_native,
)

from ... import common
from ...sources.source__shared import bind_query_reader

PROJECT_SPEC_TEMPLATES = {"project_contract", "axiom", "applicable_principle"}


def _project_spec_model(validate):
    model = getattr(validate, "__self__", None)
    if not callable(getattr(model, "project_spec_template", None)):
        raise common.InputError(
            "newAtom", "Project SPEC validation requires the admitted Model."
        )
    return model


def project_spec_template(template, validate):
    return _project_spec_model(validate).project_spec_template(template)


def validate_project_spec(header, validate, body=None):
    _project_spec_model(validate)
    view = native_header_view(header)
    context = view["context"]
    template = context.get("template")
    container = context.get("container")
    if (
        container != {"component": "C00"}
        or type(context.get("tier")) is not int
    ):
        raise common.InputError(
            "newAtom",
            "Project SPEC requires its declared Tier and Project C00 container.",
        )
    try:
        validate(template, header, "C00", body)
    except (ValueError, TypeError, KeyError) as error:
        raise common.InputError(
            "newAtom",
            f"Project SPEC does not satisfy the compiled Model: {error}",
        ) from error


def _project_spec_preflight(values, validate):
    if (
        not isinstance(values, dict)
        or set(values) - {"tier"} != {"template", "container", "lens", "body"}
        or not isinstance(values.get("template"), str)
        or values.get("container") != {"component": "C00"}
        or not isinstance(values.get("body"), str)
        or not isinstance(values.get("lens"), str)
    ):
        raise common.InputError(
            "newAtom",
            "Supply a Project SPEC template, Project C00, Lens, and Markdown body.",
        )
    try:
        declaration = project_spec_template(values["template"], validate)
    except common.InputError:
        raise
    except ValueError as error:
        raise common.InputError("newAtom", str(error)) from error
    if declaration is None or not declaration[2]:
        raise common.InputError(
            "newAtom",
            "The compiled Model does not enable this Project SPEC Template for creation.",
        )
    tier = values.get("tier", declaration[1])
    if type(tier) is not int:
        raise common.InputError(
            "tier", "Tier must match the selected Project SPEC template."
        )
    try:
        spec_lens_directories(values["lens"])
    except ValueError as error:
        raise common.InputError("lens", "Supply a valid Lens.") from error
    return tier


def _draft_header(selection, capture, values, tier):
    prefix = selection.project_prefix
    number = common.next_native_number(selection, capture, "S")
    atom_id = f"{prefix}-S-{number}"
    header = canonical_native_header(
        {
            "identity": {"atom_id": atom_id},
            "context": {
                "container": {"component": "C00"},
                "tier": tier,
                "template": values["template"],
                "lens": values["lens"],
            },
            "state": {
                "status": "draft",
                "version": 1,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
        }
    )
    return atom_id, header


def _project_spec_carrier(selection, header, summary, body):
    try:
        path = native_carrier_path(
            header,
            summary,
            project_root=selection.control_root,
            owner_directory=selection.control_root,
        )
        raw = (
            b"---\n"
            + yaml.safe_dump(header, sort_keys=False).encode()
            + b"---\n"
            + body.encode("utf-8")
        )
    except (ValueError, UnicodeError) as error:
        raise common.InputError(
            "summary", "Summary cannot be used in a Project SPEC filename."
        ) from error
    return path, raw


def create_project_spec(selection, values, validate, previous_capture=None):
    from ..native_draft__shared import _first_spec_write_lock, _summary

    tier = _project_spec_preflight(values, validate)
    summary = _summary(values["body"])
    if (
        not selection.root.is_absolute()
        or not selection.control_root.is_relative_to(selection.root)
        or selection.manifest_path.parent
        not in {selection.root, selection.control_root}
    ):
        raise common.SourceChanged("Selected Project path is invalid.")
    with _first_spec_write_lock(selection.root):
        try:
            capture = revalidate_native(selection, previous_capture)
        except (OSError, RuntimeError, ValueError) as error:
            raise common.SourceChanged(
                "Native carriers changed during Project SPEC selection."
            ) from error
        if capture.errors:
            raise common.SourceChanged("Native carrier capture is incomplete.")
        atom_id, header = _draft_header(selection, capture, values, tier)
        validate_project_spec(header, validate, values["body"])
        path, raw = _project_spec_carrier(
            selection, header, summary, values["body"]
        )
        with bind_query_reader(None):
            outcome = common.write_destination(selection.root, path, raw)
        data = (
            {}
            if outcome.errors
            else {
                "savedDraft": common.saved(
                    selection, path, atom_id, f"{atom_id}@1-draft", 1, "Draft"
                )
            }
        )
        if data:
            data["savedDraft"]["updated_at"] = header["state"]["updated_at"]
        return common.result(
            effects=outcome.effects, errors=outcome.errors, **data
        )
