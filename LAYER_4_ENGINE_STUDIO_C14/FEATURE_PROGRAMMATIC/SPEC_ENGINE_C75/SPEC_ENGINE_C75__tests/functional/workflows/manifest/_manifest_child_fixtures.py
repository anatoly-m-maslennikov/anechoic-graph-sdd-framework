from ...contracts.cli.test_cli_spec import _CONTRACT, _carrier


def _set_tier(root, pin, tier, previous):
    path = root / pin["path"]
    path.write_text(
        path.read_text().replace(f"tier: {previous}", f"tier: {tier}")
    )
    return pin


def _manifest(root, atom, owner, component, contract, boundaries=None):
    fence = contract[contract.index("```") :]
    body = f"""## Summary

Declare the Component.

## Purpose

Model one public Action.

## Component Identity

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest
declare_entity(entity_name='Component Manifest', instance=ComponentManifest(
    component_id='{component}', name='Example'))
```

## Component Boundaries

```python
{boundaries or {}!r}
```

## Component Contract

{fence}"""
    return _set_tier(
        root,
        _carrier(root, atom, "component_manifest", owner, "{}", body),
        1,
        4,
    )


def _cli_child(self):
    child = _manifest(
        self.root,
        "AN-S-2",
        "C1",
        "C2",
        _CONTRACT.replace(
            "runner='uv', path='suite.py'",
            "command='local', arguments=('--name', '<value>')",
        ),
        {
            "io": {
                "server": {
                    "suite": {
                        "transport": "cli",
                        "runner": "uv",
                        "path": "suite.py",
                    }
                }
            }
        },
    )
    return child
