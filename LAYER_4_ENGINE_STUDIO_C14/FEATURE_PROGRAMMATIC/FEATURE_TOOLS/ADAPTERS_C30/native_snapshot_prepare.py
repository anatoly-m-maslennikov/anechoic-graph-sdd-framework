"""Prepare native snapshot inputs without publishing them."""


def _archive_versions(
    versions,
    deferred,
    selection,
    archived,
    startup_reader,
    scan_archive_versions,
):
    if versions is not None and deferred is not None:
        versions.update(
            scan_archive_versions(
                startup_reader(selection.root, archive=True),
                deferred,
                archived.atoms,
                selection.project_prefix,
            )
        )


def _scan_initial(selection, archive_stage, archive_roots, domains, functions):
    (
        _,
        startup_reader,
        archive_directories,
        capture_native,
        partition_archived,
        _,
    ) = functions
    reader = startup_reader(
        selection.root,
        "foreground_capture" if archive_stage == "foreground" else None,
        archive=archive_stage == "archive",
    )
    deferred = set() if archive_stage == "foreground" else None
    directories = (
        archive_directories(selection, archive_roots)
        if archive_stage == "archive"
        else None
    )
    capture = capture_native(
        selection,
        reader=reader,
        defer_currentness=True,
        include_content_properties="summary",
        defer_archives=deferred,
        archive_roots=directories,
        domains=domains,
    )
    foreground, archived = (
        partition_archived(capture)
        if deferred is not None
        else (capture, None)
    )
    return reader, deferred, directories, capture, foreground, archived


def initial_capture(
    binding,
    archive_stage,
    archive_roots,
    archive_versions,
    domains,
    functions,
):
    selection_for = functions[0]
    startup_reader, scan_archive_versions = functions[1], functions[5]
    selection = selection_for(binding)
    reader, deferred, directories, capture, foreground, archived = (
        _scan_initial(
            selection, archive_stage, archive_roots, domains, functions
        )
    )
    _archive_versions(
        archive_versions,
        deferred,
        selection,
        archived,
        startup_reader,
        scan_archive_versions,
    )
    manifest_path = selection.manifest_path.relative_to(
        selection.root
    ).as_posix()

    return (
        selection,
        reader,
        foreground,
        archived,
        capture,
        deferred,
        directories,
        manifest_path,
    )


def make_finish(context, finish_snapshot, functions):
    def finish(endpoints, admitted_domains=None):
        return finish_snapshot(
            context, endpoints, admitted_domains, functions()
        )

    return finish


def generation_result(
    selection,
    foreground,
    archive_stage,
    finish,
    include_model_inputs,
    include_spec_rows,
    graph_config,
    model_inputs,
):
    result = (
        None if archive_stage == "archive" else graph_config(selection),
        finish,
    )
    return (
        (
            *result,
            model_inputs(
                selection, foreground, include_spec_rows=include_spec_rows
            ),
        )
        if include_model_inputs
        else result
    )
