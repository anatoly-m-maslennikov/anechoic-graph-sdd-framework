from pathlib import Path
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

import subject_notation as notation
from ATOM_LIFECYCLE.source import bind_query_reader
from ATOM_LIFECYCLE.subject_selections import resolve_named_selection


class NamedSelectionTests(TestCase):
    def test_requires_exact_current_defining_claim(self):
        def pin(claim):
            metadata = {"role": "Requirement", "form": "Rule", "status": "Active",
                        "topics": {"main_subject": subject}}
            body = f"---\natom_id: CA-R-1\n---\n\n## Claim\n\n### Formal Claim\n\n```python\n{claim}\n```\n"
            return SimpleNamespace(metadata=metadata, raw=body.encode(), path=Path("CA-R-1.md"))

        subject = "ANECHOIC_STRUCTURE <+ Named Selection//Extension Sources"
        expression = notation.parse_subject_expression(subject, subject_profile="approved").expression
        selection = SimpleNamespace(settings={"project": {"name": "anechoic"}})
        reader = SimpleNamespace(run=lambda *args, **kw: {"rows": [["CA-R-1"]], "has_more": False})
        with bind_query_reader(reader), patch("ATOM_LIFECYCLE.subject_selections.select_current_sources") as sources:
            sources.return_value = {"CA-R-1": pin('subject_path(address="Named Selection//Extension Sources")')}
            self.assertTrue(resolve_named_selection(selection, expression))
            sources.return_value = {"CA-R-1": pin('subject_path(address="Named Selection//Other")')}
            self.assertFalse(resolve_named_selection(selection, expression))
            for claim in ('subject_path(address="Named Selection//Extension Sources", extra=True)',
                          'subject_path(address=str("Named Selection//Extension Sources"))',
                          'subject_path(address="Named Selection//Extension Sources")\nprint("extra")'):
                sources.return_value = {"CA-R-1": pin(claim)}
                self.assertFalse(resolve_named_selection(selection, expression))
