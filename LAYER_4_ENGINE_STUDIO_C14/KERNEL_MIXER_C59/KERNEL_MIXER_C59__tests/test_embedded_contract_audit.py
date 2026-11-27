"""Check Package coverage for embedded Component Contracts."""
from collections import defaultdict
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch
import json

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    NativeCapture,
)

from KERNEL_MIXER_C59.package_audit import _audit_rows, _contract_candidates
from .test_component_projection import IDENTITY


class EmbeddedContractAuditTests(TestCase):
    def test_embedded_contract_supersedes_legacy_and_uses_exact_pin(self):
        def row(ref, template, body, tier):
            return {'ref': ref, '_exact_ref': ref + '@2', 'status_group': 'Current',
                    'tier': tier, 'source_path': ref + '.md', '_content_bytes': body.encode(),
                    'header_json': {'context': {'template': template, 'lens': 'SPEC'}}}

        legacy = row("AN-S-4", "component_contract", "", 0)
        manifest = row(
            "AN-S-3",
            "component_manifest",
            IDENTITY + "\n## Component Contract\n\nGuarantee.\n",
            1,
        )
        capture = NativeCapture(
            atoms=[legacy, manifest],
            containment=[
                {
                    "source_ref": "AN-S-4",
                    "target_kind": "Component",
                    "target_ref": "C3",
                },
                {
                    "source_ref": "AN-S-3",
                    "target_kind": "Component",
                    "target_ref": "C1",
                },
            ],
            errors={},
        )
        selection = SimpleNamespace(project_prefix="AN")
        with patch(
            "KERNEL_MIXER_C59.package_audit.read_component_contract",
            return_value={"ref_id": "AN-S-4@2"},
        ):
            _, contracts = _contract_candidates(selection, capture)
            self.assertEqual(['AN-S-3@2'], contracts['C3'])
            pins = defaultdict(list, {'pkg': [('implements', 'AN-S-3@2')]})
            rows = _audit_rows([('key', 'pkg')], {}, pins, {}, selection, {},
                               {'pkg': contracts['C3']}, set(), set(), set(), defaultdict(set))
            self.assertEqual([{'ref': 'AN-S-3@2', 'covered': True}], json.loads(rows[0][-1]))
            manifest['_content_bytes'] = IDENTITY.encode()
            _, contracts = _contract_candidates(selection, capture)
            self.assertEqual(['AN-S-4@2'], contracts['C3'])
