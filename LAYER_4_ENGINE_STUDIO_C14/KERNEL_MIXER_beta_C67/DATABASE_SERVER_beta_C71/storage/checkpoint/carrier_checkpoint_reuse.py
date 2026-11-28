"""Read and update carrier checkpoint reuse state."""


def _validated_hashes(connection, scope):
    from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.storage.checkpoint import checkpoint__shared as checkpoint

    hashes = checkpoint.read_checkpoint(connection, scope)
    if hashes is not None:
        warning_paths = connection.execute(
            """SELECT DISTINCT relative_path FROM main.ops_ingestion_issues
            WHERE source IN ('atom', 'archive') AND relative_path IS NOT NULL
            AND """
            + checkpoint._scope_filter(
                scope,
                (
                    "coalesce(nullif(parse_dirpath(relative_path, "
                    "'forward_slash'), ''), '.')"
                ),
            )
        ).fetchall()
        if any(path not in hashes for (path,) in warning_paths):
            hashes = None
    return hashes


def _reuse_result(connection, scope=None):
    from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.storage.checkpoint import checkpoint__shared as checkpoint

    from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.realization_support.archive_generation.archive_generation__shared import archive_pending
    from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.realization_support.model.accepted_model import generation_rows
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.header.header__shared import (
        status_domains as _status_domains,
    )

    if not checkpoint.has_table(connection, "main", "ops_generation_reuse"):
        return None
    row = connection.execute(
        (
            "SELECT g.id, r.witness FROM ops_generation g CROSS JOIN "
            "ops_generation_reuse r"
        )
    ).fetchone()
    if row is None:
        return None
    witness = checkpoint.json.loads(row[1])
    generation = generation_rows(connection)
    if len(generation) != 1 or generation[0][0] != row[0]:
        raise ValueError("Reuse generation has no matching admitted Model")
    domains = _status_domains(
        checkpoint.json.loads(generation[0][1])["bindings"]
    )
    result = {
        "base_generation": row[0],
        **witness,
        "status_domains": {
            key: sorted(values) for key, values in domains.items()
        },
    }
    hashes = _validated_hashes(connection, scope)
    if hashes is not None:
        result["carrier_hashes"] = hashes
    folders = checkpoint._read_folders(connection, witness, hashes, scope)
    if folders is not None:
        result["folder_hashes"] = folders
    if scope is not None:
        result["checkpoint_scope"] = scope
    if archive_pending(connection):
        result["archive_pending"] = True
    return result


async def _update_reuse(
    request,
    connection,
    instance_id,
    lock,
    read_object,
    error_response,
    change_archive_pending,
    GenerationBaseChanged,
):
    from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.storage.checkpoint import checkpoint__shared as checkpoint

    try:
        data = await read_object(
            request,
            4096,
            {"instance_id", "base_generation", "archive_pending"},
        )
        if data["instance_id"] != instance_id:
            return error_response(
                "foreign_instance", "Instance does not match", 403
            )
        if data["archive_pending"] is not True:
            raise ValueError("Invalid startup archive transition")
        with lock:
            generation = change_archive_pending(
                connection, data["base_generation"], True
            )
        return checkpoint.JSONResponse({"result": {"generation": generation}})
    except GenerationBaseChanged as error:
        return error_response("generation_base_changed", str(error), 409)
    except (ValueError, TypeError) as error:
        return error_response("invalid_generation", str(error), 400)


def reuse_route(connection, instance_id, lock, read_object, error_response):
    from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.storage.checkpoint import checkpoint__shared as checkpoint

    from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.realization_support.archive_generation.archive_generation__shared import change_archive_pending
    from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.storage.generation.generation__shared import GenerationBaseChanged

    async def reuse(request):
        if request.method == "PUT":
            return await _update_reuse(
                request,
                connection,
                instance_id,
                lock,
                read_object,
                error_response,
                change_archive_pending,
                GenerationBaseChanged,
            )
        query = list(request.query_params.multi_items())
        if query not in (
            [("instance_id", instance_id)],
            [("instance_id", instance_id), ("scope", "foreground")],
            [("instance_id", instance_id), ("scope", "archive")],
        ):
            return error_response(
                "foreign_instance", "Instance does not match", 403
            )
        with lock:
            return checkpoint.JSONResponse(
                {
                    "result": checkpoint._reuse_result(
                        connection, query[1][1] if len(query) == 2 else None
                    )
                }
            )

    return reuse
