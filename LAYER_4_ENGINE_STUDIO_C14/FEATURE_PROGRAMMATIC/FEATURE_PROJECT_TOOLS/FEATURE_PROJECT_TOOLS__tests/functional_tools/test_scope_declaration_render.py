from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.\
    FEATURE_PROJECT_TOOLS__tests.scope_declaration_render__pub \
    import render_scope_declaration  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.\
    FEATURE_PROJECT_TOOLS__tests.scope_declaration_test_support__pub \
    import write_scope_unit_declarations  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.structure.scope.units.units__shared \
    import read_scope_unit_declarations  # fmt: skip


class ScopeDeclarationRenderTest(unittest.TestCase):
    def test_renderer_namespaces_metadata_but_keeps_claims_local(self) -> None:
        rendered = render_scope_declaration(
            name="CHILD",
            project_name="anechoic",
            atom_id="CA-R-1",
            updated_at="now",
            scope_id="SU-1",
            parent="PROJECT",
        )

        self.assertIn(
            'active: "ANECHOIC_STRUCTURE <+ Scope Unit//CHILD"', rendered
        )
        self.assertIn("passive: []", rendered)
        self.assertNotIn("ANECHOIC", rendered.split("## Claim", 1)[1])

    def test_renderer_keeps_other_projects_on_bare_metadata_subjects(
        self,
    ) -> None:
        rendered = render_scope_declaration(
            name="CHILD",
            project_name="demo",
            atom_id="CA-R-1",
            updated_at="now",
            scope_id="SU-1",
            parent="PROJECT",
        )

        self.assertIn('active: "Scope Unit//CHILD"', rendered)
        self.assertNotIn("ANECHOIC", rendered)

    def test_renderer_uses_only_the_conditional_order_number(self) -> None:
        rendered = render_scope_declaration(
            name='CHILD"X',
            project_name="demo",
            atom_id="CA-R-1",
            updated_at="now",
            scope_id="SU-1",
            label="FEATURE",
            ordered=True,
            order_number=True,
            parent="PROJECT",
        )
        self.assertIn('id="SU-1"', rendered)
        self.assertIn("ordered=True", rendered)
        self.assertNotIn("order_number", rendered)
        self.assertIn('container="demo"', rendered)

    def test_materializer_places_root_and_child_at_parent_authority(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            control = root / ".anechoic_anechoic"
            control.mkdir()
            (control / "anechoic_project_settings.toml").write_text(
                '[project]\nname = "demo"\n', encoding="utf-8"
            )
            rows = write_scope_unit_declarations(
                root,
                (
                    {
                        "scope_unit_name": "CHILD",
                        "parent": "PROJECT",
                        "scope_unit_type": "Ordered",
                        "scope_unit_label": "FEATURE",
                        "local_order": 2,
                    },
                ),
            )
            self.assertTrue(rows["demo"]["declaration_path"].is_file())
            self.assertTrue(rows["CHILD"]["declaration_path"].is_file())
            self.assertEqual(rows["demo"]["declaration_path"].parent, control)
            self.assertEqual(
                rows["CHILD"]["declaration_path"].parent,
                control / "04_requirement",
            )
            self.assertIn(
                "TEST-SU-1_FEATURE_2_CHILD",
                str(rows["CHILD"]["authority_path"]),
            )
            self.assertNotIn("TEST-SU-1", str(rows["CHILD"]["delivery_path"]))
            self.assertEqual(
                set(read_scope_unit_declarations(root, control.name).by_name),
                {"demo", "CHILD"},
            )


if __name__ == "__main__":
    unittest.main()
