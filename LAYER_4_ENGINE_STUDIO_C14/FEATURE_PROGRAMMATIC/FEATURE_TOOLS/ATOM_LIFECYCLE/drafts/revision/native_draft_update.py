"""Update the body and authored relations of one exact native Draft."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re

import yaml

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    CEILINGS,
    ReadContext,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.content.content__shared import (
    frontmatter_bounds,
    parse_carrier,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.sources.inventory.inventory__shared import (
    revalidate_native,
)
from ... import effects
from ...common import InputError, SourceChanged, result, saved
from ...effects import _project_write_lock
from ..native_draft_guards import _summary
from ...sources.source__shared import bind_query_reader


def _validate_target(selection, target):
    if (
        not isinstance(target, dict)
        or set(target) != {"ref_id", "version"}
        or not isinstance(target["ref_id"], str)
        or type(target["version"]) is not int
        or target["version"] < 1
        or not re.fullmatch(
            re.escape(selection.project_prefix)
            + rf"-[STPC]-[0-9]+@{target['version']}-draft",
            target["ref_id"],
        )
    ):
        raise InputError(
            "target", "Supply an exact Draft reference and matching Version."
        )


def _validate_input(selection, params):
    if (
        not isinstance(params, dict)
        or set(params) - {"target", "changes", "expectedUpdatedAt"}
        or not {"target", "changes"} <= set(params)
    ):
        raise InputError("target", "Supply an exact Draft target and changes.")
    target, changes = params["target"], params["changes"]
    _validate_target(selection, target)
    if (
        not isinstance(changes, dict)
        or not changes
        or set(changes) - {"body", "removeRelations"}
        or "body" in changes
        and not isinstance(changes["body"], str)
        or "removeRelations" in changes
        and (
            not isinstance(changes["removeRelations"], list)
            or any(
                not isinstance(item, dict)
                or set(item) != {"type", "ref_id"}
                or any(not isinstance(v, str) or not v for v in item.values())
                for item in changes["removeRelations"]
            )
        )
    ):
        raise InputError(
            "changes",
            "Supply a Markdown body or authored relations to remove.",
        )
    if "expectedUpdatedAt" in params and not isinstance(
        params["expectedUpdatedAt"], str
    ):
        raise InputError(
            "expectedUpdatedAt", "Supply the Draft updated_at timestamp."
        )
    return target, changes


def _selected_draft(selection, target, current_rows):
    matches = [
        r
        for r in current_rows
        if r.get("_exact_ref") == target["ref_id"]
        and r.get("status_group") == "Draft"
        and r.get("version") == target["version"]
    ]
    if len(matches) != 1:
        raise SourceChanged("Draft selection is missing, ambiguous, or stale.")
    selected = matches[0]
    relative, digest = (
        selected.get("source_path"),
        selected.get("_source_sha256"),
    )
    if (
        not isinstance(relative, str)
        or not isinstance(digest, str)
        or not re.fullmatch(r"[0-9a-f]{64}", digest)
    ):
        raise SourceChanged("Draft capture lacks a path or digest.")
    relative = Path(relative)
    path = selection.root / relative
    if (
        relative.is_absolute()
        or ".." in relative.parts
        or not path.is_relative_to(selection.control_root)
        or path.parent.name not in {"01_draft", "000_draft"}
    ):
        raise InputError("target", "Select a native Draft carrier.")
    return selected, digest, path


def update_draft(selection, params, *, current_rows, previous_capture=None):
    target, changes = _validate_input(selection, params)
    selected, digest, path = _selected_draft(selection, target, current_rows)
    with _project_write_lock(selection.root):
        candidate, updated = _prepare(
            selection,
            params,
            changes,
            target,
            selected,
            digest,
            path,
            previous_capture,
        )
        artifact = saved(
            selection,
            path,
            selected["id"],
            target["ref_id"],
            target["version"],
            "Draft",
        ) | {"updated_at": updated}
        if candidate is None:
            return result(artifact=artifact)
        with bind_query_reader(None):
            outcome = effects.replace(selection.root, path, digest, candidate)
        data = {} if outcome.errors else {"artifact": artifact}
        return result(effects=outcome.effects, errors=outcome.errors, **data)


def _verified_draft(
    selection, target, selected, digest, path, previous_capture
):
    capture = revalidate_native(selection, previous_capture)
    fresh = [
        r for r in capture.atoms if r.get("_exact_ref") == target["ref_id"]
    ]
    keys = (
        "source_path",
        "id",
        "ref",
        "_exact_ref",
        "version",
        "status",
        "status_group",
        "header_json",
        "_content_bytes",
        "_source_sha256",
    )
    if (
        capture.errors
        or len(fresh) != 1
        or any(fresh[0].get(k) != selected.get(k) for k in keys)
    ):
        raise SourceChanged("Draft changed after selection.")
    raw = ReadContext(roots=[str(selection.root)], limits=dict(CEILINGS)).read(
        path
    )
    bounds = frontmatter_bounds(raw)
    if (
        bounds is None
        or sha256(raw).hexdigest() != digest
        or parse_carrier(raw, path).metadata != selected["header_json"]
        or raw[bounds[2] :] != selected["_content_bytes"]
    ):
        raise SourceChanged("Draft changed after selection.")
    return raw, bounds


def _prepare(
    selection,
    params,
    changes,
    target,
    selected,
    digest,
    path,
    previous_capture,
):
    try:
        raw, bounds = _verified_draft(
            selection, target, selected, digest, path, previous_capture
        )
        header = selected["header_json"]
        stamp = header.get("state", {}).get("updated_at")
        observed = stamp.isoformat() if isinstance(stamp, datetime) else stamp
        if (
            "expectedUpdatedAt" in params
            and observed != params["expectedUpdatedAt"]
        ):
            raise SourceChanged(
                "Draft updated_at does not match the expected timestamp."
            )
        old_body = raw[bounds[2] :].decode("utf-8")
        body = changes.get("body", old_body)
        if _summary(body) != _summary(old_body):
            raise InputError("summary", "Changing a Summary is not supported.")
        candidate = _candidate(
            raw, bounds, path, header, body, changes.get("removeRelations", [])
        )
        return candidate if candidate is not None else (None, observed)
    except InputError, SourceChanged:
        raise
    except (
        OSError,
        RuntimeError,
        TypeError,
        ValueError,
        KeyError,
        UnicodeError,
        yaml.YAMLError,
    ) as error:
        message = "Draft source is unavailable or changed."
        raise SourceChanged(message) from error


def _draft_header(header, before, removals):
    node = yaml.compose(header, Loader=yaml.SafeLoader)
    fields = {key.value: value for key, value in node.value}
    state = fields["state"]
    timestamps = [
        value for key, value in state.value if key.value == "updated_at"
    ]
    if len(timestamps) != 1 or not isinstance(timestamps[0], yaml.ScalarNode):
        raise InputError(
            "target", "Draft requires a scalar updated_at timestamp."
        )
    relations = before.get("relations", {})
    if not isinstance(relations, dict):
        raise InputError("changes", "Draft relations are invalid.")
    relations = {
        k: list(v) if isinstance(v, list) else v for k, v in relations.items()
    }
    for item in removals:
        values = relations.get(item["type"])
        if not isinstance(values, list) or item["ref_id"] not in values:
            raise InputError(
                "changes", "Remove only relations authored on this Draft."
            )
        values.remove(item["ref_id"])
        if not values:
            del relations[item["type"]]
    return node, timestamps[0], relations


def _candidate(raw, bounds, path, before, body, removals):
    header = raw[bounds[0] : bounds[1]].decode("utf-8")
    node, stamp, relations = _draft_header(header, before, removals)
    body_bytes = body.encode("utf-8")
    if not removals and body_bytes == raw[bounds[2] :]:
        return None
    updated = datetime.now(timezone.utc).isoformat()
    edits = [
        (stamp.start_mark.index, stamp.end_mark.index, json.dumps(updated))
    ]
    expected = dict(before)
    if removals:
        relation_key, relation_node = next(
            (key, value)
            for key, value in node.value
            if key.value == "relations"
        )
        end = relation_node.end_mark.index
        newline = (
            "\n"
            if header[relation_key.start_mark.index : end].endswith("\n")
            else ""
        )
        edits.append(
            (
                relation_key.start_mark.index,
                end,
                "relations: " + json.dumps(relations) + newline,
            )
        )
        expected["relations"] = relations
    expected["state"] = {**before["state"], "updated_at": updated}
    for start, end, value in sorted(edits, reverse=True):
        header = header[:start] + value + header[end:]
    candidate = (
        raw[: bounds[0]]
        + header.encode("utf-8")
        + raw[bounds[1] : bounds[2]]
        + body_bytes
    )
    if parse_carrier(candidate, path).metadata != expected:
        raise InputError(
            "changes", "The Draft header cannot be updated safely."
        )
    return candidate, updated
