"""Filename-only Archive allocation metadata for the Workbench database."""

from __future__ import annotations

ARCHIVE_VERSION_MAX = "archive_version_max"
ARCHIVE_ROLE_MAX = "archive_role_max"


class ArchiveCatalog:
    def __init__(self, connection, lock, root):
        self.connection = connection
        self.lock = lock
        self.root = root
        self.batch = None
        self.dirty = True
        with lock:
            connection.execute(
                (
                    "CREATE TEMP TABLE workbench_filename_catalog (path "
                    "VARCHAR PRIMARY KEY, atom_id VARCHAR, role_marker "
                    "VARCHAR, id_number VARCHAR, version VARCHAR, archived "
                    "BOOLEAN)"
                )
            )
            connection.execute("DROP TABLE IF EXISTS main.archive_version_max")
            connection.execute(
                (
                    "CREATE TABLE main.archive_version_max (atom_id VARCHAR, "
                    "max_version VARCHAR)"
                )
            )
            connection.execute("DROP TABLE IF EXISTS main.archive_role_max")
            connection.execute(
                (
                    "CREATE TABLE main.archive_role_max (role_marker VARCHAR, "
                    "max_id_number VARCHAR)"
                )
            )

    def begin(self):
        self.batch = {}
        self.dirty = True

    def finish(self):
        with self.lock:
            self.connection.execute(
                "DELETE FROM temp.main.workbench_filename_catalog"
            )
            if self.batch:
                columns = list(zip(*self.batch.values(), strict=False))
                self.connection.execute(
                    (
                        "INSERT INTO temp.main.workbench_filename_catalog "
                        "SELECT unnest(?::VARCHAR[]), unnest(?::VARCHAR[]), "
                        "unnest(?::VARCHAR[]), unnest(?::VARCHAR[]), "
                        "unnest(?::VARCHAR[]), unnest(?::BOOLEAN[])"
                    ),
                    [list(column) for column in columns],
                )
        self.batch = None

    def remember(self, path, identity, version, archived):
        relative = path.relative_to(self.root).as_posix()
        row = (relative, *identity, version, archived)
        self.dirty |= archived
        if self.batch is not None:
            self.batch[relative] = row
        else:
            with self.lock:
                self.connection.execute(
                    (
                        "INSERT OR REPLACE INTO temp.main.workbench_filename_c"
                        "atalog VALUES (?, ?, ?, ?, ?, ?)"
                    ),
                    row,
                )

    def remove(self, path):
        relative = path.relative_to(self.root).as_posix()
        with self.lock:
            removed = self.connection.execute(
                (
                    "DELETE FROM temp.main.workbench_filename_catalog WHERE "
                    "path = ? OR starts_with(path, ?) RETURNING archived"
                ),
                [relative, relative.rstrip("/") + "/"],
            ).fetchall()
            self.dirty |= any(row[0] for row in removed)

    def paths(self, *, atom_id=None, archived=None, under=None):
        conditions, parameters = [], []
        if atom_id is not None:
            conditions.append("atom_id = ?")
            parameters.append(atom_id)
        if archived is not None:
            conditions.append("archived = ?")
            parameters.append(archived)
        if under is not None:
            relative = under.relative_to(self.root).as_posix()
            conditions.append("(path = ? OR starts_with(path, ?))")
            parameters.extend((relative, relative.rstrip("/") + "/"))
        with self.lock:
            rows = self.connection.execute(
                "SELECT path FROM temp.main.workbench_filename_catalog"
                + (" WHERE " + " AND ".join(conditions) if conditions else ""),
                parameters,
            ).fetchall()
        return {self.root / row[0] for row in rows}

    def max_number(self, role, ceiling):
        if ceiling is not None and ceiling < 0:
            return 0
        parameters = [role]
        limit = ""
        if ceiling is not None:
            digits = str(ceiling)
            limit = " AND (length(id_number), id_number) <= (?, ?)"
            parameters.extend((len(digits), digits))
        with self.lock:
            row = self.connection.execute(
                (
                    "SELECT id_number FROM temp.main.workbench_filename_catalo"
                    "g WHERE role_marker = ?"
                )
                + limit
                + " ORDER BY length(id_number) DESC, id_number DESC LIMIT 1",
                parameters,
            ).fetchone()
        return int(row[0]) if row else 0

    def refresh_summaries(self):
        if not self.dirty:
            return
        with self.lock:
            self.connection.execute("DELETE FROM main.archive_role_max")
            self.connection.execute(
                (
                    "INSERT INTO main.archive_role_max SELECT role_marker, "
                    "arg_max(id_number, (length(id_number), id_number)) FROM "
                    "temp.main.workbench_filename_catalog WHERE archived "
                    "GROUP BY role_marker"
                )
            )
            self.connection.execute("DELETE FROM main.archive_version_max")
            self.connection.execute(
                "INSERT INTO main.archive_version_max "
                "SELECT atom_id, arg_max(version, (length(version), version)) "
                "FROM temp.main.workbench_filename_catalog WHERE archived "
                "AND version IS NOT NULL GROUP BY atom_id"
            )
            self.dirty = False
