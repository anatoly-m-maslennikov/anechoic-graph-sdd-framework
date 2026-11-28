"""Collect native carrier rows after capture admission."""


def _incremental_inputs(source, state, options, callbacks):
    selection, reader, previous, paths, manifest = source
    versions, hashes, classified, missing, issues = state
    _, include_content_properties, _, _, _, domains = options
    changed_inputs, capture_inputs, _, _, _ = callbacks
    previous_rows = {
        row["source_path"]: (row, edge)
        for row, edge in zip(previous.atoms, previous.containment)
    }
    candidates, errors, input_paths = changed_inputs(
        reader, selection, previous, paths
    )
    issues.extend(
        issue
        for issue in previous.ingestion_issues
        if issue["relative_path"] in errors
    )
    capture_inputs(
        reader,
        selection,
        input_paths,
        manifest,
        True,
        previous,
        previous_rows,
        candidates,
        errors,
        issues,
        versions,
        missing,
        hashes,
        include_content_properties=include_content_properties,
        domains=domains,
        classified=classified,
    )
    return candidates, errors


def _full_inputs(source, state, options, callbacks):
    selection, reader, _, _, manifest = source
    _, hashes, classified, _, issues = state
    (
        _,
        include_content_properties,
        _,
        defer_archives,
        archive_roots,
        domains,
    ) = options
    _, _, capture_full, _, _ = callbacks
    candidates, errors = {}, {}
    capture_full(
        reader,
        selection,
        manifest,
        candidates,
        errors,
        issues,
        hashes,
        include_content_properties=include_content_properties,
        defer_archives=defer_archives,
        archive_roots=archive_roots,
        domains=domains,
        classified=classified,
    )
    return candidates, errors


def collect_native_capture(
    selection, reader, previous, paths, manifest, options, callbacks
):
    incremental, _, defer_currentness, _, _, domains = options
    versions, hashes = (
        (dict(previous.versions), dict(previous.carrier_hashes))
        if incremental
        else ({}, {})
    )
    classified = dict(previous.classified_templates) if incremental else {}
    missing, issues = [], []
    source = (selection, reader, previous, paths, manifest)
    state = (versions, hashes, classified, missing, issues)
    candidates, errors = (
        _incremental_inputs(source, state, options, callbacks)
        if incremental
        else _full_inputs(source, state, options, callbacks)
    )
    _, _, _, capture_changed, unique_revisions = callbacks
    if capture_changed(reader, missing, defer_currentness):
        raise ValueError("Native Project carriers changed during capture")
    versions.update(reader.versions)
    return unique_revisions(
        candidates,
        errors,
        versions,
        issues,
        hashes,
        selection.manifest_path.relative_to(selection.root).as_posix(),
        domains,
        classified,
    )
