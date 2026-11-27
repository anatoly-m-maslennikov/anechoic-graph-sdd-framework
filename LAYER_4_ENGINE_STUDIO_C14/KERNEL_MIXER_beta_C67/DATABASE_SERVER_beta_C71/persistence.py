"""Open a private database bound to one Project manifest."""

import json
import os
from pathlib import Path
import stat

from .carrier_checkpoint import fold_checkpoint, initialize_checkpoint
from .query_engine import connect
from .project_structure import ensure_structure_table, replace_structure
from .model_projection import ensure_model_tables, replace_model_projection
from .table_names import main_objects, migrate_legacy_names, sync_query_views


def database_path(value):
    path = Path(value)
    if (
        not path.is_absolute()
        or str(path) != value
        or path.name in ("", ".", "..")
    ):
        raise ValueError("Database path must be absolute and canonical")
    parent = path.parent
    info = parent.stat()
    if (
        parent.resolve(strict=True) != parent
        or parent.is_symlink()
        or not stat.S_ISDIR(info.st_mode)
        or info.st_uid != os.getuid()
        or stat.S_IMODE(info.st_mode) & 0o077
    ):
        raise ValueError("Database directory is unavailable or unsafe")
    if path.exists() or path.is_symlink():
        info = path.lstat()
        if (
            not stat.S_ISREG(info.st_mode)
            or info.st_uid != os.getuid()
            or stat.S_IMODE(info.st_mode) & 0o077
        ):
            raise ValueError("Database file is unavailable or unsafe")
    return path


def _restore_artifact_projections(connection):
    objects = main_objects(connection)
    structure_missing = "mrt_project_structure" not in objects
    model_missing = (
        not {
            "mrt_model_entities",
            "mrt_model_properties",
            "mrt_model_tree",
            "mrt_model_primary_entities",
        }
        <= objects.keys()
    )
    if not model_missing:
        columns = {row[1] for row in connection.execute(
            "PRAGMA table_info('mrt_model_primary_entities')").fetchall()}
        model_missing = not {"axes", "node_rules"} <= columns
        tree_columns = {row[1] for row in connection.execute(
            "PRAGMA table_info('mrt_model_tree')").fetchall()}
        model_missing = model_missing or "reference_path" not in tree_columns
    ensure_structure_table(connection)
    ensure_model_tables(connection)
    if not (structure_missing or model_missing):
        return False
    row = connection.execute(
        "SELECT model, structure FROM ops_generation"
    ).fetchone()
    if row:
        if structure_missing:
            replace_structure(connection, row[1])
        if model_missing and isinstance(row[0], str):
            if row[0].startswith("{"):
                descriptor = json.loads(row[0])
                if isinstance(descriptor.get("bindings"), dict):
                    replace_model_projection(connection, descriptor)
            else:
                connection.execute(
                    "CREATE TEMP TABLE model_projection_restore_needed (marker BOOLEAN)"
                )
    return True


def open_bound_database(value, manifest_sha256, instance_id):
    path = database_path(value)
    previous_umask = os.umask(0o077)
    try:
        connection = connect(str(path))
    finally:
        os.umask(previous_umask)
    try:
        connection.execute("BEGIN TRANSACTION")
        objects = main_objects(connection)
        legacy = (
            "project_binding" in objects
            and "ops_project_binding" not in objects
        )
        binding = "project_binding" if legacy else "ops_project_binding"
        if objects and objects.get(binding) != "BASE TABLE":
            raise ValueError("Database has no Project binding")
        if not objects:
            connection.execute(
                "CREATE TABLE ops_project_binding (manifest_sha256 VARCHAR NOT NULL, instance_id VARCHAR NOT NULL)"
            )
        rows = connection.execute(
            f"SELECT manifest_sha256, instance_id FROM main.{binding}"
        ).fetchall()
        if not rows and objects:
            raise ValueError("Database has an empty Project binding")
        if rows and rows != [(manifest_sha256, instance_id)]:
            raise ValueError("Database belongs to a different Project manifest")
        if not rows:
            connection.execute(
                "INSERT INTO ops_project_binding VALUES (?, ?)",
                [manifest_sha256, instance_id],
            )
        migrated = migrate_legacy_names(connection, objects, legacy=legacy)
        initialize_checkpoint(connection, objects)
        fold_checkpoint(connection)
        connection.execute('CREATE TABLE IF NOT EXISTS mrt_atoms (reference VARCHAR PRIMARY KEY, "content.summary" VARCHAR)')
        connection.execute("CREATE TABLE IF NOT EXISTS ops_generation (id VARCHAR, model VARCHAR, structure VARCHAR)")
        if _restore_artifact_projections(connection) or migrated:
            sync_query_views(connection)
        connection.execute("COMMIT")
    except BaseException:
        connection.close()
        raise
    return connection
