"""Finalize a native generation snapshot."""


class NativeSnapshotChanged(ValueError):
    """Captured native sources changed before generation completed."""


def _recheck(
    selection,
    capture,
    deferred,
    directories,
    archive_stage,
    admitted_domains,
    startup_reader,
    capture_native,
    partition,
):
    reader = startup_reader(selection.root, archive=archive_stage == "archive")
    final = capture_native(
        selection,
        reader=reader,
        defer_currentness=True,
        include_content_properties="summary",
        domains=admitted_domains,
        defer_archives=set() if deferred is not None else None,
        archive_roots=directories,
    )
    if (
        final.carrier_hashes != capture.carrier_hashes
        or reader.currentness()["state"] != "unchanged"
    ):
        raise NativeSnapshotChanged(
            "Native Project carriers changed during generation"
        )
    return partition(final) if deferred is not None else (final, None)


def _archive_result(
    result,
    foreground,
    archived,
    deferred,
    selection,
    snapshot,
    binding,
    endpoints,
    manifest_path,
):
    return (
        result,
        foreground.carrier_hashes,
        sorted(
            path.relative_to(selection.root).as_posix() for path in deferred
        ),
        snapshot(binding, archived, endpoints, manifest_path=manifest_path),
        archived.carrier_hashes,
    )


def _check_currentness(reader, watcher_guarded, monotonic):
    if not watcher_guarded:
        reader.started = monotonic()
        if reader.currentness()["state"] != "unchanged":
            raise NativeSnapshotChanged(
                "Native Project carriers changed during generation"
            )


def finish_snapshot(context, endpoints, admitted_domains, functions):
    binding, selection, reader, foreground, archived, capture = context[:6]
    deferred, directories, domains, archive_stage = context[6:10]
    watcher_guarded, include_hashes, manifest_path = context[10:]
    (
        startup_reader,
        capture_native,
        status_domains,
        partition,
        snapshot,
        monotonic,
    ) = functions
    if admitted_domains is not None and admitted_domains != (
        domains or status_domains({})
    ):
        foreground, archived = _recheck(
            selection,
            capture,
            deferred,
            directories,
            archive_stage,
            admitted_domains,
            startup_reader,
            capture_native,
            partition,
        )
    result = snapshot(
        binding, foreground, endpoints, manifest_path=manifest_path
    )
    _check_currentness(reader, watcher_guarded, monotonic)
    if deferred is not None:
        return _archive_result(
            result,
            foreground,
            archived,
            deferred,
            selection,
            snapshot,
            binding,
            endpoints,
            manifest_path,
        )
    return (result, foreground.carrier_hashes) if include_hashes else result
