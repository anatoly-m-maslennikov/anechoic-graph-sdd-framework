"""Status source selection ignores unrelated typed Property declarations."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import StatusModelError
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import _staged_declarations


class StatusScanTypedPropertyTest(unittest.TestCase):
    def test_typed_property_is_not_a_status_declaration(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'CA-R-2541.md').write_text('''---
atom_id: CA-R-2541
role: Requirement
form: Declaration
status: Active
version: 1
---
## Claim
### Formal Claim
```python
from anechoic.formal_claims import declare_entity
from anechoic.model import NamedSelection

declare_entity(
    entity_name="Named Selection",
    relation_name="IS_PROPERTY_OF",
    base_path="Projection.Source",
    property_occurrence_cardinality=1,
    value_format=NamedSelection,
    value_cardinality=1,
    dependent_property_cardinality=0,
)
```
''', encoding='utf-8')
            with self.assertRaisesRegex(StatusModelError, 'no current Status declarations'):
                _staged_declarations(root)


if __name__ == '__main__':
    unittest.main()
