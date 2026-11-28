"""Open journal sources and serve the private socket."""


def _open_sources(s, args, parser):
    native = args.journal_storage == "duckdb"
    root = args.project_root
    if native and root is None:
        parser.error("DuckDB Journal storage requires --project-root")
    if args.journal_relative is not None and root is None:
        parser.error("--journal-relative requires --project-root")
    file_journal = (
        (root, args.journal_relative)
        if args.journal_relative is not None
        else None
    )
    if file_journal is not None:
        s._file_binding(*file_journal)
    connection = s.open_database(
        args.database_path,
        args.manifest_sha256,
        args.instance_id,
        root if native else None,
        file_journal=file_journal,
    )
    journal_sync = None
    if native:
        journal_sync = s.partial(s.sync_journal, connection, root)
    elif file_journal is not None:
        journal_sync = s.partial(
            s.sync_file_journal, connection, *file_journal
        )
    saved_queries = (
        s.SavedQueryJournal(
            connection, root, args.journal_relative, native=native
        )
        if root is not None
        else None
    )
    return (connection, journal_sync, saved_queries)


def _serve(
    s, connection, socket, args, ttl, journal_sync, saved_queries, level
):
    s.os.umask(63)
    bound = False
    try:
        with s.unix_socket.socket(s.unix_socket.AF_UNIX) as listener:
            listener.bind(str(socket))
            bound = True
            listener.listen(128)
            app = s.create_app(
                connection,
                args.instance_id,
                args.manifest_sha256,
                args.project_root,
                ttl,
                journal_sync,
                saved_queries,
            )
            server = s.uvicorn.Server(
                s.uvicorn.Config(
                    app,
                    log_level=level.lower(),
                    access_log=False,
                    log_config=s.http_log_config(),
                )
            )
            server.run(sockets=[listener])
    finally:
        connection.close()
        if bound:
            socket.unlink(missing_ok=True)


def _workspace_route(s, store, instance_id, lock, history, saved_queries):

    async def workspace(request):
        if store is None:
            return s._error(
                "workspace_unavailable", "Project root is unavailable", 409
            )
        try:
            data = await s._read_object(
                request, 65536, {"instance_id", "operation", "arguments"}
            )
            if data["instance_id"] != instance_id:
                return s._error(
                    "foreign_instance", "Instance does not match", 403
                )
            if not isinstance(data["operation"], str) or not isinstance(
                data["arguments"], dict
            ):
                raise ValueError("Invalid Workspace request")
            with lock:
                operation, arguments = (data["operation"], data["arguments"])
                provider = s._workspace_provider(
                    operation, store, history, saved_queries
                )
                if operation in s.SAVED_QUERY_OPERATIONS and provider is None:
                    return s._error(
                        "workspace_unavailable",
                        "Saved query storage is unavailable",
                        409,
                    )
                result = provider.invoke(operation, arguments)
            return s.JSONResponse({"result": result})
        except s.ProjectGraphPending as error:
            return s._error("project_graph_pending", str(error), 409)
        except (ValueError, TypeError, UnicodeError, s.duckdb.Error) as error:
            return s._error("workspace_error", str(error), 400)
        except OSError:
            return s._error(
                "workspace_unavailable",
                "Workspace storage is unavailable",
                409,
            )

    return workspace


def _rebuild_route(
    s, connection, instance_id, lock, queries, workspaces, journal_sync
):

    async def rebuild(request):
        try:
            data = await s._read_object(
                request, 65536, {"instance_id", "target"}
            )
            if data["instance_id"] != instance_id:
                return s._error(
                    "foreign_instance", "Instance does not match", 403
                )
            with lock:
                if (
                    connection.execute(
                        "SELECT id FROM ops_generation"
                    ).fetchone()
                    is None
                ):
                    return s._error(
                        "generation_required",
                        "Generation admission required",
                        409,
                    )
                if journal_sync is not None:
                    journal_sync()
                replacements = queries.rebuild(connection, data["target"])
                if workspaces is not None:
                    workspaces.replace_results(replacements)
            ids = {
                key: value["query_id"] for key, value in replacements.items()
            }
            return s.JSONResponse({"result": {"result_ids": ids}})
        except s.ProjectGraphPending as error:
            return s._error("project_graph_pending", str(error), 409)
        except (ValueError, TypeError, s.duckdb.Error) as error:
            return s._error("invalid_query", str(error), 400)
        except OSError, RuntimeError:
            return s._error(
                "journal_unavailable", "Work Journal is unavailable", 409
            )

    return rebuild


def _schema_route(s, connection, instance_id, lock):

    async def schema(request):
        if list(request.query_params.multi_items()) != [
            ("instance_id", instance_id)
        ]:
            return s._error("foreign_instance", "Instance does not match", 403)
        with lock:
            if (
                connection.execute("SELECT id FROM ops_generation").fetchone()
                is None
            ):
                return s._error(
                    "generation_required", "Generation admission required", 409
                )
            return s.JSONResponse({"result": s.public_schema(connection)})

    return schema


def _artifact_route(s, connection, instance_id, lock):

    async def artifact(request):
        if list(request.query_params.multi_items()) != [
            ("instance_id", instance_id)
        ]:
            return s._error("foreign_instance", "Instance does not match", 403)
        if request.url.path == "/model" and s.managed(connection):
            with lock:
                state = s.managed(connection)
                generation = connection.execute(
                    "SELECT id FROM ops_generation"
                ).fetchone()
                if not generation or not state[1]:
                    return s._error("generation_required", state[2], 409)
                row = (generation[0], state[1])
        else:
            reader = (
                s.reviewed_native_model
                if request.url.path == "/model"
                else s.read_structure
            )
            row = reader(connection, lock)
        if row is None:
            return s._error(
                "generation_required", "Generation admission required", 409
            )
        return s.Response(
            row[1],
            media_type="application/json",
            headers={"x-anechoic-generation": row[0]},
        )

    return artifact


def _health_route(s, connection, instance_id, manifest_sha256, lock):

    async def health(request):
        with lock:
            row = connection.execute(
                "SELECT id FROM ops_generation"
            ).fetchone()
            pending = s.archive_pending(connection)
        return s.JSONResponse(
            {
                "result": {
                    "instance_id": instance_id,
                    "pid": s.os.getpid(),
                    "manifest_sha256": manifest_sha256,
                    "ready": row is not None,
                    "archive_pending": pending,
                    "generation": row[0] if row else None,
                }
            }
        )

    return health


def _routes_0(s, c):
    return [
        s.Route(
            "/health",
            s._health_route(
                c.connection, c.instance_id, c.manifest_sha256, c.lock
            ),
        ),
        s.Route(
            "/schema", s._schema_route(c.connection, c.instance_id, c.lock)
        ),
    ]


def _routes_1(s, c):
    return [
        s.Route(
            "/spec-snapshot",
            s.spec_snapshot_route(
                c.connection,
                c.instance_id,
                c.manifest_sha256,
                c.lock,
                s._read_object,
                s._error,
            ),
            methods=["GET", "PUT"],
        ),
        s.Route(
            "/ingestion/issues",
            s.ingestion_issues.route(
                c.connection, c.instance_id, c.lock, s._read_object, s._error
            ),
            methods=["GET", "PUT"],
        ),
    ]


def _routes_2(s, c):
    return [
        s.Route(
            "/flow/events",
            s.flow_route(
                c.connection, c.instance_id, c.lock, s._read_object, s._error
            ),
            methods=["POST"],
        ),
        s.Route(
            "/database",
            s.database_route(
                c.connection,
                c.instance_id,
                c.lock,
                c.queries,
                c.sync_sources,
                c.project_root,
                c.saved_queries,
                s._read_object,
                s._error,
            ),
            methods=["POST"],
        ),
    ]


def _routes_3(s, c):
    return [
        s.Route(
            "/workspace",
            s._workspace_route(
                c.workspaces, c.instance_id, c.lock, c.history, c.saved_queries
            ),
            methods=["POST"],
        ),
        s.Route(
            "/results/rebuild",
            s._rebuild_route(
                c.connection,
                c.instance_id,
                c.lock,
                c.queries,
                c.workspaces,
                c.sync_sources,
            ),
            methods=["POST"],
        ),
    ]


def _routes_4(s, c):
    return [
        s.Route(
            "/generation/reuse",
            s.reuse_route(
                c.connection, c.instance_id, c.lock, s._read_object, s._error
            ),
            methods=["GET", "PUT"],
        ),
        s.Route(
            "/generation/archive",
            s.archive_route(
                c.connection,
                c.instance_id,
                c.manifest_sha256,
                c.lock,
                s._read_object,
                s._error,
            ),
            methods=["PUT"],
        ),
    ]


def _routes_5(s, c):
    return [
        s.Route(
            "/generation/compiler",
            s.compiler_refresh_route(
                c.connection,
                c.instance_id,
                c.manifest_sha256,
                c.lock,
                s._read_object,
                s._error,
            ),
            methods=["PUT"],
        ),
        s.Route(
            "/generation/native",
            s.native_generation_route(
                c.connection,
                c.instance_id,
                c.manifest_sha256,
                c.lock,
                s._read_object,
                s._error,
            ),
            methods=["PUT"],
        ),
    ]


def _routes_6(s, c):
    return [
        s.Route(
            "/generation/native-delta",
            s.native_generation_route(
                c.connection,
                c.instance_id,
                c.manifest_sha256,
                c.lock,
                s._read_object,
                s._error,
            ),
            methods=["PUT"],
        ),
        s.Route(
            "/generation",
            s.generation_route(
                c.connection,
                c.instance_id,
                c.manifest_sha256,
                c.lock,
                c.queries,
                c.workspaces,
                c.sync_sources,
                s._read_object,
                s._error,
            ),
            methods=["PUT"],
        ),
    ]


def _routes_7(s, c):
    return [
        s.Route(
            "/model", s._artifact_route(c.connection, c.instance_id, c.lock)
        ),
        s.Route(
            "/structure",
            s._artifact_route(c.connection, c.instance_id, c.lock),
        ),
    ]


def routes(s, c):
    return (
        _routes_0(s, c)
        + _routes_1(s, c)
        + _routes_2(s, c)
        + _routes_3(s, c)
        + _routes_4(s, c)
        + _routes_5(s, c)
        + _routes_6(s, c)
        + _routes_7(s, c)
    )
