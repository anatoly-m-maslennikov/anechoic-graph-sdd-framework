"""Commit and safely roll back a native revision."""

from . import native_draft_revision__shared as origin


def _rollback_promotion(
    selection, previous_path, previous_digest, created, recorded, errors
):
    errors = list(errors)
    for path, raw in reversed(created):
        try:
            reader = origin.ReadContext(
                roots=[str(selection.root)], limits=dict(origin.CEILINGS)
            )
            if (
                origin.sha256(reader.read(previous_path)).hexdigest()
                != previous_digest
            ):
                raise ValueError("Current changed")
            if reader.currentness()["state"] != "unchanged":
                raise ValueError("Current changed")
        except OSError, RuntimeError, ValueError:
            errors.append(
                {
                    "code": "rollback_unconfirmed",
                    "message": "Current is no longer pinned; "
                    "generated carriers were retained.",
                }
            )
            break
        removed = origin.effects.remove(
            selection.root, path, origin.sha256(raw).hexdigest()
        )
        recorded.extend(removed.effects)
        if removed.errors:
            errors.extend(removed.errors)
            errors.append(
                {
                    "code": "rollback_unconfirmed",
                    "message": "A generated carrier could not be "
                    "safely removed.",
                }
            )
    return origin.common.result(effects=recorded, errors=errors)


def _commit_revision(
    selection,
    status,
    draft,
    previous,
    paths,
    archive_path,
    destination,
    archive,
    promoted,
    atom_id,
    version,
):
    draft_path, previous_path = paths
    recorded, created = [], []
    state = created, recorded
    with origin.bind_query_reader(None):
        failure = _write_archive(
            selection, previous, (previous_path, archive_path, archive), state
        )
        if failure is not None:
            return failure
        failure = _recheck_sources(selection, draft, previous, paths, state)
        if failure is not None:
            return failure
        failure = _publish_revision(
            selection, previous, (previous_path, destination, promoted), state
        )
        if failure is not None:
            return failure
        removed = origin.effects.remove(
            selection.root, draft_path, draft["_source_sha256"]
        )
        recorded.extend(removed.effects)
    return _revision_result(
        selection, destination, atom_id, version, status, recorded, removed
    )


def _write_archive(selection, previous, paths, state):
    previous_path, archive_path, archive = paths
    created, recorded = state
    written = origin.common.write_destination(
        selection.root, archive_path, archive
    )
    recorded.extend(written.effects)
    if any(
        item.get("operation") == "create"
        and item.get("target")
        == archive_path.relative_to(selection.root).as_posix()
        for item in written.effects
    ):
        created.append((archive_path, archive))
    if written.errors:
        return origin._rollback_promotion(
            selection,
            previous_path,
            previous["_source_sha256"],
            created,
            recorded,
            written.errors,
        )
    return None


def _recheck_sources(selection, draft, previous, paths, state):
    draft_path, previous_path = paths
    created, recorded = state
    try:
        reader = origin.ReadContext(
            roots=[str(selection.root)], limits=dict(origin.CEILINGS)
        )
        if (
            origin.sha256(reader.read(draft_path)).hexdigest()
            != draft["_source_sha256"]
            or origin.sha256(reader.read(selection.manifest_path)).hexdigest()
            != selection.manifest_sha256
            or reader.currentness()["state"] != "unchanged"
        ):
            raise ValueError("Source changed")
    except OSError, RuntimeError, ValueError:
        return origin._rollback_promotion(
            selection,
            previous_path,
            previous["_source_sha256"],
            created,
            recorded,
            [
                {
                    "code": "source_changed",
                    "message": "Draft or Manifest changed after archival.",
                }
            ],
        )
    return None


def _publish_revision(selection, previous, paths, state):
    previous_path, destination, promoted = paths
    created, recorded = state
    if destination == previous_path:
        published = origin.effects.replace(
            selection.root,
            previous_path,
            previous["_source_sha256"],
            promoted,
        )
        recorded.extend(published.effects)
        if published.errors:
            return origin._rollback_promotion(
                selection,
                previous_path,
                previous["_source_sha256"],
                created,
                recorded,
                published.errors,
            )
    else:
        return _move_revision(selection, previous, paths, state)
    return None


def _move_revision(selection, previous, paths, state):
    previous_path, destination, promoted = paths
    created, recorded = state
    published = origin.common.write_destination(
        selection.root, destination, promoted
    )
    recorded.extend(published.effects)
    if any(
        item.get("operation") == "create"
        and item.get("target")
        == destination.relative_to(selection.root).as_posix()
        for item in published.effects
    ):
        created.append((destination, promoted))
    if published.errors:
        return origin._rollback_promotion(
            selection,
            previous_path,
            previous["_source_sha256"],
            created,
            recorded,
            published.errors,
        )
    removed = origin.effects.remove(
        selection.root, previous_path, previous["_source_sha256"]
    )
    recorded.extend(removed.effects)
    if removed.errors:
        return origin._rollback_promotion(
            selection,
            previous_path,
            previous["_source_sha256"],
            created,
            recorded,
            removed.errors,
        )
    return None


def _revision_result(
    selection, destination, atom_id, version, status, recorded, removed
):
    data = (
        {}
        if removed.errors
        else {
            "artifact": origin.common.saved(
                selection, destination, atom_id, atom_id, version, status
            )
        }
    )
    return origin.common.result(
        effects=recorded, errors=removed.errors, **data
    )
