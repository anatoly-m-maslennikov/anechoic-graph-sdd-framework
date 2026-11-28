"""Fixtures for verified model functional tests."""

from hashlib import sha256
from importlib import import_module
import json

_adapters = import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared"
)
canonical_native_header = _adapters.canonical_native_header

PROBE_STATUS = (
    "---\n"
    "atom_family: PROJECT_CONFIG\n"
    "atom_id: AN-C-99992\n"
    "container:\n"
    "  component: C00\n"
    "context:\n"
    "  template: manifest_property\n"
    "state:\n"
    "  status: active\n"
    "  version: 1\n"
    "  updated_at: '2026-11-27T00:00:00Z'\n"
    "concern:\n"
    "  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Co"
    "ntent/Atom//Specification//Probe.Header.State\n"
    "  relation: is_property_of\n"
    "  subject: Status\n"
    "---\n"
    "\n"
    "## Summary\n"
    "\n"
    "Declare Probe Status\n"
    "\n"
    "## Formal Manifest\n"
    "\n"
    "```python anechoic-edsl\n"
    "from anechoic.model import Atom, Property, Probe\n"
    "\n"
    "class ProbeStatus(Property):\n"
    "    name = 'Status'\n"
    "    bearer = Atom.Header.State\n"
    "    property.applies_to = (Probe,)\n"
    "    property.value.allowed = ('draft', 'ready', 'active"
    "', 'archived', 'reviewed')\n"
    "```\n"
)


def probe_variant(custom):
    variant = next((custom).glob("AN-C-3194-*.md")).read_text()
    variant = (
        variant.replace("AN-C-3194", "AN-C-99991")
        .replace("Axiom", "Probe")
        .replace("axiom", "probe")
    )
    variant = variant.replace(
        "relations:\n  IS_REPLACEMENT_FOR:\n  - AN-C-3193\n", ""
    )
    return variant


def extension_fixture(custom):
    variant = probe_variant(custom)
    variant = variant.replace(
        "node.tier = value(fixed=0)", "node.tier = value(default=0)"
    )
    node = custom / "AN-C-99991-MANIFEST_NODE--declare-probe.md"
    node.write_text(variant, encoding="utf-8")
    status = custom / "AN-C-99992-MANIFEST_PROPERTY--declare-probe-status.md"
    status.write_text(PROBE_STATUS, encoding="utf-8")
    current = custom / "AN-C-99993-MANIFEST_PROPERTY--extend-ticket-status.md"
    extension = (
        status.read_text()
        .replace("AN-C-99992", "AN-C-99993")
        .replace(
            "//Specification//Probe.Header.State",
            "//Ticket.Header.State",
        )
        .replace("Probe", "TicketAtom")
        .replace(
            "('draft', 'ready', 'active', 'archived', 'reviewed')",
            "('triage',)",
        )
    )
    current.write_text(extension, encoding="utf-8")
    return variant, node, current, extension


def contract_fixture(custom):
    variant = probe_variant(custom)
    variant = variant.replace(
        "//Specification//.Header.Context",
        "//Specification//Contract//Project Contract//.Header.Context",
    )
    variant = variant.replace(
        "Lens, Project, SpecAtom", "Lens, ProjectContract"
    )
    variant = variant.replace(
        "class Probe(SpecAtom):", "class Probe(ProjectContract):"
    )
    variant = variant.replace(
        "    node.container_type = value(fixed=Project)\n", ""
    )
    variant = variant.replace(
        "    node.tier =",
        "    node.creation_enabled = value(fixed=False)\n    node.tier =",
    )
    (custom / "AN-C-99991-MANIFEST_NODE--declare-probe.md").write_text(variant)


def contract_header():
    header = canonical_native_header(
        {
            "identity": {"atom_id": "AN-S-99991"},
            "context": {
                "container": {"component": "C00"},
                "tier": 0,
                "template": "probe",
                "lens": "SPEC",
            },
            "state": {
                "status": "draft",
                "version": 1,
                "updated_at": "2026-11-27T00:00:00+00:00",
            },
        }
    )
    body = (
        "\n## Summary\n\nProbe\n\n## Guarantee\n\n"
        "The Project records the decision.\n"
    )
    return header, body


HEADER_CHECKS = (
    "\n"
    'def atomRoot := "Graph/Node//Artifact//SSOT//Prescribed'
    '/Content/Atom"\n'
    'def specRoot := atomRoot ++ "//Specification"\n'
    'def ticketRoot := atomRoot ++ "//Ticket"\n'
    'def header : AtomHeader := ⟨"SPEC", specRoot ++ "//Axio'
    'm", some (.text "active"), some (.integer 0), none⟩\n'
    "example : atomHeaderValid header = true := by decide\n"
    "example : atomHeaderValid {header with modelClass := sp"
    "ecRoot, tier := some (.integer 1)} = true := by decide\n"
    "example : atomHeaderValid {header with status := none} "
    "= false := by decide\n"
    "example : atomHeaderValid {header with status := some ."
    "other} = false := by decide\n"
    "example : atomHeaderValid {header with tier := none} = "
    "false := by decide\n"
    "example : atomHeaderValid {header with tier := some (.i"
    "nteger 1)} = false := by decide\n"
    'example : atomHeaderValid {header with family := "TKT",'
    " priority := none} = false := by decide\n"
    'example : atomHeaderValid {header with family := "TKT",'
    " priority := some (.integer 2)} = false := by decide\n"
    "example : atomHeaderValid {header with modelClass := sp"
    'ecRoot ++ "//Unknown"} = false := by decide\n'
    'example : atomHeaderValid {header with family := "TKT",'
    " modelClass := ticketRoot, priority := some (.integer 2"
    ")} = false := by decide\n"
    'def ticket : AtomHeader := ⟨"TKT", ticketRoot, some (.t'
    'ext "in_queue"), none, some (.integer 2)⟩\n'
    "example : atomHeaderValid ticket = true := by decide\n"
    "example : atomHeaderValid {ticket with priority := none"
    "} = false := by decide\n"
    "example : atomHeaderValid {ticket with status := some ("
    '.text "backlog")} = true := by decide\n'
    "example : atomHeaderValid {ticket with status := some ("
    '.text "draft")} = true := by decide\n'
    "example : atomHeaderValid {ticket with status := some ("
    '.text "archived")} = true := by decide\n'
    "example : atomHeaderValid {ticket with status := some ("
    '.text "ready")} = false := by decide\n'
    "example : atomHeaderValid {header with status := some ("
    '.text "backlog")} = false := by decide\n'
    "example : atomHeaderValid {header with status := some ("
    '.text "unknown")} = false := by decide\n'
    "example : atomHeaderValid {ticket with status := some ("
    '.text "unknown")} = false := by decide\n'
    'def config : AtomHeader := ⟨"PROJECT_CONFIG", atomRoot '
    '++ "//project_config", some (.text "active"), none, non'
    "e⟩\n"
    "example : atomHeaderStatusValid config = true := by dec"
    "ide\n"
    "example : atomHeaderStatusValid {config with status := "
    'some (.text "draft")} = true := by decide\n'
    "example : atomHeaderStatusValid {config with status := "
    'some (.text "archived")} = true := by decide\n'
    "example : atomHeaderStatusValid {config with status := "
    'some (.text "ready")} = false := by decide\n'
    "example : atomHeaderStatusValid {config with status := "
    'some (.text "unknown")} = false := by decide\n'
    'example : atomHeaderValid {header with family := "OTHER'
    '"} = false := by decide\n'
)


def assert_project_extension(self, stage, fingerprint, accepted, open_model):
    declarations = json.loads(accepted)["bindings"]["declarations"]
    (groups,) = (
        args["status_groups"]
        for _, declaration in declarations
        if "triage"
        in (args := declaration["arguments"]).get("allowed_values", ())
    )
    self.assertEqual("Current", groups["triage"])
    with open_model(stage, fingerprint, sha256(accepted).hexdigest()) as model:
        types = {cls.__name__: cls for cls in model._types.values()}
        probe = types["Probe"].__dataclass_fields__
        previous = types["Axiom"].__dataclass_fields__
        self.assertEqual(
            ("probe",), probe["template"].metadata["allowed_values"]
        )
        self.assertEqual(0, probe["tier"].default)
        self.assertEqual((0, True), model.project_spec_template("probe")[1:])
        self.assertIn("reviewed", probe["status"].metadata["allowed_values"])
        self.assertEqual(
            ("axiom",), previous["template"].metadata["allowed_values"]
        )
        self.assertNotIn(
            "reviewed", previous["status"].metadata["allowed_values"]
        )
        ticket = (
            types["TicketAtom"]
            .__dataclass_fields__["status"]
            .metadata["allowed_values"]
        )
        self.assertTrue(
            {"draft", "backlog", "in_queue", "triage", "archived"}
            <= set(ticket)
        )
