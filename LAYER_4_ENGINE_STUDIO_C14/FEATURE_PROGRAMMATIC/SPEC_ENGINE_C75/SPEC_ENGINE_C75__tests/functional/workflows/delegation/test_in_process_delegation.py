import os
import shutil
import tempfile
import unittest
from pathlib import Path

# fmt: off
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.\
    LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_4_SPEC_COMPARISON_C88.\
    DELEGATION_VERIFICATION_C89._package__shared import (
    check_sibling_binding,
)
# fmt: on
# fmt: off
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.SPEC_ENGINE_C75__tests.\
    functional.contracts.cli.test_cli_spec import (
    _carrier,
)
# fmt: on


MANIFEST = """## Formal Manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest
declare_entity(entity_name='Component Manifest', instance=ComponentManifest(
    component_id={component!r}, name='Example', boundaries={{'io': {io!r}}}))
```
"""
CONTRACT = """## Claim

### Formal Claim

```python trace
declare_trace_contract(action='run', output='ready', must_effect=(('C3\
', 'called'),){binding})
```
"""
SOLUTION = """## Claim

### Formal Claim

```python
component_workflow(component={component!r}, action='run', machine={{
    'id': 'run', 'initial': 'start', 'states': {{
        'start': {{'on': {{'start': {{'target': 'running', 'guard': {{\
'type': 'matchesTrace',
            'params': {trigger!r}}}}}}}}},
        'running': {{'on': {{'invoke': {{'target': 'returning', 'guard\
': {{'type': 'matchesTrace',
            'params': {effect!r}}}}}}}}},
        'returning': {{'on': {{'return': {{'target': 'done', 'guard': \
{{'type': 'matchesTrace',
            'params': {{'kind': 'output', 'outcome': 'ready'}}}}}}}}}},
        'done': {{'type': 'final'}}}}}})
```
"""
BINDING = {"transport": "in_process", "entry": "Orchestrator.run_worker"}
INTERFACE = "compiler_worker"


def carriers(root, component, offset, io, trigger, effect, binding=""):
    manifest, contract, solution = (f"AN-S-{offset + n}" for n in range(3))
    return (
        _carrier(
            root,
            manifest,
            "component_manifest",
            "C1",
            "{}",
            MANIFEST.format(component=component, io=io),
        ),
        _carrier(
            root,
            contract,
            "component_contract",
            component,
            f"{{ANSWERS: [{manifest}]}}",
            CONTRACT.format(binding=binding),
        ),
        _carrier(
            root,
            solution,
            "decision",
            component,
            f"{{IS_SOLUTION_FOR: [{contract}@1]}}",
            SOLUTION.format(
                component=component, trigger=trigger, effect=effect
            ),
        ),
    )


class InProcessDelegationTests(unittest.TestCase):
    def setUp(self):
        self.lean = os.environ.get("ANECHOIC_TEST_LEAN") or shutil.which(
            "lean"
        )
        if not self.lean:
            self.skipTest("Lean executable unavailable")
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        caller_effect = {
            "kind": "effect",
            "target": "C3",
            "outcome": "called",
            "detail": {"interface": INTERFACE, **BINDING},
        }
        self.caller = carriers(
            self.root,
            "C2",
            1,
            {"client": [{"component": "C3", "interface": INTERFACE}]},
            {"kind": "trigger", "target": "caller"},
            caller_effect,
        )
        self.provider = carriers(
            self.root,
            "C3",
            4,
            {"server": {INTERFACE: BINDING}},
            {"kind": "trigger", "target": INTERFACE, "detail": BINDING},
            {"kind": "effect", "target": "C3", "outcome": "called"},
            ", interface='compiler_worker', transport='in_process', "
            "entry='Orchestrator.run_worker'",
        )

    def check(self):
        return check_sibling_binding(
            self.root,
            self.caller,
            "C3",
            self.provider,
            event="invoke",
            interface=INTERFACE,
            lean=self.lean,
        )

    def statuses(self):
        return {
            name: direction["status"]
            for name, direction in self.check()["directions"].items()
        }

    def test_provider_declarations_match_and_solution_entry_conflicts(self):
        matched = {
            "caller_manifest": "matched",
            "caller_contract": "matched",
            "caller_solution": "matched",
        }
        self.assertEqual(matched, self.statuses())
        path = self.root / self.provider[2]["path"]
        path.write_text(
            path.read_text().replace(
                "Orchestrator.run_worker", "Orchestrator.other"
            )
        )
        self.assertEqual(
            {**matched, "caller_solution": "conflicting"}, self.statuses()
        )

    def test_missing_caller_detail_is_unresolved(self):
        path = self.root / self.caller[2]["path"]
        path.write_text(
            path.read_text().replace("'interface': 'compiler_worker', ", "")
        )
        self.assertTrue(
            all(status == "unresolved" for status in self.statuses().values())
        )

    def test_rejects_non_sibling_and_undeclared_dependency(self):
        path = self.root / self.provider[0]["path"]
        original = path.read_text()
        path.write_text(
            original.replace(
                "container: {component: C1}", "container: {component: C9}"
            )
        )
        self.provider[0]["container_component"] = "C9"
        with self.assertRaises(ValueError):
            self.check()
        path.write_text(original)
        self.provider[0]["container_component"] = "C1"
        path = self.root / self.caller[0]["path"]
        path.write_text(
            path.read_text().replace("'component': 'C3'", "'component': 'C4'")
        )
        with self.assertRaises(ValueError):
            self.check()


from ._http_sibling_binding_cases import (  # noqa: E402
    HttpSiblingBindingTests as HttpSiblingBindingTests,
)
