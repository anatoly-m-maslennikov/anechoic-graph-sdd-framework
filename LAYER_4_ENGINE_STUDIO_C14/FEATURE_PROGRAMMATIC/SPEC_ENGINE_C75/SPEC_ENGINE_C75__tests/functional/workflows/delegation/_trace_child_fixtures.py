from ...contracts.cli.test_cli_spec import _carrier


MANIFEST = """## Formal Manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest
declare_entity(entity_name='Component Manifest', instance=ComponentManifest(
    component_id='C2', name='Renderer', boundaries={'io': {'server': {\
'render': {
        'outcomes': {'succeeded': {'must_effect': [('workbench_display\
', 'shown')]}}}}}}))
```
"""
CONTRACT = """## Claim

### Formal Claim

```python trace
declare_trace_contract(action='render', output='succeeded',
                       must_effect=(('workbench_display', 'shown'),))
```
"""
PARENT = """## Claim

### Formal Claim

```python
component_workflow(component='C1', action='run', machine={
    'id': 'run', 'initial': 'start', 'states': {
        'start': {'on': {'render': {'target': 'done', 'guard': {'type'\
: 'matchesTrace',
            'params': {'kind': 'effect', 'target': 'workbench_display'\
, 'outcome': 'shown',
                       'detail': {'component': 'C2', 'action': 'render\
', 'output': 'succeeded'}}}}}},
        'done': {'type': 'final'}}})
```
"""
SOLUTION = """## Claim

### Formal Claim

```python
component_workflow(component='C2', action='render', machine={
    'id': 'render', 'initial': 'start', 'states': {
        'start': {'on': {'show': {'target': 'shown', 'guard': {'type':\
 'matchesTrace',
            'params': {'kind': 'effect', 'target': 'workbench_display'\
, 'outcome': 'shown'}}}}},
        'shown': {'on': {'return': {'target': 'done', 'guard': {'type'\
: 'matchesTrace',
            'params': {'kind': 'output', 'outcome': 'succeeded'}}}}},
        'done': {'type': 'final'}}})
```
"""


def pins(root):
    parent = _carrier(root, "AN-S-4", "decision", "C1", "{}", PARENT)
    child = (
        _carrier(root, "AN-S-1", "component_manifest", "C1", "{}", MANIFEST),
        _carrier(
            root,
            "AN-S-2",
            "component_contract",
            "C2",
            "{ANSWERS: [AN-S-1]}",
            CONTRACT,
        ),
        _carrier(
            root,
            "AN-S-3",
            "decision",
            "C2",
            "{IS_SOLUTION_FOR: [AN-S-2@1]}",
            SOLUTION,
        ),
    )
    return parent, child
