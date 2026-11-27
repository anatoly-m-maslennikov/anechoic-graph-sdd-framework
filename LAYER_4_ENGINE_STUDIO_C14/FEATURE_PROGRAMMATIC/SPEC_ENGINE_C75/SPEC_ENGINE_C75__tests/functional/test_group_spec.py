import hashlib
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from ...LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_2_SPEC_READING_C83 \
    ._package__shared import (
    recognized_claim,
)
from ...LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_2_SPEC_READING_C83 \
    .SPECIFICATION_MODEL_C85._package__shared import (
    parse_group,
)
from ...LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_3_MERMAID_RENDERER_C87 \
    ._package__shared import (
    group_to_mermaid,
)
from ...LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_4_SPEC_COMPARISON_C88 \
    ._package__shared import (
    check_group_spec,
)

LEAN = os.environ.get('ANECHOIC_TEST_LEAN') or os.environ.get('LEAN_BIN') or 'lean'
CONTRACT = "declare_group_contract(roles={'generation': 'C50', 'core': 'C52'}, entry_points=('api',))"
SOLUTION = "component_group(roles={'generation': 'C50', 'core': 'C52'}, entry_points=('api',))"

ROOT = Path(__file__).resolve().parents[5]
TOOLS = (ROOT / '_anechoic_anechoic/LAYER_4_ENGINE_STUDIO_C14/'
         'FEATURE_PROGRAMMATIC_C15/FEATURE_TOOLS_C16')
GROUP = TOOLS / 'FEATURE_GROUP_SCHEDULERS_C32'
SCHEDULER_FILES = (
    (TOOLS / ('01_draft/AN-S-3070@4-draft-SPEC-COMPONENT_MANIFEST--'
              'declare-schedulers.md'),
     'AN-S-3070', 4, 'draft', 'C16',
     '91058117b53fa2bb5931a32a4599ff7dc3eceab7a6430f75594e874148147af2'),
    (GROUP / ('01_draft/AN-S-5059@1-draft-DES-SOLUTION--'
              'group-batch-and-workflow-schedulers.md'),
     'AN-S-5059', 1, 'draft', 'C32',
     '98c484c9585c05400a856a3874aa1f643209f445e7809ef4a6ef149a0d89a863'),
    (GROUP / ('01_TIER_1_ARCHITECTURE/AN-S-3074-SPEC-COMPONENT_MANIFEST--'
              'declare-batch-scheduler.md'),
     'AN-S-3074', 4, 'active', 'C32',
     '3f9afd6ba412be2fd31b218b258f86bf5eb7efc782c6ceebe551abf3a01777d6'),
    (GROUP / ('01_TIER_1_ARCHITECTURE/AN-S-3075-SPEC-COMPONENT_MANIFEST--'
              'declare-workflow-scheduler.md'),
     'AN-S-3075', 4, 'active', 'C32',
     '574850878f00dbddf87ec3136e42ee6e05813c40f5d3328dccb28afe06eb5f9d'),
)


def scheduler_inputs(root, *, swapped=False):
    pins = []
    for path, atom, version, status, owner, digest in SCHEDULER_FILES:
        content = path.read_bytes()
        if swapped and atom in ('AN-S-3070', 'AN-S-5059'):
            content = content.replace(
                b"'batch_scheduler': 'C41', 'workflow_scheduler': 'C42'",
                b"'batch_scheduler': 'C42', 'workflow_scheduler': 'C41'")
            digest = hashlib.sha256(content).hexdigest()
        (root / path.name).write_bytes(content)
        pins.append({'path': path.name, 'atom_id': atom, 'version': version,
                     'status': status, 'container_component': owner,
                     'sha256': digest})
    providers = {
        'batch_scheduler': {'component_id': 'C41', 'name': 'BATCH_SCHEDULER',
                            'manifest': pins[2]},
        'workflow_scheduler': {'component_id': 'C42',
                               'name': 'WORKFLOW_SCHEDULER',
                               'manifest': pins[3]},
    }
    return pins, providers


def model(contract=CONTRACT, solution=SOLUTION, server=None):
    boundaries = {"io": {"server": {"api": {}} if server is None else server}}
    return {
        "component_id": "C51",
        "manifest": {
            "source": {"atom_id": "M"},
            "fields": {
                "component_id": "C51",
                "name": "Model",
                "boundaries": boundaries,
            },
            "boundaries": boundaries,
        },
        "contract": {
            "source": {"atom_id": "C"},
            "claims": [("python group", contract)],
        },
        "solution": {
            "source": {"atom_id": "S"},
            "claims": [("python group", solution)],
        },
    }


class GroupSpecTests(unittest.TestCase):
    def check(
        self,
        *,
        children=("C50", "C52"),
        contract=CONTRACT,
        solution=SOLUTION,
        server=None,
        current_record_count=None,
    ):
        with patch(
            "FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_2_SPEC_READING_C83._package__shared.load_boundary_model",
            return_value=model(contract, solution, server),
        ):
            return check_group_spec(
                ".",
                "C51",
                {},
                {},
                {},
                structure_children=children,
                current_record_count=current_record_count,
                lean=LEAN,
            )

    def test_structure_and_entrypoint_comparison(self):
        result = self.check()
        self.assertEqual(
            "matched", result["directions"]["manifest_contract"]["status"]
        )
        self.assertEqual(
            "matched", result["directions"]["contract_solution"]["status"]
        )
        self.assertEqual(["C50", "C52"], result["structure_children"])
        self.assertIn("C51 -->|generation| C50", result["mermaid"])
        for children in (("C50",), ("C50", "C53")):
            self.assertEqual(
                "conflicting",
                self.check(children=children)["directions"][
                    "manifest_contract"
                ]["status"],
            )
        result = self.check(server={"api": {}, "extra": {}})
        self.assertEqual(
            "conflicting", result["directions"]["manifest_solution"]["status"]
        )
        result = self.check(
            solution=SOLUTION.replace(
                "'generation': 'C50', 'core': 'C52'",
                "'generation': 'C52', 'core': 'C50'",
            )
        )
        self.assertEqual(
            "conflicting", result["directions"]["contract_solution"]["status"]
        )
        self.assertTrue(self.check(server="unsupported")["unresolved"])

    def test_omitted_entry_points_remain_unknown(self):
        contract = "declare_group_contract(roles={'generation': 'C50', 'core': 'C52'})"
        solution = (
            "component_group(roles={'generation': 'C50', 'core': 'C52'})"
        )
        self.assertEqual(
            {"roles": {"generation": "C50", "core": "C52"}},
            parse_group(solution, "solution"),
        )
        result = self.check(
            contract=contract, solution=solution, server="unsupported"
        )
        self.assertEqual("unresolved", result["status"])
        self.assertEqual(
            "matched", result["directions"]["contract_solution"]["status"]
        )
        self.assertEqual(
            {"M", "C", "S"},
            {gap["source"]["atom_id"] for gap in result["unresolved"]},
        )
        result = self.check(contract=CONTRACT, solution=solution)
        self.assertEqual('unresolved', result['directions']['contract_solution']['status'])
        result = self.check(contract=contract, solution=solution.replace("'C52'", "'C53'"))
        self.assertEqual('conflicting', result['directions']['contract_solution']['status'])
        empty = solution[:-1] + ', entry_points=[])'
        result = self.check(contract=CONTRACT, solution=empty)
        self.assertEqual(
            "conflicting", result["directions"]["contract_solution"]["status"]
        )
        self.assertEqual([], parse_group(empty, "solution")["entry_points"])

    def test_current_record_count(self):
        contract = CONTRACT[:-1] + ", current_record_count=500)"
        solution = SOLUTION[:-1] + ", current_record_count=500)"
        result = self.check(
            contract=contract, solution=solution, current_record_count=500
        )
        self.assertTrue(
            all(
                direction["status"] == "matched"
                for direction in result["directions"].values()
            )
        )
        self.assertIn("C51 (500 records)", result["mermaid"])
        changed = self.check(
            contract=contract,
            solution=solution.replace("500", "499"),
            current_record_count=500,
        )
        self.assertEqual(
            "conflicting", changed["directions"]["contract_solution"]["status"]
        )
        self.assertIn("C51 (499 records)", changed["mermaid"])
        self.assertEqual(
            "conflicting",
            self.check(
                contract=contract, solution=solution, current_record_count=499
            )["status"],
        )
        result = self.check(contract=contract, solution=solution)
        self.assertEqual('unresolved', result['status'])
        self.assertEqual('unresolved', result['directions']['manifest_contract']['status'])
        self.assertIn('M', {gap['source']['atom_id'] for gap in result['unresolved']})
        result = self.check(contract=CONTRACT, solution=solution, current_record_count=500)
        self.assertEqual('unresolved', result['directions']['contract_solution']['status'])
        self.assertIn('C', {gap['source']['atom_id'] for gap in result['unresolved']})
        for invalid in ('-1', 'True', "'500'", '1.5'):
            with self.assertRaises(ValueError):
                parse_group(SOLUTION[:-1] + f', current_record_count={invalid})', 'solution')
        with self.assertRaises(ValueError):
            self.check(current_record_count=True)

    def test_safe_literals_and_empty_group(self):
        empty = 'component_group(roles={}, entry_points=())'
        self.assertTrue(recognized_claim('solution', 'python group', empty))
        self.assertEqual({'roles': {}, 'entry_points': []}, parse_group(empty, 'solution'))
        for bad in (empty.replace('{}', "{'x': run()}"),
                    empty.replace('{}', "{'x': 'C1', 'x': 'C2'}"), empty + '\nrun()'):
            with self.assertRaises((ValueError, TypeError)):
                parse_group(bad, 'solution')
        with self.assertRaises(ValueError):
            self.check(children=('C50', 'C50'))
        with self.assertRaises(ValueError):
            self.check(children=('C51',))
        with self.assertRaises(ValueError):
            group_to_mermaid({'roles': {}}, 'C51]; malicious')
        shared = parse_group("component_group(roles={'a': 'C50', 'b': 'C50'}, entry_points=())", 'solution')
        self.assertEqual({'a': 'C50', 'b': 'C50'}, shared['roles'])

    def test_reviewed_scheduler_role_witness(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pins, providers = scheduler_inputs(root)
            args = (root, 'C32', pins[0], None, pins[1])
            options = {'structure_children': ('C41', 'C42'), 'lean': LEAN}
            result = check_group_spec(
                *args, role_providers=providers, **options)
            self.assertEqual('matched', result['status'])
            self.assertEqual('complete', result['role_provider_coverage'])
            self.assertEqual('matched',
                             result['manifest_consistency']['status'])
            self.assertIn({'key': 'entry_points', 'left': [], 'right': [],
                           'status': 'matched'},
                          result['directions']['manifest_solution']['facts'])
            self.assertEqual(
                pins[2], result['role_provider_sources']['batch_scheduler'])
            legacy = check_group_spec(*args, **options)
            self.assertEqual('matched', legacy['status'])
            self.assertEqual('not_selected', legacy['role_provider_coverage'])
            partial = check_group_spec(
                *args, role_providers={'batch_scheduler': providers[
                    'batch_scheduler']}, **options)
            self.assertEqual('unresolved', partial['status'])
            self.assertEqual('partial', partial['role_provider_coverage'])
            pins, _ = scheduler_inputs(root, swapped=True)
            swapped = check_group_spec(root, 'C32', pins[0], None, pins[1],
                                       role_providers=providers, **options)
            self.assertEqual('conflicting', swapped['status'])
            self.assertEqual('conflicting',
                             swapped['manifest_consistency']['status'])
            facts = swapped['directions']['manifest_solution']['facts']
            self.assertEqual(
                {'role.batch_scheduler', 'role.workflow_scheduler'},
                {fact['key'] for fact in facts
                 if fact['status'] == 'conflicting'})

    def test_role_witness_rejects_invalid_identity_and_pin(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pins, providers = scheduler_inputs(root)
            args = (root, 'C32', pins[0], None, pins[1])
            batch = providers['batch_scheduler']
            for replacement in (
                {**batch, 'name': 'WORKFLOW_SCHEDULER'},
                {**batch, 'component_id': 'C42'},
                {**batch, 'component_id': 'C99'},
                {**batch, 'manifest': {k: v for k, v in pins[2].items()
                                       if k != 'sha256'}},
                {**batch, 'manifest': {**pins[2], 'sha256': '0' * 64}},
                {**batch, 'manifest': {**pins[2],
                                       'container_component': 'C16'}},
            ):
                with self.subTest(replacement=replacement), \
                        self.assertRaises(ValueError):
                    check_group_spec(
                        *args, structure_children=('C41', 'C42'),
                        role_providers={**providers,
                                        'batch_scheduler': replacement},
                        lean=LEAN)
            path = root / pins[2]['path']
            content = path.read_bytes().replace(b'component: C32',
                                                b'component: C16')
            path.write_bytes(content)
            pin = {**pins[2], 'container_component': 'C16',
                   'sha256': hashlib.sha256(content).hexdigest()}
            providers['batch_scheduler'] = {**batch, 'manifest': pin}
            with self.assertRaisesRegex(ValueError, 'not a direct child'):
                check_group_spec(*args, structure_children=('C41', 'C42'),
                                 role_providers=providers, lean=LEAN)
