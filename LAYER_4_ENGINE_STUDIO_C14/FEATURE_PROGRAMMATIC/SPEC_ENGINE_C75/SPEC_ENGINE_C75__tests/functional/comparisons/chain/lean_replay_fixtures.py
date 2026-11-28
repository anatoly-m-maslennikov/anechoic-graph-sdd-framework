import hashlib
import json
from copy import deepcopy

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75 import formal_chain__pub as chain
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_1_SOURCE_ADAPTERS_C95.\
    _package__shared import read_source  # fmt: skip

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.\
    LAYER_3_LEAN_TRANSLATOR_C84._package__shared import (
    run_lean_json,
)  # fmt: skip


def assert_observations(self, evidence, stages, claims):
    def digest(value):
        encoded = json.dumps(
            value,
            sort_keys=True,
            allow_nan=False,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    self.assertEqual(digest(claims), evidence["model_pin"])
    self.assertEqual(evidence["model_pin"], stages["generated_claims"])
    self.assertEqual(evidence["model_pin"], stages["lean_claims"])
    self.assertEqual(
        {
            "claims_pin": evidence["model_pin"],
            "action": None,
            "kind": "trace",
        },
        stages["comparison"],
    )
    self.assertEqual(
        digest(claims["solution"]), stages["rendering"]["solution_pin"]
    )


def comparison_mutations():
    render = chain.render_solution
    compare = chain.compare_trace_spec

    def other_action(model, claim, **options):
        return render(model, claim, **{**options, "action": "audit"})

    def changed_claim(model, canonical, **options):
        canonical["claims"]["solution"]["changed"] = True
        return compare(model, canonical, **options)

    def substituted_claim(model, canonical, **options):
        other = deepcopy(canonical)
        other["claims"]["solution"] = {}
        return compare(model, other, **options)

    def substituted_action(model, canonical, **options):
        return compare(model, canonical, **{**options, "action": "audit"})

    def changed_source(model, canonical, **options):
        result = compare(model, canonical, **options)
        result["sources"]["solution"] = {
            **result["sources"]["solution"],
            "sha256": "f" * 64,
        }
        return result

    def changed_diagram(model, canonical, **options):
        return {
            **compare(model, canonical, **options),
            "mermaid": "flowchart TD\n  x --> y",
        }

    return (
        ("render_solution", other_action, "Rendering Action differs"),
        ("compare_trace_spec", changed_claim, "Comparison Model"),
        ("compare_trace_spec", substituted_claim, "Comparison Model"),
        ("compare_trace_spec", substituted_action, "Comparison Model"),
        ("compare_trace_spec", changed_source, "Comparison source"),
        ("compare_trace_spec", changed_diagram, "Comparison diagram"),
    )


FAILURE_PIN = {
    "path": (
        "_anechoic_anechoic/LAYER_4_ENGINE_STUDIO_C14/"
        "FEATURE_PROGRAMMATIC_C15/01_draft/"
        "AN-S-5072@2-draft-SWCS-STANDARD--report-"
        "programmatic-operation-failures-explicitly.md"
    ),
    "atom_id": "AN-S-5072",
    "version": 2,
    "status": "draft",
    "container_component": "C15",
    "sha256": (
        "90858185dfdf80f16af951c5dfc6e699bb896deb46fc50a9ae49973bdf6f489b"
    ),
}


def default_failure_standard(self, root):
    pin = FAILURE_PIN
    standard, pinned = read_source(root, pin, "standard")
    self.assertEqual(pin, pinned)
    specs = root / "_anechoic_anechoic"
    owners = {}
    for component, atom, version, parent in (
        ("C75", "AN-S-3395", 8, "C15"),
        ("C94", "AN-S-5020", 5, "C75"),
        ("C95", "AN-S-5021", 3, "C75"),
    ):
        (path,) = specs.rglob(f"{atom}-SPEC-COMPONENT_MANIFEST--*.md")
        owner_pin = {
            "path": path.relative_to(root).as_posix(),
            "atom_id": atom,
            "version": version,
            "status": "active",
            "container_component": parent,
        }
        carrier, _ = read_source(root, owner_pin, "manifest")
        self.assertIn(f"component_id='{component}'", carrier.body)
        owners[component] = carrier.metadata["container"]["component"]
    self.assertEqual(
        {"C75": pin["container_component"], "C94": "C75", "C95": "C75"},
        owners,
    )
    self.assertIn(
        "Apply this Standard by default to Programmatic public operations",
        standard.body,
    )
    return standard


def assert_replay(self, evidence, expected, root, lean):
    for item in (
        evidence["validation_programs"] + evidence["comparison_programs"]
    ):
        self.assertEqual(
            json.loads(item["stdout"]),
            run_lean_json(item["program"], lean),
        )
    self.assertEqual(
        expected,
        next(
            f["status"]
            for f in evidence["coverage"]
            if f.get("key") == "must_effect"
        ),
    )
    self.assertEqual(
        {"python", "cfel"},
        {f["output"] for f in evidence["coverage"] if "output" in f},
    )
    for role, source in evidence["sources"].items():
        self.assertEqual(
            hashlib.sha256((root / source["path"]).read_bytes()).hexdigest(),
            source["sha256"],
            role,
        )
