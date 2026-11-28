"Verify the shared projection across Project connections and source upgrades."

import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import duckdb

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.settings.project.framework_database__pub import (
    attach_framework,
)


DELIVERED_LAYERS = ("LAYER_1_META_ONTOLOGY_C9", "LAYER_2_META_METHODOLOGY_C58")


class FrameworkDatabaseTests(unittest.TestCase):
    def setUp(self):
        folder = self.enterContext(tempfile.TemporaryDirectory())
        self.root = Path(folder).resolve()
        self.volume = self.root / "volume"
        self.volume.mkdir()
        self.enterContext(
            patch.dict(
                os.environ, {"ANECHOIC_FRAMEWORK_DB_ROOT": str(self.volume)}
            )
        )
        for number, layer in enumerate(DELIVERED_LAYERS, 1):
            (self.root / layer).mkdir()
            self.write_atom(number, 1)

    def write_atom(self, number, version, status="active"):
        path = (
            self.root
            / DELIVERED_LAYERS[number - 1]
            / f"AN-S-{number}-SPEC--atom.md"
        )
        path.write_text(
            f"---\natom_family: SPEC\natom_id: AN-S-{number}\n"
            "container: {component: C00}\ntier: 2\ncontext: {lens: SPEC}\n"
            f"state: {{status: {status}, version: {version}}}\n---\n"
            f"\n## Summary\n\nAtom {number}\n",
            encoding="utf-8",
        )

    def project(self, name):
        connection = self.enterContext(
            duckdb.connect(str(self.root / f"{name}.duckdb"))
        )
        attach_framework(connection, source=self.root)
        connection.execute("SET enable_external_access = false")
        connection.execute(
            "CREATE TABLE local_project AS SELECT ?::VARCHAR AS name", [name]
        )
        return connection

    def test_reuse_for_two_projects_and_refresh_when_delivery_changes(self):
        first = self.project("first")
        database = self.volume / "framework.duckdb"
        old = database.stat()
        second = self.project("second")
        self.assertEqual(database.stat(), old)
        for connection, name in ((first, "first"), (second, "second")):
            self.assertEqual(
                connection.execute(
                    "SELECT name FROM local_project"
                ).fetchall(),
                [(name,)],
            )
            self.assertEqual(
                connection.execute(
                    (
                        "SELECT atom_id, version FROM framework.atoms ORDER "
                        "BY atom_id"
                    )
                ).fetchall(),
                [("AN-S-1", 1), ("AN-S-2", 1)],
            )
        with self.assertRaises(duckdb.InvalidInputException):
            first.execute("DELETE FROM framework.atoms")
        self.write_atom(2, 2)
        third = self.project("third")
        self.assertEqual(
            third.execute(
                "SELECT max(version) FROM framework.atoms"
            ).fetchone(),
            (2,),
        )
        self.assertEqual(
            first.execute(
                "SELECT max(version) FROM framework.atoms"
            ).fetchone(),
            (1,),
        )

    def test_invalid_delivery_preserves_last_published_database(self):
        self.project("first")
        database = self.volume / "framework.duckdb"
        old = database.read_bytes()
        self.write_atom(2, 2, "archived")
        with self.assertRaisesRegex(
            ValueError, "expected a delivered Active SPEC Atom"
        ):
            self.project("second")
        self.assertEqual(database.read_bytes(), old)
