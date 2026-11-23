"""Join the carrier, Model, and Component placement checks on temporary Markdown files."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import yaml

from verify_native_templates import model_validator
from carrier_cases import select_revision, validate_carrier
from structure_cases import validate_component_tree, validate_manifest
from FEATURE_APPS.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.markdown_content import (
    formal_claim_fences, parse_content,
)
from ADAPTERS_C30.carrier_read__pub import parse_carrier


PROJECT = "C0"
PARENTS = {PROJECT: None, "C20": PROJECT, "C43": "C20", "C44": "C20"}
SECTIONS = {
    "C20": Path(".anechoic_anechoic/ENGINE_STUDIO_C20"),
    "C43": Path(".anechoic_anechoic/BACKEND_DECK_C43"),
    "C44": Path(".anechoic_anechoic/MCP_PATCHBAY_C44"),
}
MANIFEST_FILENAME = "AN-S-096-SPEC--declare-backend-deck.md"
GROUP_DIRECTORIES = {"draft": "Draft", "archived": "Archived"}


def read_review_carrier(path, root, project_name, prefix):
    try:
        relative = path.resolve().relative_to(root.resolve())
    except ValueError:
        raise ValueError("Carrier is outside the selected Project root") from None
    carrier = parse_carrier(path.read_bytes(), path)
    body = {tuple(record["property_path"]): record["direct_markdown"].strip()
            for record in parse_content(carrier.body) if record["direct_markdown"] is not None}
    header = carrier.metadata
    context = header["context"]
    state = header["state"]
    lens = context.get("lens")
    fields = dict(atom_id=header["identity"]["atom_id"], version=state["version"], status=state["status"],
                  summary=body[("summary",)], project_prefix=prefix, lens=lens)
    group = GROUP_DIRECTORIES.get(relative.parent.name, "Current")
    # These fixtures use only the SPEC lens and omit the template token.
    marker = relative.name.partition("--")[0]
    if lens:
        marker = marker.removesuffix(f"-{lens}")
    observed_ref = f"{marker}@{state['version']}" if group == "Current" else marker
    section = SECTIONS.get(context["container"].get("component"), Path(f".anechoic_{project_name}"))
    selection = validate_carrier(relative, project_name, group, observed_ref, fields,
                                 enabled_lenses={"SPEC"}, spec_section=section)
    return context, body, fields, selection[:2], carrier.body


class CarrierModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = [
            (name, row["subject"], row["claim"])
            for name in ("native-graph-claims.json", "native-spec-template-claims.json")
            for row in json.loads(Path(__file__).with_name(name).read_text())
        ]
        cls.types, validate = model_validator(cls.records, "_anechoic_carrier_review", cls.addClassCleanup)
        cls.validate = staticmethod(validate)
        validate_component_tree(PROJECT, PARENTS)
        cls.components = {PROJECT: validate("Project")}
        for component, parent in PARENTS.items():
            if parent is not None:
                cls.components[component] = validate("Component", {"CHILD_OF": [cls.components[parent]]})

    def setUp(self):
        self.workspace = Path(self.enterContext(TemporaryDirectory()))
        self.root = self.workspace / "anechoic"

    def write(self, relative, body, *, root=None, atom_id="AN-S-096", owner="C20", tier=0,
              version=3, status="active"):
        path = (root or self.root) / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        header = {
            "identity": {"atom_id": atom_id},
            "context": {"container": {"component": owner}, "tier": tier},
            "state": {"status": status, "version": version, "updated_at": "2026-11-19T00:00:00Z"},
        }
        if "-S-" in atom_id and status == "active":
            header["context"]["lens"] = "SPEC"
        path.write_text(f"---\n{yaml.safe_dump(header, allow_unicode=True)}---\n\n{body}", encoding="utf-8")
        return path

    def manifest(self, relative=None, *, component="C43", owner="C20", **header):
        body = "## Summary\n\nDeclare Backend Deck\n\n## Claim\n"
        if component is not None:
            body += f"\n### Component ID\n\n{component}\n"
        body += "\n### Name\n\nBackend Deck\n\n### Layer\n\n2\n"
        return self.write(relative or SECTIONS["C20"] / "SPEC" / MANIFEST_FILENAME,
                          body, owner=owner, **header)

    def component_spec(self, path, kind="Component Manifest", *, peers=()):
        context, body, fields, (group, ref), _ = read_review_carrier(path, self.root, "anechoic", "AN")
        container = context["container"]
        if (not isinstance(container, dict) or container.keys() != {"component"}
                or container["component"] not in self.components):
            raise ValueError("The Manifest or Purpose needs an existing Component container")
        owner = container["component"]
        if not (component := body.get(("claim", "component_id"))):
            raise ValueError("Described Component ID is missing")
        properties = ({"name": body[("claim", "name")], "layer": int(body[("claim", "layer")])}
                      if kind == "Component Manifest" else {"purpose": body[("claim", "purpose")]})
        instance = self.validate(kind, {"CONTAINED_BY": [self.components[owner]]},
                                 peers=peers, atom_id=fields["atom_id"], ref_id=ref,
                                 version=fields["version"], tier=context["tier"],
                                 component_id=component, **properties)
        validate_manifest(instance.component_id, owner, instance.tier, {}, PROJECT, PARENTS)
        return instance, (group, ref)

    def test_current_manifest_purpose_and_history(self):
        current, current_ref = self.component_spec(self.manifest())
        self.assertIsInstance(current, self.types["Spec Atom"])
        self.assertEqual((current.atom_id, current.ref_id, current.component_id, current.name, current.layer),
                         ("AN-S-096", "AN-S-096@3", "C43", "Backend Deck", 2))
        purpose_file = self.write(
            SECTIONS["C20"] / "SPEC/AN-S-097-SPEC--state-backend-purpose.md", atom_id="AN-S-097",
            body="## Summary\n\nState Backend Purpose\n\n## Claim\n\n### Component ID\n\nC43\n\n"
                 "### Purpose\n\nProvide synchronous read and write access.\n",
        )
        purpose, _ = self.component_spec(purpose_file, "Component Purpose")
        self.assertEqual((purpose.component_id, purpose.tier), (current.component_id, current.tier))

        draft = self.manifest(SECTIONS["C20"] / "draft/AN-S-096@2-draft--declare-backend-deck.md",
                              version=2, status="draft")
        archive = self.manifest(SECTIONS["C20"] / "archived/AN-S-096@2--declare-backend-deck.md",
                                version=2, status="archived")
        draft_instance, draft_ref = self.component_spec(draft, peers=[current])
        _, archive_ref = self.component_spec(archive, peers=[current, draft_instance])
        revisions = [current_ref, draft_ref, archive_ref]
        for reference, expected in (
            ("AN-S-096", ("Current", "AN-S-096@3")), ("AN-S-096@3", ("Current", "AN-S-096@3")),
            ("AN-S-096@2-draft", ("Draft", "AN-S-096@2-draft")), ("AN-S-096@2", ("Archived", "AN-S-096@2")),
            ("AN-S-096@3-draft", None),
        ):
            self.assertEqual(select_revision(reference, revisions), expected)

    def test_wrong_group_qualifier_and_unicode_id(self):
        for relative, status, violation in (
            ("AN-S-096@2-draft--declare-backend-deck.md", "draft", "Status group"),
            ("draft/AN-S-096@2--declare-backend-deck.md", "draft", "exact reference disagrees"),
            ("archived/AN-S-096@2-draft--declare-backend-deck.md", "archived", "exact reference disagrees"),
        ):
            with self.subTest(relative=relative), self.assertRaisesRegex(ValueError, violation):
                self.component_spec(self.manifest(SECTIONS["C20"] / relative, status=status, version=2))
        with self.assertRaisesRegex(ValueError, "Invalid stable Atom ID"):
            self.component_spec(self.manifest(atom_id="AN-S-０９６"))

    def test_wrong_parent_spec_section_and_tier(self):
        for owner in ("C44", "C43"):
            with self.subTest(owner=owner), self.assertRaisesRegex(ValueError, "belongs to its parent"):
                self.component_spec(self.manifest(SECTIONS[owner] / "SPEC" / MANIFEST_FILENAME,
                                                  owner=owner))
        with self.assertRaisesRegex(ValueError, "Physical carrier directory"):
            self.component_spec(self.manifest(owner="C404"))
        with self.assertRaisesRegex(ValueError, "belongs to its parent"):
            self.component_spec(self.manifest(component="C404"))
        with self.assertRaisesRegex(ValueError, "Component ID is missing"):
            self.component_spec(self.manifest(component=None))
        with self.assertRaisesRegex(ValueError, "Physical carrier directory"):
            self.component_spec(self.manifest(SECTIONS["C44"] / "SPEC" / MANIFEST_FILENAME))
        with self.assertRaisesRegex(ValueError, "tier: value must be one of 0"):
            self.component_spec(self.manifest(tier=1))

    def test_local_extension_requires_a_pmeta_carrier_in_the_selected_project(self):
        local_root = self.workspace / "local"
        relative = Path(".anechoic_local/_PMETA/LOCAL-P-17--declare-review-component.md")
        body = """## Summary

Declare Review Component

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Component

class ReviewComponent(Component):
    pass

declare_entity(entity_name="Review Component", entity_class=ReviewComponent)
```
"""

        def local_declaration(path):
            context, _, fields, (_, ref), markdown = read_review_carrier(path, local_root, "local", "LOCAL")
            self.assertEqual(context["container"], {"component": PROJECT})
            self.validate("PMETA Atom", {"CONTAINED_BY": [self.components[PROJECT]]},
                          atom_id=fields["atom_id"], ref_id=ref, version=fields["version"])
            (language, claim), = tuple(formal_claim_fences(markdown))
            self.assertEqual(language, "python")
            return ref, "MODEL//LOCAL <+ Node//Artifact//Component//Review Component", claim

        outside = self.write(relative, body, root=self.workspace / "foreign", atom_id="LOCAL-P-17", owner=PROJECT)
        with self.assertRaisesRegex(ValueError, "outside the selected Project root"):
            local_declaration(outside)
        in_spec = self.write(relative.parent.parent / relative.name, body, root=local_root, atom_id="LOCAL-P-17", owner=PROJECT)
        with self.assertRaisesRegex(ValueError, "logical Project tree"):
            local_declaration(in_spec)
        as_spec = self.write(
            relative.parent.parent / "SPEC/LOCAL-S-17-SPEC--declare-review-component.md",
            body, root=local_root, atom_id="LOCAL-S-17", owner=PROJECT,
        )
        with self.assertRaisesRegex(ValueError, "check_atom_identity"):
            local_declaration(as_spec)
        in_pmeta = self.write(relative, body, root=local_root, atom_id="LOCAL-P-17", owner=PROJECT)
        extension = local_declaration(in_pmeta)
        self.assertEqual(extension[0], "LOCAL-P-17@3")
        local_types, validate_local = model_validator(
            [*self.records, extension], "_anechoic_carrier_local_review", self.addCleanup,
        )
        parent = validate_local("Project")
        component = validate_local("Review Component", {"CHILD_OF": [parent]})
        self.assertIsInstance(component, local_types["Component"])
        self.assertNotIn("Review Component", self.types)
        self.assertEqual(self.components[PROJECT], self.validate("Project"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
