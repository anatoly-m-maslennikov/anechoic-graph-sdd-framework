"""Workbench schema generator cases."""

import json
from pathlib import Path
from unittest.mock import Mock, patch

from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.\
    FEATURE_IWE_CONSOLE_BACKEND__shared import compile_project_schema  # fmt: skip
from ..workbench_schema_fixture import atom


class SchemaGeneratorCases:
    def test_project_generator_uses_one_reader_capture_and_writes_exact_bytes(
        self,
    ) -> None:
        row = atom(header={"atom_id": "CA-R-1"})
        draft = atom(
            "CA-R-2",
            header={"atom_id": "CA-R-2"},
            body="## Summary\n\nEdited Draft.\n",
        )
        draft["status_group"] = "Draft"
        reader = Mock(
            capture=Mock(side_effect=[([row], []), ([row, draft], [])]),
            model_rows=Mock(return_value=[]),
        )
        with patch(
            (
                "IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND."
                "generate_workbench_schema.SourceReader"
            ),
            return_value=reader,
        ):
            first = compile_project_schema(Path("/project"))
            second = compile_project_schema(Path("/project"))
        self.assertEqual(first, second)
        self.assertEqual(2, reader.capture.call_count)
        self.assertEqual([], json.loads(first)["sources"])

    def test_project_generator_emits_declared_status_groups(self) -> None:
        row = atom(
            form="Declaration",
            body="""## Claim

### Formal Claim

```python
from anechoic.model import Plan
from anechoic.formal_claims import declare_entity
declare_entity(
    entity_name="Status", relation_name="IS_PROPERTY_OF", base_path="Atom.Header.State",
    applies_to_entity_classes=(Plan,), allowed_values=("Backlog", "Done"),
    status_groups={"Backlog": "Backlog"},
)
```
""",
        )
        ordinary = atom(
            "CA-R-2",
            body="## Claim\n\n### Formal Claim\n\n```python\nvalue = 1\n```\n",
        )
        rows = [row, ordinary]
        reader = Mock(
            capture=Mock(return_value=(rows, [])),
            model_rows=Mock(return_value=rows),
        )
        with patch(
            (
                "IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND."
                "generate_workbench_schema.SourceReader"
            ),
            return_value=reader,
        ):
            asset = json.loads(compile_project_schema(Path("/project")))
        self.assertEqual(
            [["Plan", "Backlog", "Backlog"]], asset["status_groups"]
        )
