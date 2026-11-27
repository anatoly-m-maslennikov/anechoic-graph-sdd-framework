import hashlib
import shutil
import tempfile
from pathlib import Path
from unittest.mock import NonCallableMock

from ....FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    native_header_view,
)
from ....FEATURE_TOOLS.ADAPTERS_C30.carrier_read__pub import (
    parse_carrier,
)

ROOT = Path(__file__).resolve().parents[5]
CONTROL = ROOT / "_anechoic_anechoic"
if (ROOT.parent / "native-control").is_dir():
    CONTROL = ROOT.parent / "native-control"
PROJECT = ROOT / "AN-S-3037-SPEC-PROJECT_MANIFEST--declare-anechoic.md"
COMPONENT = CONTROL / (
    "01_TIER_1_ARCHITECTURE/"
    "AN-S-3039-SPEC-COMPONENT_MANIFEST--declare-engine-studio.md"
)

LEGACY_COMPONENT = """---
atom_family: SPEC
atom_id: AN-S-3039
container:
  component: C00
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: active
  version: 4
  updated_at: '2026-11-23T13:46:18.273025+00:00'
---

## Summary

Declare Engine Studio

## Purpose

Consume Environments. DevOps builds Engine Studio.

This Component delegates implementation to its child Components.

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C14',
        name='Engine Studio',
        layer=4,
        lens_whitelist=['DES', 'DevOps', 'QA', 'SPEC', 'SWD'],
        boundaries={'code': {'imports': [], 'exports': {}}},
    ),
)
```
"""


def selection(control, project=None):
    if project is None:
        project = PROJECT if control == CONTROL else control / PROJECT.name
    raw = project.read_bytes()
    meta = native_header_view(parse_carrier(raw, project).metadata)
    ref = f"{meta['identity']['atom_id']}@{meta['state']['version']}"
    return NonCallableMock(
        spec_set=[
            "control_root",
            "manifest_path",
            "manifest_ref",
            "manifest_sha256",
        ],
        control_root=control,
        manifest_path=project,
        manifest_ref=ref,
        manifest_sha256=hashlib.sha256(raw).hexdigest(),
    )


class Model:
    fingerprint = "model-fingerprint"
    requires_atom_state = False

    def validate_manifest(self, fields, parent_id):
        assert fields["name"] and fields["prefix"] and parent_id == "C00"

    def validate_component_manifest(self, fields, parent_id):
        assert fields["component_id"] and parent_id

    def validate_component_seed_manifest(self, fields, parent_id):
        assert fields["component_seed_id"] and parent_id


CANONICAL_BODY = (
    """## Summary

Declare Engine Studio

## Purpose

Provide the engine.

## Component Identity

```python
from anechoic.model import ComponentManifest
"""
    + "ComponentManifest(component_id='C14', name='Engine Studio', "
    + "lens_whitelist=['SPEC'])"
    + """
```

## Component Boundaries

```python
{'code': {'imports': ['C30']}}
```

## Component Contract

```python contract
declare_contract()
```
"""
)


class StructureFixture:
    def _standalone_project(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        control, project = root / "control", root / PROJECT.name
        (control / "_SPEC").mkdir(parents=True)
        shutil.copyfile(PROJECT, project)
        return control, selection(control, project)
