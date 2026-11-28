"""Source reader root-container cases."""

from . import test_source_reader as fixtures


class SourceReaderRootCases:
    @staticmethod
    def _relation_declarations():
        return [
            {
                "source_path": f"{reference}.md",
                "status_group": "Current",
                "id": reference,
                "ref": reference,
                "version": 1,
                "status": "Active",
                "role": "Requirement",
                "form": "Declaration",
                "tier": 1,
                "updated_at": None,
                "current_scope_unit": None,
                "claim_target_scope_unit": None,
                "header_json": {
                    "relations": {},
                    "subjects": {
                        "active": f"ANECHOIC_MODEL <+ CFEL <+ Relation//{name}"
                    },
                },
                "content_markdown": (
                    "## Claim\n\n### Formal Claim\n\n```python\n"
                    f'subject_path(address="Relation//{name}")\n{binding}\n'
                    "```\n"
                ),
                "content_properties_json": [],
                "relation_edges_json": [],
                "hash": None,
            }
            for reference, name, binding in (
                (
                    "CA-R-1",
                    "IS_CONTAINED_BY",
                    (
                        'relation(source="Relation//IS_CONTAINED_BY", '
                        'name="HAS_INVERSE", target="Relation//CONTAINS", '
                        "reverse=False)"
                    ),
                ),
                ("CA-R-2", "CONTAINS", ""),
            )
        ]

    def _assert_root_container_case(
        self,
        root,
        relative,
        original,
        audit,
        non_root,
        index,
        field,
        stored,
        target,
    ):
        with self.subTest(field=field, index=index):
            text = original.replace("\nrole:", f"\n{field}role:", 1)
            root.write_text(text, encoding="utf-8")
            atoms, scopes = self._capture_root_variant(
                root, relative, text, index
            )
            source = next(
                row for row in atoms if row["source_path"] == relative
            )
            self.assertEqual("container" in source["header_json"], bool(field))
            self.assertEqual(source["header_json"].get("container"), stored)
            self.assertEqual(
                any(
                    issue["field"] == "container"
                    for issue in audit.issues(source)
                ),
                target is None,
            )
            self.assertEqual(
                fixtures.expected_carrier(source, {}, {}.get, None),
                (None, self.control.name),
            )
            self.assertNotIn(
                "_project_root_header",
                next(row for row in atoms if row["source_path"] == non_root),
            )

            rows, scope_rows = self._assert_root_relations(
                atoms, scopes, relative, source, target
            )
            self.assertEqual(root.read_text(encoding="utf-8"), text)

        return atoms, rows, scope_rows

    def _capture_root_variant(self, root, relative, text, index):
        if index == 0:
            copy = root.parent / "z_copy" / root.name
            copy.parent.mkdir()
            copy.write_text(text, encoding="utf-8")
            atoms, scopes = self.reader.capture()
            copied = next(
                row
                for row in atoms
                if row["source_path"] == copy.relative_to(self.root).as_posix()
            )
            self.assertNotIn("_project_root_header", copied)
        else:
            atoms, scopes = self.reader.capture(
                [{"operation": "update", "new_path": relative}]
            )
        return atoms, scopes

    def _assert_root_relations(self, atoms, scopes, relative, source, target):
        relation_declarations = self._relation_declarations()
        rows, scope_rows = fixtures.materialize(
            relation_declarations + atoms, scopes
        )
        projected = next(row for row in rows if row["source_path"] == relative)
        direct = [
            edge["target_ref"]
            for edge in projected["relation_edges_json"]
            if edge["relation_type"] == "IS_CONTAINED_BY"
        ]
        self.assertEqual(direct, [] if target is None else [target])
        self.assertIs(projected["header_json"], source["header_json"])
        self.assertNotIn("_project_root_header", projected)
        self.assertEqual(len(scope_rows), 3)
        legacy_row = next(row for row in rows if row["ref"] == "CA-R-999")
        self.assertTrue(
            any(
                edge["target_ref"] == "MAIN"
                for edge in legacy_row["relation_edges_json"]
            )
        )
        return rows, scope_rows

    def test_root_container_default_changes_the_relation_and_preserves_stored_header(
        self,
    ) -> None:
        root = self.declarations["fixture"]["declaration_path"]
        relative = root.relative_to(self.root).as_posix()
        original = root.read_text(encoding="utf-8")
        original = original.replace(
            "\nrole:", "\ncurrent_scope_unit: MAIN\nrole:", 1
        )
        audit = fixtures.auditor(container_constraint=True)
        legacy = self._write_atom(
            "MAIN", "04_requirement", "legacy.md", atom_id="CA-R-999"
        )
        legacy.write_text(
            legacy.read_text().replace(
                "\nrole:", "\ncurrent_scope_unit: MAIN\nrole:", 1
            )
        )
        non_root = (
            self.declarations["MAIN"]["declaration_path"]
            .relative_to(self.root)
            .as_posix()
        )

        cases = self._root_container_cases()
        for index, (field, stored, target) in enumerate(cases):
            atoms, rows, scope_rows = self._assert_root_container_case(
                root,
                relative,
                original,
                audit,
                non_root,
                index,
                field,
                stored,
                target,
            )

        self._assert_projected_root(atoms, rows, scope_rows, root)
        self._assert_root_settings(root, relative, audit)

    def _assert_projected_root(self, atoms, rows, scope_rows, root):
        header = fixtures.infer_header_schema(atoms)
        public_rows, _ = fixtures.projected_rows(
            rows, scope_rows, header, self.reader.content_schema
        )
        public = next(
            row
            for row in public_rows
            if row["filename"] == root.name
            and row["relative_path"] == self.control.name
        )
        self.assertNotIn("header.container.scope_unit", public)
        self.assertEqual(
            public["header.relations"]["IS_CONTAINED_BY"],
            [
                {
                    "kind": "Scope Unit",
                    "reference": "CA-SU--1",
                    "derived": False,
                }
            ],
        )

    def _assert_root_settings(self, root, relative, audit):
        settings = self.control / "anechoic_project_settings.toml"
        settings_text = settings.read_text()
        for old, new in (
            ('name = "fixture"', 'name = "different"'),
            (
                'control_root = ".anechoic_anechoic"',
                'control_root = ".anechoic_other"',
            ),
        ):
            with self.subTest(settings=new):
                settings.write_text(settings_text.replace(old, new))
                atoms, _ = self.reader.capture()
                source = next(
                    row for row in atoms if row["source_path"] == relative
                )
                self.assertNotIn("_project_root_header", source)
                self.assertEqual(
                    fixtures.yaml.safe_load(
                        root.read_text().split("---", 2)[1]
                    ),
                    source["header_json"],
                )
                self.assertTrue(
                    any(
                        issue["field"] == "container"
                        for issue in audit.issues(source)
                    )
                )

    @staticmethod
    def _root_container_cases():
        return (
            ("", None, "CA-SU--1"),
            (
                "container: {scope_unit: CA-SU--1}\n",
                {"scope_unit": "CA-SU--1"},
                "CA-SU--1",
            ),
            (
                "container: {scope_unit: CA-SU-00}\n",
                {"scope_unit": "CA-SU-00"},
                "fixture",
            ),
            ("container: null\n", None, None),
            ("container: {scope_unit: ''}\n", {"scope_unit": ""}, None),
            (
                "container: {atom: CA-R-1, scope_unit: CA-SU-00}\n",
                {"atom": "CA-R-1", "scope_unit": "CA-SU-00"},
                None,
            ),
            ("", None, "CA-SU--1"),
        )
