"""Fixtures for native graph relation tests."""


class GraphRelationsCases:
    @staticmethod
    def atom(ref: str, edges: list[dict], *, version: int = 1) -> dict:
        return {
            "source_path": f"{ref}.md",
            "status_group": "Current",
            "id": ref,
            "ref": ref,
            "version": version,
            "status": "Active",
            "current_scope_unit": None,
            "claim_target_scope_unit": None,
            "role": "Requirement",
            "form": "Declaration",
            "tier": 1,
            "updated_at": None,
            "header_json": {},
            "content_markdown": "",
            "content_properties_json": [],
            "relation_edges_json": edges,
            "hash": ref,
        }

    @staticmethod
    def scope(name: str, edges: list[dict]) -> dict:
        return {
            "name": name,
            "scope_unit_id": None,
            "parent_name": None,
            "declared_label": None,
            "ordered": False,
            "order_number": None,
            "declaration_source_path": f"{name}.md",
            "declaration_version": 1,
            "relation_edges_json": edges,
            "hash": name,
        }

    @staticmethod
    def edge(
        source_kind: str,
        source_ref: str,
        target_kind: str,
        target_ref: str,
        relation_type: str,
        derived: bool = False,
    ) -> dict:
        return {
            "source_kind": source_kind,
            "source_ref": source_ref,
            "target_kind": target_kind,
            "target_ref": target_ref,
            "relation_type": relation_type,
            "derived": derived,
        }

    def _assert_flat_type_change(self, connection, query):
        changed_type = [
            self.atom(
                "A",
                [self.edge("Atom", "A", "Atom", "D", "CONTAINS")],
                version=3,
            )
        ]
        self.assertTrue(
            self.store.apply(changed_type, [], relation_types={"CONTAINS"})
        )
        self.assertEqual(
            [("Atom", "A", "Atom", "D", "CONTAINS", False)],
            connection.execute(query).fetchall(),
        )
        self.store.replace([], [], relation_types=set())
        self.assertEqual([], connection.execute(query).fetchall())
