import hashlib
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.\
    LAYER_2_SPEC_READING_C83.SPECIFICATION_MODEL_C85._package__shared \
    import validate_declaration  # fmt: skip


CONTRACT = """declare_contract(operation='POST /tools', outcomes={
    'success': (200, 'result'), 'invalid_input': (400, 'typed_error'),
    'internal_error': (500, 'typed_error')})"""
SOLUTION = """component_workflow(component='C7', action='invoke', machine={
    'id': 'invoke', 'initial': 'start', 'states': {
        'start': {'on': {'finish': {'target': 'done', 'guard': {
            'type': 'matchesTrace', 'params': {'kind': 'output'}}}}},
        'done': {'type': 'final'}}})"""


def _carrier(
    root, role, claim, language=None, tier=None, template_override=None
):
    template, default_tier, default_language = {
        "contract": ("component_contract", 0, "python contract"),
        "solution": ("decision", 1, "python"),
    }[role]
    pin = {
        "path": role + ".md",
        "atom_id": "AN-S-1",
        "version": 1,
        "status": "active",
        "container_component": "C7",
    }
    source = (
        f"---\natom_family: SPEC\natom_id: AN-S-1\ncontainer: {{component: C7}}\n"
        f"tier: {default_tier if tier is None else tier}\n"
        f"context: {{template: {template_override or template}}}\nrelations: {{}}\n"
        f"state: {{status: active, version: 1}}\n---\n"
        f"## Claim\n\n### Formal Claim\n\n```{language or default_language}\n{claim}\n```\n"
    )
    (root / pin["path"]).write_text(source)
    return pin


class DeclarationValidationTests(unittest.TestCase):
    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)

    def test_valid_standalone_contract_and_solution(self):
        for role, claim in (("contract", CONTRACT), ("solution", SOLUTION)):
            with self.subTest(role=role):
                pin = _carrier(self.root, role, claim)
                result = validate_declaration(self.root, "C7", role, pin)
                self.assertEqual([], result["issues"])
                self.assertEqual([], result["unresolved"])
                self.assertEqual(pin["atom_id"], result["source"]["atom_id"])
                self.assertEqual(
                    hashlib.sha256(
                        (self.root / pin["path"]).read_bytes()
                    ).hexdigest(),
                    result["source"]["sha256"],
                )
                (self.root / pin["path"]).unlink()

    def test_invalid_claims_are_reported(self):
        for role, claim, language in (
            ("contract", "declare_contract(", None),
            ("solution", "def x := True", "lean"),
        ):
            with self.subTest(role=role):
                pin = _carrier(self.root, role, claim, language)
                result = validate_declaration(self.root, "C7", role, pin)
                self.assertTrue(result["issues"] or result["unresolved"])

    def test_standalone_tier_zero_solution(self):
        pin = _carrier(
            self.root,
            "solution",
            SOLUTION,
            tier=0,
            template_override="solution",
        )
        result = validate_declaration(self.root, "C7", "solution", pin)
        self.assertEqual([], result["issues"])
        self.assertEqual([], result["unresolved"])

    def test_wrong_tier_or_component_is_rejected(self):
        for role, claim, tier in (
            ("contract", CONTRACT, 1),
            ("solution", SOLUTION, 0),
        ):
            with self.subTest(role=role, mismatch="tier"):
                pin = _carrier(self.root, role, claim, tier=tier)
                with self.assertRaises(ValueError):
                    validate_declaration(self.root, "C7", role, pin)
            with self.subTest(role=role, mismatch="component"):
                pin = _carrier(self.root, role, claim)
                with self.assertRaises(ValueError):
                    validate_declaration(self.root, "C8", role, pin)
