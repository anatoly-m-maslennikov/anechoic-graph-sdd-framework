"""Allocate and publish the archived SPEC Draft carrier."""

from hashlib import sha256

from ...common import SourceChanged


def _allocate_archived_spec(
    selection,
    target,
    draft,
    path,
    digest,
    owner,
    previous_capture,
    raw,
    bounds,
    body,
    header,
    used,
    version,
):
    from . import native_update_spec__shared as host
    from ... import common

    while version <= 2**63 - 1:
        if version in used:
            version += 1
            continue
        destination, archived = _archived_spec_carrier(
            selection, target, path, owner, raw, bounds, body, header, version
        )
        outcome = host._write_archived_spec(
            selection,
            target,
            draft,
            path,
            digest,
            destination,
            archived,
            version,
        )
        if not common.destination_collision(outcome):
            return outcome
        _recheck_archive_collision(
            host, selection, draft, path, digest, previous_capture
        )
        version += 1
    raise SourceChanged("No representable revision Version remains.")


def _write_archived_spec(
    selection, target, draft, path, digest, destination, archived, version
):
    from ... import common
    from . import native_update_spec__shared as host

    with host.bind_query_reader(None):
        written = common.write_destination(
            selection.root, destination, archived
        )
        recorded = list(written.effects)
        if written.errors:
            return host.result(effects=recorded, errors=written.errors)
        removed = host.effects.remove(selection.root, path, digest)
        recorded.extend(removed.effects)
        if removed.errors:
            errors = list(removed.errors)
            _restore_spec_after_failed_removal(
                host,
                selection,
                path,
                digest,
                destination,
                archived,
                removed,
                recorded,
                errors,
            )
            return host.result(effects=recorded, errors=errors)
    artifact = host.saved(
        selection,
        destination,
        draft["id"],
        f"{draft['id']}@{version}",
        version,
        "archived",
    )
    return host.result(
        effects=recorded, artifact=artifact, sourceRef=target["ref_id"]
    )


def _archived_spec_carrier(
    selection, target, path, owner, raw, bounds, body, header, version
):
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.header.header__shared import (
        native_carrier_path,
    )
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.drafts.sources.native_draft_source_details import (
        _state_bytes,
    )
    from ...drafts.native_draft__shared import (
        _summary,
    )

    projected = {
        **header,
        "state": {
            **header["state"],
            "status": "archived",
            "version": version,
        },
    }
    destination = native_carrier_path(
        projected,
        _summary(body),
        project_root=selection.control_root,
        owner_directory=owner,
    )
    archived = _state_bytes(
        raw,
        bounds,
        path,
        version,
        body,
        "archived",
        update_timestamp=version != target["version"],
    )
    return destination, archived


def _recheck_archive_collision(
    host, selection, draft, path, digest, previous_capture
):
    try:
        host._selected_spec_bytes(selection, draft, path, digest)
        refreshed = host.revalidate_native(selection, previous_capture)
        if refreshed.errors:
            raise SourceChanged("Native carrier capture is incomplete.")
    except (OSError, RuntimeError, ValueError) as error:
        raise SourceChanged("SPEC Draft changed after selection.") from error


def _restore_spec_after_failed_removal(
    host,
    selection,
    path,
    digest,
    destination,
    archived,
    removed,
    recorded,
    errors,
):
    if not removed.effects and not any(
        error.get("code") == "effect_uncertain" for error in errors
    ):
        try:
            if (
                sha256(
                    host.ReadContext(
                        roots=[str(selection.root)],
                        limits=dict(host.CEILINGS),
                    ).read(path)
                ).hexdigest()
                == digest
            ):
                rollback = host.effects.remove(
                    selection.root,
                    destination,
                    sha256(archived).hexdigest(),
                )
                recorded.extend(rollback.effects)
                errors.extend(rollback.errors)
        except OSError, RuntimeError, ValueError:
            pass
