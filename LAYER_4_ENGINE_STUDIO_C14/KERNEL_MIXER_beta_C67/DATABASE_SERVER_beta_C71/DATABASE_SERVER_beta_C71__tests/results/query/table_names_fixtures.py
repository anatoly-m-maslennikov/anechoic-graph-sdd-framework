"""Fixtures for legacy table migration tests."""

import json

import duckdb

from ...DATABASE_SERVER_beta_C71__tests__shared import PIN


def _write_legacy_database(path):
    connection = duckdb.connect(str(path))
    try:
        connection.execute(
            "CREATE TABLE project_binding (manifest_sha256 VARCHAR NOT NULL, instance_id VARCHAR NOT NULL)"
        )
        connection.execute(
            "INSERT INTO project_binding VALUES (?, ?)", [PIN, "instance"]
        )
        connection.execute(
            'CREATE TABLE atoms (reference VARCHAR PRIMARY KEY, "content.summary" VARCHAR)'
        )
        connection.execute(
            "INSERT INTO atoms VALUES ('legacy-atom', 'retained')"
        )
        connection.execute(
            "CREATE TABLE generation (id VARCHAR, model VARCHAR, structure VARCHAR)"
        )
        connection.execute(
            "INSERT INTO generation VALUES ('legacy-generation', '{}', ?)",
            [
                json.dumps(
                    {
                        "components": {},
                        "project": {"ref": "AN-S-1", "sha256": PIN},
                    }
                )
            ],
        )
        connection.execute("CREATE TABLE generation_carriers (hashes VARCHAR)")
        connection.execute(
            "INSERT INTO generation_carriers VALUES (?)",
            [json.dumps({"a.py": "a" * 64})],
        )
        connection.execute("CREATE TABLE generation_reuse (witness VARCHAR)")
        connection.execute(
            "INSERT INTO generation_reuse VALUES (?)",
            [json.dumps({"legacy": True})],
        )
        _write_legacy_flow(connection)
    finally:
        connection.close()


def _write_legacy_flow(connection):
    connection.execute("""CREATE TABLE flow_events (
        run_id VARCHAR NOT NULL, component VARCHAR NOT NULL, action VARCHAR NOT NULL,
        sequence INTEGER NOT NULL, kind VARCHAR NOT NULL, name VARCHAR NOT NULL,
        "at" DOUBLE NOT NULL, causes INTEGER[] NOT NULL, target VARCHAR, outcome VARCHAR,
        detail JSON NOT NULL, PRIMARY KEY (run_id, sequence))""")
    connection.execute(
        "INSERT INTO flow_events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [
            "a" * 32,
            "C00",
            "legacy",
            0,
            "trigger",
            "start",
            1.0,
            [],
            None,
            None,
            "{}",
        ],
    )
