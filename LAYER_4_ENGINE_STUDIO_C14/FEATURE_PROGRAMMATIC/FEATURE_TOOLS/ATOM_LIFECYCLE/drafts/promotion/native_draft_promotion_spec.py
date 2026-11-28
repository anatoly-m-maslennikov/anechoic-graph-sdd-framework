"""Preflight the first publication of a native Spec Draft."""


def _preflight_first_spec(
    selection,
    draft,
    structure_snapshot,
    previous_capture,
    validate_project_spec_model,
    atom_id,
    ref_id,
    path,
    digest,
):
    from . import native_draft_promotion__shared as p
    from ..native_draft__shared import _validate_project_template

    try:
        capture = p.revalidate_native(selection, previous_capture)
        _check_history(capture, draft, atom_id, ref_id)
        header = draft["header_json"]
        destination, owner = _spec_destination(
            selection,
            draft,
            structure_snapshot,
            validate_project_spec_model,
            atom_id,
            ref_id,
            path,
            header,
        )
        promoted, version = _spec_bytes(
            selection,
            draft,
            path,
            digest,
            header,
            owner,
            destination,
            validate_project_spec_model,
            _validate_project_template,
        )
    except p.common.InputError, p.common.SourceChanged:
        raise
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        raise p.common.SourceChanged(
            "Native Spec source is unavailable or changed."
        ) from error
    return destination, promoted, version, capture


def _check_history(capture, draft, atom_id, ref_id):
    from . import native_draft_promotion__shared as p

    history = [row for row in capture.atoms if row["id"] == atom_id]
    matching = [row for row in history if row["_exact_ref"] == ref_id]
    if (
        capture.errors
        or matching != [draft]
        or any(row["status_group"] != "Draft" for row in history)
    ):
        raise p.common.SourceChanged(
            "Spec Draft changed or the identity has published revisions."
        )


def _check_template(context, header, path, validate_project_spec_model):
    from . import native_draft_promotion__shared as p

    if (
        context.get("template") not in (None, *p.PROJECT_SPEC_TEMPLATES)
        and not (
            validate_project_spec_model
            and p.project_spec_template(
                context.get("template"), validate_project_spec_model
            )
        )
        and not p.is_c9_typed_manifest(header)
        or p.re.search(
            r"-(?:PROJECT|COMPONENT)_MANIFEST(?:--|\.md$)", path.name, p.re.I
        )
    ):
        raise p.common.InputError(
            "target",
            (
                "Select a Spec Draft with a lens and without a structural "
                "template."
            ),
        )


def _spec_destination(
    selection,
    draft,
    structure_snapshot,
    validate_project_spec_model,
    atom_id,
    ref_id,
    path,
    header,
):
    from . import native_draft_promotion__shared as p

    context = p.native_header_view(header)["context"]
    lens = context.get("lens")
    _check_template(context, header, path, validate_project_spec_model)
    owner = path.parent.parent
    try:
        p.spec_lens_directories(lens)
        directory = owner / p.READY_DIRECTORY
    except ValueError as error:
        raise p.common.InputError(
            "target", "Select a Spec Draft with a valid Lens."
        ) from error
    destination = directory / (atom_id + path.name[len(ref_id) :])
    proposed = {
        **draft,
        "source_path": destination.relative_to(selection.root).as_posix(),
        "status": "ready",
    }
    if p._revision_root(selection, proposed, structure_snapshot) != owner:
        raise p.common.InputError(
            "target",
            (
                "Spec Draft and Current carrier must belong to the same "
                "Component."
            ),
        )
    if destination.exists() or destination.is_symlink():
        raise p.common.InputError(
            "target", "The promotion destination already exists."
        )
    return destination, owner


def _spec_bytes(
    selection,
    draft,
    path,
    digest,
    header,
    owner,
    destination,
    validate_project_spec_model,
    validate_project_template,
):
    from . import native_draft_promotion__shared as p

    reader = p.ReadContext(
        roots=[str(selection.control_root)], limits=dict(p.CEILINGS)
    )
    raw = reader.read(path)
    bounds = p.frontmatter_bounds(raw)
    if (
        bounds is None
        or p.sha256(raw).hexdigest() != digest
        or raw[bounds[2] :] != draft["_content_bytes"]
        or p.parse_carrier(raw, path).metadata != header
        or reader.currentness()["state"] != "unchanged"
    ):
        raise p.common.SourceChanged(
            "Spec Draft source changed after selection."
        )
    body = raw[bounds[2] :].decode("utf-8")
    p._check_first_spec(selection, header, body, path, owner)
    version = draft["version"]
    promoted = p._state_bytes(raw, bounds, path, version, body, "ready")
    validate_project_template(
        p.parse_carrier(promoted, destination).metadata,
        validate_project_spec_model,
        body,
    )
    return promoted, version
