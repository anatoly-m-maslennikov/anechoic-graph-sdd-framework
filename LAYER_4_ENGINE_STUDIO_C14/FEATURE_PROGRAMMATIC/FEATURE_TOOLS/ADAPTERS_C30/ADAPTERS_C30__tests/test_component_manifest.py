import unittest

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    component_contract_fences, parse_component_manifest,
)


CANONICAL = '''## Summary

Declare Example

## Purpose

Maintain the selected examples.

## Component Identity

```python
from anechoic.model import ComponentManifest
ComponentManifest(component_id='C14', name='Example', layer=4, lens_whitelist=['SPEC'])
```

## Component Boundaries

```python
{'io': {'server': {'test': (1, None)}}, 'code': {'imports': ['C30']}}
```

## Component Contract

```python contract
declare_contract()
```

```python trace
declare_trace_contract()
```
'''


class ComponentManifestTests(unittest.TestCase):
    def test_tier_one_sections_preserve_identity_boundaries_and_contract_order(self):
        fields, purpose = parse_component_manifest(CANONICAL, tier=1)
        self.assertEqual(fields, {'component_id': 'C14', 'name': 'Example', 'layer': 4,
                                 'lens_whitelist': ['SPEC'], 'boundaries': {
                                     'io': {'server': {'test': (1, None)}}, 'code': {'imports': ['C30']}}})
        self.assertEqual(purpose, 'Maintain the selected examples.')
        self.assertEqual(component_contract_fences(CANONICAL), (
            ('python contract', 'declare_contract()\n'), ('python trace', 'declare_trace_contract()\n')))

    def test_legacy_manifest_remains_readable_at_tier_four(self):
        body = ("## Formal Manifest\n\n```python\nfrom anechoic.model import ComponentManifest\n"
                "ComponentManifest(component_id='C14', name='Example')\n```\n")
        self.assertEqual(parse_component_manifest(body, tier=4), ({'component_id': 'C14', 'name': 'Example'}, None))
        self.assertIsNone(component_contract_fences(body))
        with self.assertRaisesRegex(ValueError, 'Tier 1 Component Manifest'):
            parse_component_manifest(body, tier=1)
        with self.assertRaisesRegex(ValueError, 'requires Tier 1'):
            parse_component_manifest(CANONICAL, tier=4)

    def test_identity_is_the_only_required_manifest_section(self):
        _, identity = CANONICAL.split('## Component Identity', 1)
        body = '## Component Identity' + identity.split('## Component Boundaries', 1)[0]
        fields, purpose = parse_component_manifest(body, tier=1)
        self.assertEqual(fields, {'component_id': 'C14', 'name': 'Example', 'layer': 4,
                                  'lens_whitelist': ['SPEC']})
        self.assertIsNone(purpose)
        self.assertIsNone(component_contract_fences(body))

    def test_component_contract_preserves_prose_and_formal_claims(self):
        base, contracts = CANONICAL.split('## Component Contract', 1)
        body = base + '## Component Contract\n\n### Guarantee\n\nReturn the selected examples.\n'
        self.assertEqual(component_contract_fences(body), ())
        self.assertEqual(component_contract_fences(body + '\n### Formal Claim\n' + contracts),
                         component_contract_fences(CANONICAL))
        with self.assertRaisesRegex(ValueError, 'Expected prose'):
            parse_component_manifest(base + '## Component Contract\n', tier=1)

    def test_canonical_sections_are_unique_and_direct(self):
        for body, error in (
            (CANONICAL.replace('## Summary', '### Summary'), 'top-level'),
            (CANONICAL.replace('## Component Identity', '## Other'), 'Missing'),
            (CANONICAL.replace('Declare Example', ''), 'Expected prose'),
            (CANONICAL + '\n## Component Contract\n', 'top-level'),
            (CANONICAL + '\n## Formal Manifest\n', 'Ambiguous'),
            (CANONICAL.replace('## Component Boundaries\n', '## Component Boundaries\n\n### Nested\n'),
             'directly under'),
        ):
            with self.subTest(error=error), self.assertRaisesRegex(ValueError, error):
                parse_component_manifest(body, tier=1)

    def test_rejects_runnable_source_and_ambiguous_boundaries(self):
        for body, error in (
            (CANONICAL.replace("name='Example'", "name=print('Example')"), 'literals'),
            (CANONICAL.replace("name='Example'", "name='Example', boundaries=None"), 'Identity'),
            (CANONICAL.replace("{'io':", "dict() or {'io':"), 'literal mapping'),
            (CANONICAL.replace("'test': (1, None)", "'test': 0, 'test': 1"), 'duplicate dictionary key'),
        ):
            with self.subTest(error=error), self.assertRaisesRegex(ValueError, error):
                parse_component_manifest(body, tier=1)
