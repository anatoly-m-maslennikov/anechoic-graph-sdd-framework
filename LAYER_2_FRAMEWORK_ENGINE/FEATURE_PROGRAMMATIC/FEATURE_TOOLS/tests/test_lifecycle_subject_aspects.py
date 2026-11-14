"""Resolve Project Aspects from active, selected Declaration Claims."""

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import unittest

from ATOM_LIFECYCLE.source import bind_query_reader
from ATOM_LIFECYCLE.subject_aspects import resolve_aspect


def source(ref, claim, status="active", form="Declaration"):
    raw = ("---\natom_id: " + ref + "\nrole: Requirement\nform: " + form +
           "\nstatus: " + status + "\nversion: 1\n---\n\n## Claim\n\n### Formal Claim\n\n"
           "```python\n" + claim + "\n```\n").encode()
    return SimpleNamespace(path=Path(ref + ".md"), raw=raw,
                           metadata={"role": "Requirement", "form": form, "status": status})


class AspectResolutionTests(unittest.TestCase):
    def setUp(self):
        self.selection = SimpleNamespace(settings={"project": {"name": "caprmedio"}})
        self.subject = "CAPRMEDIO_STRUCTURE <+ Aspects <+ Engineering <+ Query"
        self.address = "PROJECT STRUCTURE//CAPRMEDIO <+ Aspects <+ Engineering <+ Query"
        self.claim = ("from caprmedio.formal_claims import declare_entity\n"
                      "from caprmedio.model import Aspect\n"
                      f"declare_entity(entity_name='Query', instance=Aspect(address={self.address!r}))")
        self.reader = SimpleNamespace(run=lambda *args, **kwargs: {"rows": [["CA-R-1"]], "has_more": False})

    def resolve(self, claim=None, **pin_options):
        pin = source("CA-R-1", claim or self.claim, **pin_options)
        with bind_query_reader(self.reader), patch(
            "ATOM_LIFECYCLE.subject_aspects.select_current_sources", return_value={"CA-R-1": pin}
        ):
            return resolve_aspect(self.selection, self.subject)

    def test_explicit_aspect_and_equivalent_namespace(self):
        self.assertTrue(self.resolve())
        pin = source("CA-R-1", self.claim)
        with bind_query_reader(self.reader), patch(
            "ATOM_LIFECYCLE.subject_aspects.select_current_sources", return_value={"CA-R-1": pin}
        ):
            self.assertTrue(resolve_aspect(self.selection, self.address))
            self.assertTrue(resolve_aspect(self.selection, "CAPRMEDIO <+ STRUCTURE <+ Aspects <+ Engineering <+ Query"))

    def test_hierarchy_requires_aspect_membership(self):
        prefix = "from caprmedio.formal_claims import declare_entity\n"
        def claim(members):
            return (prefix + "declare_entity(entity_name='Project Structure', "
                    f"structure_paths=({self.address!r},), aspect_memberships={members!r})")
        self.assertTrue(self.resolve(claim((self.address,))))
        self.assertFalse(self.resolve(claim(())))

    def test_legacy_named_aspect_uses_the_defining_composition(self):
        self.subject = "PROJECT STRUCTURE//CAPRMEDIO <+ Aspect//Visual Design"
        claim = 'composition(container="PROJECT STRUCTURE//CAPRMEDIO", parts=("Aspect//Visual Design",))'
        self.assertTrue(self.resolve(claim))
        self.assertFalse(self.resolve('subject_path(address="Aspect//Visual Design")'))
        self.assertFalse(self.resolve('composition(container="PROJECT STRUCTURE//CAPRMEDIO", '
                                      'parts=(str("Aspect//Visual Design"),))'))
        self.assertFalse(self.resolve(claim + '\nprint("extra")'))
        self.assertTrue(self.resolve(claim + '\n' + claim))

    def test_path_is_exact_and_source_must_be_an_active_declaration(self):
        different = self.claim.replace("Engineering <+ Query", "Product <+ Query")
        self.assertFalse(self.resolve(different))
        self.assertFalse(self.resolve(status="done"))
        self.assertFalse(self.resolve(form="Requirement"))

    def test_unavailable_or_incomplete_query_fails_explicitly(self):
        with self.assertRaisesRegex(ValueError, "query API"):
            resolve_aspect(self.selection, self.subject)
        self.reader.run = lambda *args, **kwargs: {"rows": [], "has_more": True}
        with bind_query_reader(self.reader), self.assertRaisesRegex(ValueError, "incomplete"):
            resolve_aspect(self.selection, self.subject)

    def test_proposed_definition_can_introduce_its_own_aspect(self):
        pin = source("CA-R-1", self.claim)
        body = pin.raw.decode().split("---", 2)[2]
        self.assertTrue(resolve_aspect(self.selection, self.subject, proposed_body=body))

    def test_different_project_and_non_aspect_are_not_selected(self):
        self.assertIsNone(resolve_aspect(self.selection, "PROJECT STRUCTURE//OTHER <+ Aspects <+ Query"))
        self.assertIsNone(resolve_aspect(self.selection, "CAPRMEDIO_STRUCTURE <+ Scope Unit//TOOLS"))
