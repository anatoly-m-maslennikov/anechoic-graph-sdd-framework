from pathlib import Path
import sys
import unittest

sys.path.insert(0, str((ENGINE := (TOOLS := Path(__file__).resolve()
    .parents[1]).parents[1]) / 'IWE_CONSOLE_C43'))
sys.path.insert(0, str(TOOLS))
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import capture_native
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import (
    InputError, SourceChanged, change_spec_status, promote_draft,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests import (
    test_native_lifecycle_draft as fixtures,
)

SOURCE_0 = "---\natom_family: SPEC\natom_id: AN-S-3196\ncontainer:\n  component: C9\ntier: 2\ncontext:\n  lens: SPEC\nstate:\n  status: active\n  version: 1\n  updated_at: '2026-11-21T18:17:21+00:00'\n---\n\n## Summary\n\nDeclare Applicable Principle\n\n## Claim scope\n\nMODEL//ANECHOIC <+ Node//Artifact//Atom//Spec Atom//Applicable Principle\n\n## Claim\n\n### Prose Claim\n\nThe Applicable Principle Template guides Project decisions when its\napplicability conditions hold.\n\n### Formal Claim\n\n```python\nfrom anechoic.formal_claims import declare_entity\nfrom anechoic.model import SpecAtom\n\nclass ApplicablePrinciple(SpecAtom):\n    pass\n\ndeclare_entity(\n    entity_name='Applicable Principle',\n    entity_class=ApplicablePrinciple,\n    entity_kind='Primary',\n)\n```\n"
SOURCE_1 = "---\natom_family: SPEC\natom_id: AN-S-3302\ncontainer:\n  component: C9\ntier: 2\ncontext:\n  lens: SPEC\nstate:\n  status: active\n  version: 1\n  updated_at: '2026-11-22T00:43:18.850641+00:00'\n---\n\n## Summary\n\nSet the Applicable Principle encapsulation\n\n## Claim scope\n\nMODEL//ANECHOIC <+ Node//Artifact//Atom//Spec Atom//Applicable Principle.Encapsulation\n\n## Claim\n\n### Formal Claim\n\n```python\nfrom anechoic.formal_claims import declare_entity\n\ndeclare_entity(\n    entity_name='Encapsulation',\n    entity_kind='Property',\n    relation_name='IS_PROPERTY_OF',\n    base_path='Node//Artifact//Atom',\n    value_format=str,\n    allowed_values=('white_box', 'black_box'),\n    field_options={'class_var': True, 'default': 'black_box'},\n    applies_to_entity_classes=('Node//Artifact//Atom//Spec Atom//Applicable Principle',),\n)\n```\n"
SOURCE_2 = "---\natom_family: SPEC\natom_id: AN-S-3196\ncontainer:\n  component: C9\ntier: 2\ncontext:\n  lens: SPEC\n  template: manifest_node\nrelations:\n  IS_REPLACEMENT_FOR:\n  - AN-S-3302\nstate:\n  status: draft\n  version: 3\n  updated_at: '2026-11-24T16:58:01.502301+00:00'\n---\n\n## Summary\n\nDeclare Applicable Principle\n\n## Claim scope\n\nMODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification//Applicable Principle\n\n## Claim\n\n### Prose Claim\n\nThe Applicable Principle Template guides Project decisions when its\napplicability conditions hold.\n\n## Formal Manifest\n\n```python anechoic-edsl\n# Anechoic Python eDSL\n\nfrom anechoic.model import SpecAtom\n\nclass ApplicablePrinciple(SpecAtom):\n    pass\n```\n"

class ReplacementPromotionTests(fixtures.NativeRevisionCarrierTests, unittest.TestCase):
    def setUp(self):
        super().setUp()
        root = self.control / "UNIT_C9"
        self.paths = [
            root / "_SPEC/AN-S-3196-SPEC--declare-applicable-principle.md",
            root
            / "_SPEC/AN-S-3302-SPEC--set-the-applicable-principle-encapsulation.md",
            root
            / "01_draft/AN-S-3196@3-draft-SPEC-MANIFEST_NODE--declare-applicable-principle.md",
        ]
        for path, text in zip(
            self.paths, (SOURCE_0, SOURCE_1, SOURCE_2), strict=False
        ):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
        self.params = {'target': {'ref_id': 'AN-S-3196@3-draft', 'version': 3}, 'targetStatus': 'ready'}

    def promote(self):
        return promote_draft(
            self.selection,
            self.params,
            current_rows=capture_native(self.selection).atoms,
        )

    def test_actual_c9_revision_archives_both_predecessors(self):
        result = self.promote()
        self.assertEqual('completed', result['outcome'], result)
        self.assertTrue((self.control / 'UNIT_C9/02_ready/AN-S-3196-SPEC-MANIFEST_NODE--declare-applicable-principle.md').exists())
        self.assertFalse(any(path.exists() for path in self.paths))
        archives = list((self.control / 'UNIT_C9/09_archived').glob('*.md'))
        self.assertEqual(2, len(archives))
        self.assertIn(
            "2026-11-21T18:17:21+00:00",
            next(p for p in archives if "3196@" in p.name).read_text(),
        )

    def test_new_link_cannot_target_archive_only_predecessor(self):
        self.archive_predecessor()
        with self.assertRaisesRegex(InputError, 'Current Ready or Active'):
            self.promote()
        self.assertTrue(self.paths[0].exists())
        self.assertTrue(self.paths[2].exists())

    def archive_predecessor(self):
        archived = self.control / 'UNIT_C9/09_archived/AN-S-3302@1-SPEC--set-the-applicable-principle-encapsulation.md'
        archived.parent.mkdir(parents=True)
        archived.write_text(self.paths[1].read_text().replace('status: active', 'status: archived'))
        self.paths[1].unlink()
        return archived

    def test_revision_retains_adopted_link_to_archived_predecessor(self):
        relation = 'relations:\n  IS_REPLACEMENT_FOR:\n  - AN-S-3302\n'
        self.paths[0].write_text(SOURCE_0.replace('state:', relation + 'state:'))
        archived = self.archive_predecessor()
        before = archived.read_bytes()
        self.paths[2].write_text(SOURCE_2.replace(relation, ''))
        with self.assertRaisesRegex(InputError, 'retain its adopted replacement links'):
            self.promote()
        self.paths[2].write_text(SOURCE_2)
        result = self.promote()
        self.assertEqual('completed', result['outcome'], result)
        self.assertEqual(before, archived.read_bytes())
        self.assertEqual(2, len(list(archived.parent.glob('*.md'))))
        self.assertIn(relation, (self.selection.root / result['artifact']['path']).read_text())

    def test_missing_target_and_occupied_archive_have_no_effects(self):
        for case in ('missing', 'collision'):
            original = self.paths[1].read_bytes()
            if case == 'missing':
                self.paths[1].unlink()
            else:
                archive = self.control / 'UNIT_C9/09_archived/AN-S-3302@1-SPEC--set-the-applicable-principle-encapsulation.md'
                archive.parent.mkdir(parents=True, exist_ok=True)
                archive.write_text('occupied')
            with self.assertRaises((InputError, SourceChanged)):
                self.promote()
            self.assertTrue(self.paths[0].exists())
            self.assertTrue(self.paths[2].exists())
            if case == 'missing':
                self.paths[1].write_bytes(original)
            else:
                archive.unlink()

    def test_new_identity_replaces_multiple_targets_once(self):
        ready = self.control / 'UNIT_C9/02_ready' / self.paths[1].name
        ready.parent.mkdir()
        ready.write_text(SOURCE_1.replace('status: active', 'status: ready'))
        self.paths[1].unlink()
        draft = self.paths[2].with_name(
            "AN-S-9000@1-draft-SPEC-MANIFEST_NODE--declare-applicable-principle.md"
        )
        draft.write_text(
            SOURCE_2.replace("AN-S-3196", "AN-S-9000")
            .replace("version: 3", "version: 1")
            .replace("- AN-S-3302", "- AN-S-3196\n  - AN-S-3302")
        )
        self.paths[2].unlink()
        result = promote_draft(
            self.selection,
            {
                "target": {"ref_id": "AN-S-9000@1-draft", "version": 1},
                "targetStatus": "ready",
            },
            current_rows=capture_native(self.selection).atoms,
        )
        self.assertEqual("completed", result["outcome"], result)
        self.assertFalse(self.paths[0].exists())
        self.assertFalse(ready.exists())
        self.assertEqual(
            2, len(list((self.control / "UNIT_C9/09_archived").glob("*.md")))
        )
        self.assertTrue(
            (
                self.control
                / "UNIT_C9/02_ready/AN-S-9000-SPEC-MANIFEST_NODE--declare-applicable-principle.md"
            ).exists()
        )

    def test_invalid_target_and_other_header_drift_are_refused(self):
        for altered in (SOURCE_2.replace('AN-S-3302', 'AN-S-3302@1'),
                        SOURCE_2.replace('AN-S-3302', 'AN-S-3196'),
                        SOURCE_2.replace('- AN-S-3302', '- AN-S-3302\n  - AN-S-3302'),
                        SOURCE_2.replace('tier: 2', 'tier: 3')):
            self.paths[2].write_text(altered)
            with self.assertRaises((InputError, SourceChanged)):
                self.promote()
            self.assertTrue(all(path.exists() for path in self.paths))
            self.assertFalse((self.control / 'UNIT_C9/09_archived').exists())

    def test_activation_refuses_active_predecessor_or_successor(self):
        ready = self.control / 'UNIT_C9/02_ready' / self.paths[0].name
        ready.parent.mkdir()
        self.paths[0].unlink()
        self.paths[2].unlink()
        relation = 'relations:\n  IS_REPLACEMENT_FOR:\n  - {}\n'
        ready_text = SOURCE_0.replace('status: active', 'status: ready')
        for outgoing in (True, False):
            with self.subTest(outgoing=outgoing):
                ready.write_text(
                    ready_text.replace(
                        "state:", relation.format("AN-S-3302") + "state:"
                    )
                    if outgoing
                    else ready_text
                )
                self.paths[1].write_text(
                    SOURCE_1
                    if outgoing
                    else SOURCE_1.replace(
                        "state:", relation.format("AN-S-3196") + "state:"
                    )
                )
                target = {
                    "target": {"ref_id": "AN-S-3196", "version": 1},
                    "targetStatus": "active",
                }
                with self.assertRaisesRegex(
                    InputError, "cannot both be Active"
                ):
                    change_spec_status(
                        self.selection,
                        target,
                        current_rows=capture_native(self.selection).atoms,
                    )
                self.assertTrue(ready.exists())
                self.assertTrue(self.paths[1].exists())

    def test_draft_container_is_refused_when_target_is_archived(self):
        archived = self.control / 'UNIT_C9/09_archived/AN-S-3302@1-SPEC--set-the-applicable-principle-encapsulation.md'
        archived.parent.mkdir(parents=True)
        archived.write_text(self.paths[1].read_text().replace('status: active', 'status: archived'))
        self.paths[1].unlink()
        self.paths[2].with_suffix('').mkdir()
        with self.assertRaises(InputError):
            self.promote()
        self.assertTrue(self.paths[0].exists())
        self.assertTrue(self.paths[2].exists())

    def test_archive_failure_stops_before_publication(self):
        from unittest.mock import patch
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE import (
            native_replacement_promotion as promotion,
        )

        original = promotion.common.write_destination
        def write(root, path, raw):
            if '3302@' in path.name:
                return promotion.effects.Result(errors=[{'code': 'injected'}])
            return original(root, path, raw)

        draft = self.paths[2].with_name(
            "AN-S-9000@1-draft-SPEC-MANIFEST_NODE--declare-applicable-principle.md"
        )
        draft.write_text(
            SOURCE_2.replace("AN-S-3196", "AN-S-9000")
            .replace("version: 3", "version: 1")
            .replace("- AN-S-3302", "- AN-S-3196\n  - AN-S-3302")
        )
        self.paths[2].unlink()
        with patch.object(
            promotion.common, "write_destination", side_effect=write
        ):
            result = promote_draft(
                self.selection,
                {
                    "target": {"ref_id": "AN-S-9000@1-draft", "version": 1},
                    "targetStatus": "ready",
                },
                current_rows=capture_native(self.selection).atoms,
            )
        self.assertEqual("failed", result["outcome"])
        self.assertEqual("injected", result["errors"][0]["code"])
        self.assertFalse(self.paths[0].exists())
        self.assertTrue(self.paths[1].exists())
        self.assertTrue(draft.exists())
        self.assertTrue(any('3196@1' in effect.get('target', '') for effect in result['effects']))
        self.assertFalse((self.control / 'UNIT_C9/02_ready').exists())


class TicketReplacementTests(fixtures.NewNativeTaskTests, unittest.TestCase):
    def add_replacement(self, draft):
        import yaml

        _, text, body = draft.read_text().split("---", 2)
        header = yaml.safe_load(text)
        header["relations"] = {"IS_REPLACEMENT_FOR": ["AN-T-1"]}
        draft.write_text(
            "---\n" + yaml.safe_dump(header, sort_keys=False) + "---" + body
        )

    def test_first_ticket_archives_explicit_predecessor(self):
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import (
            create_draft,
        )

        result = create_draft(self.selection, self.new, current_rows=self.rows)
        self.add_replacement(self.root / result["savedDraft"]["path"])
        result = promote_draft(
            self.selection,
            {
                "target": {
                    "ref_id": result["savedDraft"]["ref_id"],
                    "version": 1,
                },
                "targetStatus": "backlog",
            },
            current_rows=capture_native(self.selection).atoms,
        )
        self.assertEqual("completed", result["outcome"], result)
        self.assertFalse(self.path.exists())
        self.assertTrue(
            (
                self.control
                / "001_TICKETS/TASKS/09_archived/AN-T-1@1-TASK--example.md"
            ).exists()
        )

    def test_ticket_tree_checks_and_archives_child_replacement_predecessor(self):
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import create_draft
        parent = create_draft(
            self.selection, self.new, current_rows=self.rows
        )["savedDraft"]
        child = create_draft(self.selection, {'newAtom': {
            'template': 'task', 'container': {'atom': parent['atom_id']}, 'body': '\n## Summary\n\nChild\n',
        }}, current_rows=capture_native(self.selection).atoms)['savedDraft']
        child_path = self.root / child['path']
        self.add_replacement(child_path)
        params = {
            "target": {"ref_id": parent["ref_id"], "version": 1},
            "targetStatus": "backlog",
        }
        original = self.path.read_text()
        backlog = self.path.parent / 'backlog' / self.path.name
        backlog.parent.mkdir()
        backlog.write_text(
            original.replace("status: active", "status: backlog")
        )
        self.path.unlink()
        with self.assertRaisesRegex(InputError, "Current Ready or Active"):
            promote_draft(
                self.selection,
                params,
                current_rows=capture_native(self.selection).atoms,
            )
        self.assertTrue(backlog.exists())
        self.assertTrue(child_path.exists())
        backlog.unlink()
        self.path.write_text(original)
        result = promote_draft(
            self.selection,
            params,
            current_rows=capture_native(self.selection).atoms,
        )
        self.assertEqual('completed', result['outcome'], result)
        self.assertFalse(self.path.exists())
        self.assertFalse(child_path.exists())
        self.assertTrue(
            (
                self.control
                / "001_TICKETS/TASKS/09_archived/AN-T-1@1-TASK--example.md"
            ).exists()
        )
