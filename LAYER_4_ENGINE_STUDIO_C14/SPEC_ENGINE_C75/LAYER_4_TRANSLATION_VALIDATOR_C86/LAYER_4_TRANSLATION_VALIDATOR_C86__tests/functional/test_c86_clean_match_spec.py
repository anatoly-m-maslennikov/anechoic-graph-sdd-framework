import copy
import re
import unittest
from pathlib import Path

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    parse_component_manifest,
)
from SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C85.contract_model__pub import (
    parse_trace_contract,
)
from SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C85.trace_manifest__pub import outcome_cases
from SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C85.workflow_model__pub import (
    normalize_workflow,
    parse_workflow,
)
from SPEC_ENGINE_C75.LAYER_4_SPEC_COMPARISON_C88.trace_spec__pub import (
    compare_trace_workflow,
)
from SPEC_ENGINE_C75.LAYER_4_TRANSLATION_VALIDATOR_C86.LAYER_4_TRANSLATION_VALIDATOR_C86__tests.functional.test_translation_validation import (
    lean_path,
)


class CleanMatchSpecTests(unittest.TestCase):
    def test_findings_cannot_precede_a_matched_return(self):
        root = next(path for path in Path(__file__).resolve().parents if (path / '_anechoic_anechoic').is_dir())
        drafts = root / '_anechoic_anechoic/LAYER_4_ENGINE_STUDIO_C14/SPEC_ENGINE_C75'
        manifest, contract, solution = [next(drafts.rglob(f'AN-S-{number}@1-*.md')).read_text()
                                        for number in (4933, 4960, 4961)]
        fields, _ = parse_component_manifest(manifest)
        cases, _ = outcome_cases(fields['boundaries'])
        manifest_match = next(case for case in cases if case['output'] == 'matched')
        source = re.search(r'```python trace\n(.*?)\n```', contract, re.DOTALL).group(1)
        contract_match = parse_trace_contract(source)
        source = re.search(r'```python\n(.*?)\n```', solution, re.DOTALL).group(1)
        workflow = parse_workflow(source)
        invalid = copy.deepcopy(workflow)
        states = invalid['machine']['states']
        edge = copy.deepcopy(states['checking']['on']['unresolved_effect'])
        edge['target'] = 'known_unresolved'
        states['checking']['on']['unresolved_is_present'] = edge
        states['known_unresolved'] = {'on': {'acknowledge_validation':
                                      copy.deepcopy(states['checking']['on']['matched_effect'])}}
        lean = lean_path(self)
        for case in (manifest_match, contract_match):
            for candidate, expected in ((workflow, 'matched'), (invalid, 'conflicting')):
                normalized = {'action': candidate['action'], **normalize_workflow(candidate['machine'])}
                result = compare_trace_workflow(case, normalized, lean=lean)
                self.assertEqual(expected, result['status'], result)
