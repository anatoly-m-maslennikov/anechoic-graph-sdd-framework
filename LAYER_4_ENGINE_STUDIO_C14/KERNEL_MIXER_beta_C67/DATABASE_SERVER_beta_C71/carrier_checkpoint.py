"""Persist admitted carrier changes and fold them into the startup checkpoint."""

from collections import defaultdict
from hashlib import sha256
import json
from pathlib import PurePosixPath
import re

from starlette.responses import JSONResponse

from .realization_projection import has_table
from .table_names import main_objects


_LEGACY_CHECKPOINTS = {
    "ops_generation_carrier_hashes": "carrier_sha256_by_path",
    "ops_carrier_hashes": "carrier_sha256_by_path",
    "generation_carriers": "hashes",
}
_PENDING_FOLDER = (
    "coalesce(nullif(parse_dirpath(path, 'forward_slash'), ''), '.')"
)
_PENDING_DIGESTS = f"""SELECT path, {_PENDING_FOLDER} AS folder, digest
    FROM main.ops_generation_carrier_changes WHERE digest IS NOT NULL"""
_EFFECTIVE_DIGESTS = f"""SELECT d.path, d.folder, d.digest FROM main.ops_generation_carrier_digests d
    ANTI JOIN main.ops_generation_carrier_changes USING (path)
    UNION ALL {_PENDING_DIGESTS}"""


def initialize_checkpoint(connection, objects=None):
    """Create checkpoint tables and migrate legacy rows in the caller's transaction."""
    if objects is None:
        objects = main_objects(connection)
    connection.execute("""CREATE TABLE IF NOT EXISTS main.ops_generation_carrier_digests
        (path VARCHAR PRIMARY KEY, folder VARCHAR NOT NULL, digest VARCHAR NOT NULL)""")
    if "ops_generation_carrier_digests" not in objects:
        connection.execute(
            "CREATE INDEX ops_generation_carrier_digests_folder ON main.ops_generation_carrier_digests(folder)"
        )
    connection.execute("""CREATE TABLE IF NOT EXISTS main.ops_generation_carrier_checkpoint
        (complete BOOLEAN PRIMARY KEY CHECK (complete))""")
    connection.execute("""CREATE TABLE IF NOT EXISTS main.ops_generation_carrier_changes
        (path VARCHAR PRIMARY KEY, digest VARCHAR)""")
    connection.execute("""CREATE TABLE IF NOT EXISTS main.ops_generation_folder_hashes
        (folder VARCHAR PRIMARY KEY, digest VARCHAR NOT NULL)""")
    sources = [
        (name, column)
        for name, column in _LEGACY_CHECKPOINTS.items()
        if objects.get(name) == "BASE TABLE"
    ]
    if sources:
        hashes = _legacy_hashes(connection, *sources[0])
        if checkpoint_exists(connection) or any(
            _legacy_hashes(connection, *source) != hashes
            for source in sources[1:]
        ):
            raise ValueError("Conflicting retained carrier checkpoints")
        _replace_checkpoint(connection, hashes)
        for name, _ in sources:
            connection.execute(f"DROP TABLE main.{name}")
    if sources or not _LEGACY_CHECKPOINTS.keys() <= objects.keys():
        connection.execute(f"""CREATE OR REPLACE VIEW main.ops_generation_carrier_hashes AS
            SELECT coalesce(json_group_object(path, digest)::VARCHAR, '{{}}') AS carrier_sha256_by_path
            FROM ({_EFFECTIVE_DIGESTS})
            HAVING EXISTS (SELECT 1 FROM main.ops_generation_carrier_checkpoint)""")
        connection.execute("""CREATE OR REPLACE VIEW main.ops_carrier_hashes AS
            SELECT carrier_sha256_by_path FROM main.ops_generation_carrier_hashes""")
        connection.execute("""CREATE OR REPLACE VIEW main.generation_carriers AS
            SELECT carrier_sha256_by_path AS hashes FROM main.ops_generation_carrier_hashes""")


def _legacy_hashes(connection, table, column):
    rows = connection.execute(
        f"SELECT {column} FROM main.{table} LIMIT 2"
    ).fetchall()
    if not rows:
        return None
    if len(rows) != 1 or not isinstance(rows[0][0], str):
        raise ValueError("Invalid retained carrier checkpoint")
    hashes = json.loads(rows[0][0])
    if not _valid_hashes(hashes):
        raise ValueError("Invalid retained carrier checkpoint")
    return hashes


def _path(parent, filename):
    return str(PurePosixPath(parent) / filename)


def _valid_hashes(hashes):
    return isinstance(hashes, dict) and all(
        isinstance(value, str)
        and re.fullmatch(r"[0-9a-f]{64}", value) is not None
        for value in hashes.values()
    )


def _folder_hashes(rows):
    folders = defaultdict(list)
    for path, folder, digest in rows:
        folders[folder].append((PurePosixPath(path).name, digest))
    result = {}
    for folder, entries in folders.items():
        encoded = json.dumps(
            sorted(entries), ensure_ascii=False, separators=(",", ":")
        ).encode()
        result[folder] = sha256(encoded).hexdigest()
    return result


def _write_folder_hashes(connection, rows):
    folders = _folder_hashes(rows)
    if folders:
        connection.execute(
            """INSERT INTO main.ops_generation_folder_hashes
            SELECT unnest(?::VARCHAR[]), unnest(?::VARCHAR[])""",
            [list(folders), list(folders.values())],
        )


def _replace_checkpoint(connection, hashes):
    connection.execute("DELETE FROM main.ops_generation_carrier_digests")
    connection.execute("DELETE FROM main.ops_generation_folder_hashes")
    connection.execute("DELETE FROM main.ops_generation_carrier_checkpoint")
    connection.execute("DELETE FROM main.ops_generation_carrier_changes")
    if hashes is not None:
        rows = [
            (path, PurePosixPath(path).parent.as_posix(), digest)
            for path, digest in hashes.items()
        ]
        if rows:
            connection.execute(
                """INSERT INTO main.ops_generation_carrier_digests
                SELECT unnest(?::VARCHAR[]), unnest(?::VARCHAR[]), unnest(?::VARCHAR[])""",
                list(zip(*rows, strict=False)),
            )
        _write_folder_hashes(connection, rows)
        connection.execute(
            "INSERT INTO main.ops_generation_carrier_checkpoint VALUES (true)"
        )


def _record_changes(connection, paths, hashes):
    changes = {_path(parent, filename): None for parent, filename in paths}
    if not hashes.keys() <= changes.keys():
        raise ValueError("Invalid carrier hashes")
    changes.update(hashes)
    if changes:
        connection.execute(
            """INSERT INTO main.ops_generation_carrier_changes
            SELECT unnest(?::VARCHAR[]), unnest(?::VARCHAR[])
            ON CONFLICT (path) DO UPDATE SET digest = excluded.digest""",
            [list(changes), list(changes.values())],
        )


def update_checkpoint(connection, data, *, delta=False):
    hashes = data.get("carrier_hashes")
    if "carrier_hashes" in data:
        snapshot = data["snapshot"]
        if (
            not _valid_hashes(hashes)
            or not isinstance(snapshot, dict)
            or snapshot.get("schema_version") != 2
        ):
            raise ValueError("Invalid carrier hashes")
        expected = {
            _path(atom["relative_path"], atom["filename"])
            for atom in snapshot["atoms"]
        }
        rejected = {
            issue["relative_path"]
            for issue in snapshot.get("ingestion_issues", [])
        }
        if not expected <= hashes.keys() <= expected | rejected:
            raise ValueError("Invalid carrier hashes")
    if delta and hashes is not None:
        if checkpoint_exists(connection):
            _record_changes(connection, data["paths"], hashes)
    else:
        if not has_table(
            connection, "main", "ops_generation_carrier_checkpoint"
        ):
            initialize_checkpoint(connection)
        _replace_checkpoint(connection, hashes)


def checkpoint_exists(connection):
    return (
        has_table(connection, "main", "ops_generation_carrier_checkpoint")
        and connection.execute(
            "SELECT 1 FROM main.ops_generation_carrier_checkpoint LIMIT 1"
        ).fetchone()
        is not None
    )


def checkpoint_changes_pending(connection):
    return (
        has_table(connection, "main", "ops_generation_carrier_changes")
        and connection.execute(
            "SELECT 1 FROM main.ops_generation_carrier_changes LIMIT 1"
        ).fetchone()
        is not None
    )


def _scope_filter(scope, folder="folder"):
    condition = f"list_contains(list_slice(string_split({folder}, '/'), 2, -1), '09_archived')"
    return "TRUE" if scope is None else condition if scope == "archive" else f"NOT {condition}"


def read_checkpoint(connection, scope=None):
    if checkpoint_exists(connection):
        return dict(connection.execute(f"SELECT path, digest FROM ({_EFFECTIVE_DIGESTS}) WHERE {_scope_filter(scope)}").fetchall())
    return None


def archive_checkpoint_paths(connection):
    return {path for path, in connection.execute(f"""SELECT path FROM ({_EFFECTIVE_DIGESTS})
        WHERE list_contains(string_split(folder, '/'), '09_archived')""").fetchall()}


def _touched_folders(connection, scope=None):
    return [folder for folder, in connection.execute(
        f"SELECT DISTINCT {_PENDING_FOLDER} AS folder FROM main.ops_generation_carrier_changes "
        f"WHERE {_scope_filter(scope, _PENDING_FOLDER)}"
    ).fetchall()]


def fold_checkpoint(connection):
    """Fold pending paths and their folder digests in the caller's transaction."""
    touched = _touched_folders(connection)
    if not touched:
        return
    connection.execute("""DELETE FROM main.ops_generation_carrier_digests
        WHERE path IN (SELECT path FROM main.ops_generation_carrier_changes)""")
    connection.execute(f"INSERT INTO main.ops_generation_carrier_digests {_PENDING_DIGESTS}")
    connection.execute("""DELETE FROM main.ops_generation_folder_hashes
        WHERE folder IN (SELECT unnest(?::VARCHAR[]))""", [touched])
    _write_folder_hashes(connection, connection.execute("""SELECT path, folder, digest
        FROM main.ops_generation_carrier_digests WHERE folder IN (SELECT unnest(?::VARCHAR[]))""", [touched]).fetchall())
    connection.execute("DELETE FROM main.ops_generation_carrier_changes")


def _read_folders(connection, witness, hashes, scope=None):
    required = (
        ("main", "ops_generation_folder_hashes"),
        ("main", "mrt_atoms"),
        ("main", "mrt_atom_references"),
        ("main", "mrt_atom_graph_relations"),
        ("native_graph", "int_labels"),
    )
    if (
        hashes is None
        or "carrier_schema" not in witness["inputs"]
        or not all(
            has_table(connection, schema, name) for schema, name in required
        )
    ):
        return None
    folders = dict(
        connection.execute(
            f"SELECT folder, digest FROM ops_generation_folder_hashes WHERE {_scope_filter(scope)}"
        ).fetchall()
    )
    touched = _touched_folders(connection, scope)
    if touched:
        for folder in touched:
            folders.pop(folder, None)
        rows = connection.execute(
            f"""SELECT path, folder, digest FROM ({_EFFECTIVE_DIGESTS})
            WHERE folder IN (SELECT unnest(?::VARCHAR[]))""",
            [touched],
        ).fetchall()
        folders.update(_folder_hashes(rows))
    return folders


def _reuse_result(connection, scope=None):
    from .archive_generation import archive_pending
    from .accepted_model import generation_rows
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import status_domains as _status_domains

    if not has_table(connection, "main", "ops_generation_reuse"):
        return None
    row = connection.execute("SELECT g.id, r.witness FROM ops_generation g CROSS JOIN ops_generation_reuse r").fetchone()
    if row is None:
        return None
    witness = json.loads(row[1])
    generation = generation_rows(connection)
    if len(generation) != 1 or generation[0][0] != row[0]:
        raise ValueError("Reuse generation has no matching admitted Model")
    domains = _status_domains(json.loads(generation[0][1])["bindings"])
    result = {"base_generation": row[0], **witness,
              "status_domains": {key: sorted(values) for key, values in domains.items()}}
    hashes = read_checkpoint(connection, scope)
    if hashes is not None:
        warning_paths = connection.execute("""SELECT DISTINCT relative_path FROM main.ops_ingestion_issues
            WHERE source IN ('atom', 'archive') AND relative_path IS NOT NULL
            AND """ + _scope_filter(scope, "coalesce(nullif(parse_dirpath(relative_path, 'forward_slash'), ''), '.')")).fetchall()
        if any(path not in hashes for path, in warning_paths):
            hashes = None
    if hashes is not None:
        result["carrier_hashes"] = hashes
    folders = _read_folders(connection, witness, hashes, scope)
    if folders is not None:
        result["folder_hashes"] = folders
    if scope is not None:
        result["checkpoint_scope"] = scope
    if archive_pending(connection):
        result["archive_pending"] = True
    return result


def reuse_route(connection, instance_id, lock, read_object, error_response):
    from .archive_generation import change_archive_pending
    from .generation import GenerationBaseChanged

    async def reuse(request):
        if request.method == "PUT":
            try:
                data = await read_object(
                    request,
                    4096,
                    {"instance_id", "base_generation", "archive_pending"},
                )
                if data["instance_id"] != instance_id:
                    return error_response("foreign_instance", "Instance does not match", 403)
                if data["archive_pending"] is not True:
                    raise ValueError("Invalid startup archive transition")
                with lock:
                    generation = change_archive_pending(connection, data["base_generation"], True)
                return JSONResponse({"result": {"generation": generation}})
            except GenerationBaseChanged as error:
                return error_response("generation_base_changed", str(error), 409)
            except (ValueError, TypeError) as error:
                return error_response("invalid_generation", str(error), 400)
        query = list(request.query_params.multi_items())
        if query not in ([("instance_id", instance_id)], [("instance_id", instance_id), ("scope", "foreground")],
                          [("instance_id", instance_id), ("scope", "archive")]):
            return error_response("foreign_instance", "Instance does not match", 403)
        with lock:
            return JSONResponse({"result": _reuse_result(connection, query[1][1] if len(query) == 2 else None)})

    return reuse
