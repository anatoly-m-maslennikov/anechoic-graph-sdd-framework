"""Open a private database bound to one Project manifest."""

import os
from pathlib import Path
import stat

from .query_engine import connect


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


def open_bound_database(value, manifest_sha256, instance_id):
    path = database_path(value)
    previous_umask = os.umask(0o077)
    try:
        connection = connect(str(path))
    finally:
        os.umask(previous_umask)
    try:
        connection.execute("BEGIN TRANSACTION")
        tables = connection.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'main'").fetchall()
        if tables and ("project_binding",) not in tables:
            raise ValueError("Database has no Project binding")
        connection.execute("CREATE TABLE IF NOT EXISTS project_binding (manifest_sha256 VARCHAR NOT NULL, instance_id VARCHAR NOT NULL)")
        rows = connection.execute("SELECT manifest_sha256, instance_id FROM project_binding").fetchall()
        if not rows and tables:
            raise ValueError("Database has an empty Project binding")
        if not rows:
            connection.execute("INSERT INTO project_binding VALUES (?, ?)", [manifest_sha256, instance_id])
        elif rows != [(manifest_sha256, instance_id)]:
            raise ValueError("Database belongs to a different Project manifest")
        connection.execute('CREATE TABLE IF NOT EXISTS atoms (reference VARCHAR PRIMARY KEY, "content.summary" VARCHAR)')
        connection.execute("CREATE TABLE IF NOT EXISTS generation (id VARCHAR, model VARCHAR, structure VARCHAR)")
        connection.execute("COMMIT")
    except BaseException:
        connection.close()
        raise
    return connection
