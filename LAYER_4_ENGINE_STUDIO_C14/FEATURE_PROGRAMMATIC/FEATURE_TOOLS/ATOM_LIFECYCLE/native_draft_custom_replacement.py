from hashlib import sha256
from pathlib import Path
import re

from markdown_it import MarkdownIt
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    CEILINGS,
    ReadContext,
    frontmatter_bounds,
    native_carrier_path,
    parse_carrier,
    parse_content,
    parse_typed_manifest_node,
    revalidate_native,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.continuant_concern__pub import (
    continuant_model_subject, validate_continuant_variant,
)
from . import common, effects
from .effects import _project_write_lock
from .native_draft_guards import _summary
from .native_draft_source import _state_bytes
from .native_replacement_promotion import (
    _plan_replacements,
    _archive_replacements,
    _check_replacement_activation,
)
from .source import bind_query_reader


def _publish_custom_replacement(selection, draft, current_rows, previous_capture):
    relative, digest = draft.get('source_path'), draft.get('_source_sha256')
    if (
        not isinstance(relative, str)
        or not isinstance(digest, str)
        or not re.fullmatch(r"[0-9a-f]{64}", digest)
    ):
        raise common.SourceChanged(
            "Draft capture lacks a valid path or digest."
        )
    path = selection.root / relative
    if Path(relative).is_absolute() or '..' in Path(relative).parts:
        raise common.InputError('target', 'Draft path is invalid.')
    with _project_write_lock(selection.root):
        try:
            capture = revalidate_native(selection, previous_capture)
            if any(row.get('id') == draft['id'] and row.get('status_group') != 'Draft' for row in capture.atoms):
                raise common.SourceChanged('Replacement identity already has published history.')
            reader = ReadContext(roots=[str(selection.control_root)], limits=dict(CEILINGS))
            raw = reader.read(path)
            bounds = frontmatter_bounds(raw)
            header = draft['header_json']
            if (bounds is None or sha256(raw).hexdigest() != digest or raw[bounds[2]:] != draft['_content_bytes']
                    or parse_carrier(raw, path).metadata != header or reader.currentness()['state'] != 'unchanged'):
                raise common.SourceChanged('Draft source changed after selection.')
            body = raw[bounds[2]:].decode('utf-8')
            _validate_custom_manifest(header, body)
            config_root = selection.control_root / '__PROJECT_CONFIG'
            projected = native_carrier_path(header, _summary(body), project_root=selection.control_root, owner_directory=None)
            if path != config_root / 'CUSTOM_MODEL' / projected.relative_to(config_root):
                raise common.InputError('target', 'Custom Model Draft path disagrees with its Header and Summary.')
            active_header = {**header, 'state': {**header['state'], 'status': 'active'}}
            projected = native_carrier_path(active_header, _summary(body), project_root=selection.control_root, owner_directory=None)
            destination = config_root / 'CUSTOM_MODEL' / projected.relative_to(config_root)
            if destination.exists() or destination.is_symlink() or destination.parent.is_symlink() or not destination.parent.is_dir():
                raise common.InputError('target', 'The promotion destination already exists or is unsafe.')
            promoted = _state_bytes(raw, bounds, path, 1, body, 'active')
            plans = _plan_replacements(selection, draft, current_rows, None, capture)
            _check_replacement_activation([draft], capture.atoms, {row['id'] for row, *_ in plans})
        except (common.InputError, common.SourceChanged):
            raise
        except (OSError, RuntimeError, TypeError, ValueError) as error:
            raise common.SourceChanged('Native Custom Model Draft is unavailable or changed.') from error
        return _commit_custom_replacement(selection, draft, path, digest, destination, promoted, plans)


def _validate_custom_manifest(header, body):
    content = parse_content(body)
    if header.get("concern") is not None:
        continuant_model_subject(header["concern"])
        if any(
            section["property_path"] == ["claim_scope"] for section in content
        ):
            raise common.InputError(
                "target", "Concern and Claim scope cannot be combined."
            )
    sections = [
        section
        for section in content
        if section["property_path"] == ["formal_manifest"]
    ]
    tokens = []
    if len(sections) == 1:
        markdown = sections[0]["direct_markdown"] or ""
        tokens = MarkdownIt("commonmark").parse(markdown)
    if (
        len(tokens) != 1
        or tokens[0].type != "fence"
        or tokens[0].info.strip() != "python anechoic-edsl"
    ):
        raise common.InputError("target", "A typed node manifest is required.")
    source = tokens[0].content
    parse_typed_manifest_node(source)
    template = header.get("context", {}).get("template")
    validate_continuant_variant(header.get("concern"), template, source)


def _commit_custom_replacement(
    selection, draft, path, digest, destination, promoted, plans
):
    archived = _archive_replacements(selection, plans, draft)
    if archived["outcome"] != "completed":
        return archived
    with bind_query_reader(None):
        written = common.write_destination(
            selection.root, destination, promoted
        )
        recorded, errors = (
            archived["effects"] + list(written.effects),
            list(written.errors),
        )
        if not errors:
            removed = effects.remove(selection.root, path, digest)
            recorded.extend(removed.effects)
            errors.extend(removed.errors)
    data = (
        {}
        if errors
        else {
            "artifact": common.saved(
                selection, destination, draft["id"], draft["id"], 1, "active"
            )
        }
    )
    return common.result(effects=recorded, errors=errors, **data)
