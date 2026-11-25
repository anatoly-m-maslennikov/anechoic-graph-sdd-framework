"""Open a private database bound to one Project manifest."""

import json
import os
from pathlib import Path
import stat

from .query_engine import connect
from .project_structure import ensure_structure_table, replace_structure
from .model_projection import ensure_model_tables, replace_model_projection
from .table_names import main_objects, migrate_legacy_names, sync_query_views


def database_path(value):
    path = Path(value)
    if not path.is_absolute() or str(path) != value or path.name in ("", ".", ".."):
        raise ValueError("Database path must be absolute and canonical")
    parent = path.parent
    info = parent.stat()
    if (parent.resolve(strict=True) != parent or parent.is_symlink()
            or not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid()
            or stat.S_IMODE(info.st_mode) & 0o077):
        raise ValueError("Database directory is unavailable or unsafe")
    if path.exists() or path.is_symlink():
        info = path.lstat()
        if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid()
                or stat.S_IMODE(info.st_mode) & 0o077):
            raise ValueError("Database file is unavailable or unsafe")
    return path


def _migrate_structure(connection):
    columns = {row[1] for row in connection.execute("PRAGMA table_info('ops_generation')").fetchall()}
    if "structure" in columns:
        rows = connection.execute("SELECT structure FROM ops_generation").fetchall()
        if len(rows) > 1:
            raise ValueError("Invalid retained generation")
        facts = replace_structure(connection, rows[0][0]) if rows else None
        if main_objects(connection).get("generation") == "VIEW":
            connection.execute("DROP VIEW generation")
        connection.execute("ALTER TABLE ops_generation DROP COLUMN structure")
        connection.execute("ALTER TABLE ops_generation ADD COLUMN structure_facts VARCHAR")
        if rows:
            connection.execute("UPDATE ops_generation SET structure_facts = ?", [facts])
        return True
    return False


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
        legacy = "project_binding" in objects and "ops_project_binding" not in objects
        binding = "project_binding" if legacy else "ops_project_binding"
        if objects and objects.get(binding) != "BASE TABLE":
            raise ValueError("Database has no Project binding")
        if not objects:
            connection.execute("CREATE TABLE ops_project_binding (manifest_sha256 VARCHAR NOT NULL, instance_id VARCHAR NOT NULL)")
        rows = connection.execute(f"SELECT manifest_sha256, instance_id FROM main.{binding}").fetchall()
        if not rows and objects:
            raise ValueError("Database has an empty Project binding")
        if rows and rows != [(manifest_sha256, instance_id)]:
            raise ValueError("Database belongs to a different Project manifest")
        if not rows:
            connection.execute("INSERT INTO ops_project_binding VALUES (?, ?)", [manifest_sha256, instance_id])
        migrated = migrate_legacy_names(connection, objects, legacy=legacy)
        connection.execute('CREATE TABLE IF NOT EXISTS mrt_atoms (reference VARCHAR PRIMARY KEY, "content.summary" VARCHAR)')
        connection.execute("CREATE TABLE IF NOT EXISTS ops_generation (id VARCHAR, model VARCHAR, structure_facts VARCHAR)")
        ensure_structure_table(connection)
        model_tables_missing = "mrt_model_entities" not in main_objects(connection)
        ensure_model_tables(connection)
        migrated = _migrate_structure(connection) or migrated
        if model_tables_missing:
            row = connection.execute("SELECT model FROM ops_generation").fetchone()
            if row:
                descriptor = json.loads(row[0])
                if isinstance(descriptor.get("bindings"), dict):
                    replace_model_projection(connection, descriptor)
        if migrated:
            sync_query_views(connection)
        connection.execute("COMMIT")
    except BaseException:
        connection.close()
        raise
    return connection
