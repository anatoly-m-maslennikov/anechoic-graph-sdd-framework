---
atom_family: PROJECT_CONFIG
atom_id: AN-C-1
container: {component: C00}
context: {template: model_manifest}
state: {version: 1, status: active, updated_at: '2026-11-23T00:00:00Z'}
---

## Summary

Declare the reviewed Model for the lifecycle latency fixture.

## Semantics

Use the reviewed Model declarations for the image test.

## Formal Manifest

### Declaration 1

MODEL//ANECHOIC <+ Model

```python
from anechoic.formal_claims import declare_entity

class Model:
    pass

declare_entity(entity_name="Model", entity_class=Model)
```

### Declaration 2

MODEL//ANECHOIC <+ Graph

```python
from anechoic.formal_claims import declare_entity

class Graph:
    pass

declare_entity(entity_name="Graph", entity_class=Graph)
```

### Declaration 3

MODEL//ANECHOIC <+ Node

```python
from anechoic.formal_claims import declare_entity

class Node:
    pass

declare_entity(entity_name="Node", entity_class=Node)
```

### Declaration 4

MODEL//ANECHOIC <+ Graph/Relation

```python
from anechoic.formal_claims import declare_entity

class Relation:
    pass

declare_entity(entity_name="Relation", entity_class=Relation)
```

### Declaration 5

MODEL//ANECHOIC <+ eDSL

```python
from anechoic.formal_claims import declare_entity

class EDSL:
    pass

declare_entity(entity_name="eDSL", entity_class=EDSL)
```

### Declaration 6

MODEL//ANECHOIC <+ Carrier

```python
from anechoic.formal_claims import declare_entity

class Carrier:
    pass

declare_entity(entity_name="Carrier", entity_class=Carrier)
```

### Declaration 7

MODEL//ANECHOIC <+ eDSL/Format

```python
from anechoic.formal_claims import declare_entity

class Format:
    pass

declare_entity(entity_name="Format", entity_class=Format)
```

### Declaration 8

MODEL//ANECHOIC <+ eDSL/Cardinality

```python
from anechoic.formal_claims import declare_entity

class Cardinality:
    pass

declare_entity(entity_name="Cardinality", entity_class=Cardinality)
```

### Declaration 9

MODEL//ANECHOIC <+ View

```python
from anechoic.formal_claims import declare_entity

class View:
    pass

declare_entity(entity_name="View", entity_class=View)
```

### Declaration 10

MODEL//ANECHOIC <+ Node//Artifact

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Node

class Artifact(Node):
    pass

declare_entity(entity_name="Artifact", entity_class=Artifact)
```

### Declaration 11

MODEL//ANECHOIC <+ Node//Ephemeral

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Node

class Ephemeral(Node):
    pass

declare_entity(entity_name="Ephemeral", entity_class=Ephemeral)
```

### Declaration 12

MODEL//ANECHOIC <+ Node//Artifact//Atom

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Artifact
from dataclasses import field
from typing import ClassVar

class Atom(Artifact):
    atom_id: str
    version: int = field(metadata={"minimum_value": 1})
    ref_id: str
    family_marker: ClassVar[str | None] = None

def check_atom_identity(atom: Atom) -> bool:
    parts = atom.atom_id.split("-")
    if len(parts) != 3:
        return False
    prefix, family, number = parts
    if not (prefix.isascii() and prefix.isalpha() and prefix.isupper()
            and (family == atom.family_marker or (atom.family_marker == 'C' and family == 'P'))
            and number.isascii() and number.isdecimal()):
        return False
    revision = f"{atom.atom_id}@{atom.version}"
    return atom.ref_id in (revision, f"{revision}-draft")

declare_entity(
    entity_name="Atom",
    entity_class=Atom,
    instance_check=check_atom_identity,
    instance_relation_constraints={
        "CONTAINED_BY": {"target_entity_paths": ("Node//Artifact//Component", "Node//Artifact//Atom"), "targets_per_source": 1},
    },
    population_unique_constraints=({"keys": ("Ref ID",)},),
)
```

### Declaration 13

MODEL//ANECHOIC <+ Node//Artifact//Atom//Spec Atom

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Atom
from typing import ClassVar

class SpecAtom(Atom):
    family_marker: ClassVar[str] = "S"

declare_entity(entity_name="Spec Atom", entity_class=SpecAtom)
```

### Declaration 14

MODEL//ANECHOIC <+ Node//Artifact//Atom//Ticket Atom

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Atom
from typing import ClassVar

class TicketAtom(Atom):
    family_marker: ClassVar[str] = "T"

declare_entity(entity_name="Ticket Atom", entity_class=TicketAtom)
```

### Declaration 15

MODEL//ANECHOIC <+ Node//Artifact//Atom//Project Config Atom

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Atom
from typing import ClassVar

class ProjectConfigAtom(Atom):
    family_marker: ClassVar[str] = "C"

declare_entity(entity_name="Project Config Atom", entity_class=ProjectConfigAtom)
```

### Declaration 16

MODEL//ANECHOIC <+ Node//Artifact//Event Record

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Artifact

class EventRecord(Artifact):
    pass

declare_entity(entity_name="Event Record", entity_class=EventRecord)
```

### Declaration 17

MODEL//ANECHOIC <+ Node//Artifact//Component

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Artifact

class Component(Artifact):
    pass

declare_entity(entity_name="Component", entity_class=Component,
    instance_relation_constraints={
        "CHILD_OF": {"target_entity_paths": ("Node//Artifact//Component",), "targets_per_source": 1},
    },
)
```

### Declaration 18

MODEL//ANECHOIC <+ Node//Artifact//Component//Project

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Component

class Project(Component):
    pass

declare_entity(entity_name="Project", entity_class=Project,
    instance_relation_constraints={"CHILD_OF": {"targets_per_source": 0}},
)
```

### Declaration 19

MODEL//ANECHOIC <+ Component/Component Spec Section

```python
from anechoic.formal_claims import declare_entity

class ComponentSpecSection:
    pass

declare_entity(entity_name="Component Spec Section", entity_class=ComponentSpecSection)
```

### Declaration 20

MODEL//ANECHOIC <+ Node//Artifact//Package

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Artifact

class Package(Artifact):
    pass

declare_entity(entity_name="Package", entity_class=Package)
```

### Declaration 21

MODEL//ANECHOIC <+ Node//Artifact//Package//Component Package

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Package

class ComponentPackage(Package):
    pass

declare_entity(entity_name="Component Package", entity_class=ComponentPackage)
```

### Declaration 22

MODEL//ANECHOIC <+ Package/Module

```python
from anechoic.formal_claims import declare_entity

class Module:
    pass

declare_entity(entity_name="Module", entity_class=Module)
```

### Declaration 23

MODEL//ANECHOIC <+ Module/Unit

```python
from anechoic.formal_claims import declare_entity

class Unit:
    pass

declare_entity(entity_name="Unit", entity_class=Unit)
```

### Declaration 24

MODEL//ANECHOIC <+ Continuant

```python
from anechoic.formal_claims import declare_entity

class Continuant:
    pass

declare_entity(entity_name="Continuant", entity_class=Continuant)
```

### Declaration 25

MODEL//ANECHOIC <+ Occurrent

```python
from anechoic.formal_claims import declare_entity

class Occurrent:
    pass

declare_entity(entity_name="Occurrent", entity_class=Occurrent)
```

### Declaration 26

MODEL//ANECHOIC <+ SSOT

```python
from anechoic.formal_claims import declare_entity

class SSOT:
    pass

declare_entity(entity_name="SSOT", entity_class=SSOT)
```

### Declaration 27

MODEL//ANECHOIC <+ Relation//CHILD_OF

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name="CHILD_OF",
    inverse_alias="CHILDREN",
    source_endpoint={"level": "instances", "entity_paths": ("Node//Artifact//Component",)},
    target_endpoint={"level": "instances", "entity_paths": ("Node//Artifact//Component",)},
    acyclic=True,
)
```

### Declaration 28

MODEL//ANECHOIC <+ Relation//CONTAINED_BY

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name="CONTAINED_BY",
    inverse_alias="CONTAINS",
    reverse_written_alias="<+",
    endpoint_pairs=(
        {
            "source_endpoint": {"level": "model_entities", "entity_paths": ("Graph", "eDSL", "Carrier")},
            "target_endpoint": {"level": "model_entities", "entity_paths": ("Model",)},
        },
        {
            "source_endpoint": {"level": "model_entities", "entity_paths": ("Node", "Relation")},
            "target_endpoint": {"level": "model_entities", "entity_paths": ("Graph",)},
        },
        {
            "source_endpoint": {"level": "model_entities", "entity_paths": ("Format", "Cardinality")},
            "target_endpoint": {"level": "model_entities", "entity_paths": ("eDSL",)},
        },
        {
            "source_endpoint": {"entity_paths": ("Component Spec Section", "Node//Artifact//Package//Component Package")},
            "target_endpoint": {"entity_paths": ("Node//Artifact//Component",)},
        },
        {
            "source_endpoint": {"entity_paths": ("Node//Artifact//Package", "Module")},
            "target_endpoint": {"entity_paths": ("Node//Artifact//Package",)},
        },
        {
            "source_endpoint": {"entity_paths": ("Unit",)},
            "target_endpoint": {"entity_paths": ("Module",)},
        },
        {
            "source_endpoint": {"level": "instances", "entity_paths": ("Node//Artifact//Atom",)},
            "target_endpoint": {"level": "instances", "entity_paths": ("Node//Artifact//Component", "Node//Artifact//Atom")},
        },
    ),
)
```

### Declaration 29

MODEL//ANECHOIC <+ Relation//IS_CLASSIFIED_BY

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name="IS_CLASSIFIED_BY",
    inverse_alias="CLASSIFIES",
    endpoint_pairs=(
        {
            "source_endpoint": {"level": "model_entities", "entity_paths": ("Node//Artifact//Atom//Spec Atom", "Node//Artifact//Atom//Project Config Atom")},
            "target_endpoint": {"level": "model_entities", "entity_paths": ("Continuant",)},
        },
        {
            "source_endpoint": {"level": "model_entities", "entity_paths": ("Node//Artifact//Atom//Ticket Atom",)},
            "target_endpoint": {"level": "model_entities", "entity_paths": ("Occurrent",)},
        },
        {
            "source_endpoint": {"level": "model_entities", "entity_paths": ("Node//Artifact//Atom//Spec Atom", "Node//Artifact//Event Record")},
            "target_endpoint": {"level": "model_entities", "entity_paths": ("SSOT",)},
        },
    ),
)
```

### Declaration 30

MODEL//ANECHOIC <+ Node//Artifact//Atom.Ref ID

```python
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name="Ref ID",
    relation_name="IS_PROPERTY_OF",
    base_path="Node//Artifact//Atom",
    value_format=str,
    value_cardinality=1,
)
```

### Declaration 31

MODEL//ANECHOIC <+ Relation//IS_PROPERTY_OF

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name="IS_PROPERTY_OF",
    source_endpoint={"level": "model_entities"},
    target_endpoint={"level": "model_entities"},
)
```

### Declaration 32

MODEL//ANECHOIC <+ Node//Artifact//Atom//Spec Atom//Manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import SpecAtom
from typing import ClassVar
from dataclasses import field

class Manifest(SpecAtom):
    control_flow: ClassVar[str] = "Declarative"
    lens_whitelist: list[str] | None = field(default=None, kw_only=True)

declare_entity(
    entity_name="Manifest",
    entity_class=Manifest,
)
```

### Declaration 33

MODEL//ANECHOIC <+ Node//Artifact//Atom//Spec Atom//Manifest//Project Manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Manifest
from dataclasses import field

class ProjectManifest(Manifest):
    tier: int = field(metadata={"allowed_values": (-1,)})
    name: str
    prefix: str
    parameters: dict[str, object] = field(default_factory=dict)

def check_project_manifest(manifest: ProjectManifest) -> bool:
    mcp = manifest.parameters.get("project_mcp", {})
    return bool(
        manifest.name.strip()
        and manifest.prefix.strip()
        and len(manifest.parameters) + 2 + (manifest.lens_whitelist is not None) <= 20
        and type(mcp) is dict
        and type(mcp.get("release_workflows_enabled", False)) is bool
    )

declare_entity(
    entity_name="Project Manifest",
    entity_class=ProjectManifest,
    instance_relation_constraints={
        "CONTAINED_BY": {"target_entity_paths": ("Node//Artifact//Component//Project",), "targets_per_source": 1},
    },
    instance_check=check_project_manifest,
)
```

### Declaration 34

MODEL//ANECHOIC <+ Node//Artifact//Atom//Spec Atom//Manifest//Component Manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Manifest
from dataclasses import field

class ComponentManifest(Manifest):
    tier: int = field(metadata={"allowed_values": (4,)})
    component_id: str
    name: str
    layer: int | None = None
    boundaries: dict[str, object] | None = None

def check_component_manifest(manifest: ComponentManifest) -> bool:
    return bool(manifest.component_id.strip() and manifest.name.strip())

declare_entity(
    entity_name="Component Manifest",
    entity_class=ComponentManifest,
    instance_relation_constraints={
        "CONTAINED_BY": {"target_entity_paths": ("Node//Artifact//Component",), "targets_per_source": 1},
    },
    instance_check=check_component_manifest,
)
```

### Declaration 35

MODEL//ANECHOIC <+ Node//Artifact//Atom//Spec Atom//Purpose

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import SpecAtom

class Purpose(SpecAtom):
    purpose: str

def check_purpose(purpose: Purpose) -> bool:
    return bool(purpose.purpose.strip())

declare_entity(
    entity_name="Purpose",
    entity_class=Purpose,
    instance_check=check_purpose,
)
```

### Declaration 36

MODEL//ANECHOIC <+ Node//Artifact//Atom//Spec Atom//Purpose//Project Goal

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Purpose
from dataclasses import field

class ProjectGoal(Purpose):
    tier: int = field(metadata={"allowed_values": (-1,)})

declare_entity(
    entity_name="Project Goal",
    entity_class=ProjectGoal,
    instance_relation_constraints={
        "CONTAINED_BY": {"target_entity_paths": ("Node//Artifact//Component//Project",), "targets_per_source": 1},
    },
)
```

### Declaration 37

MODEL//ANECHOIC <+ Node//Artifact//Atom//Spec Atom//Contract

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import SpecAtom

class Contract(SpecAtom):
    guarantee: str
    tier: int | None = None

def check_contract(contract: Contract) -> bool:
    return bool(contract.guarantee.strip())

declare_entity(
    entity_name="Contract",
    entity_class=Contract,
    instance_relation_constraints={
        "CONTAINED_BY": {"target_entity_paths": ("Node//Artifact//Component",), "targets_per_source": 1},
    },
    instance_check=check_contract,
)
```

### Declaration 38

MODEL//ANECHOIC <+ Node//Artifact//Atom//Spec Atom//Contract//Component Contract

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Contract
from dataclasses import field

class ComponentContract(Contract):
    tier: int = field(metadata={"allowed_values": (1,)})

declare_entity(
    entity_name="Component Contract",
    entity_class=ComponentContract,
)
```

### Declaration 39

MODEL//ANECHOIC <+ Node//Artifact//Atom//Spec Atom//Component Seed Manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import SpecAtom

class ComponentSeedManifest(SpecAtom):
    component_seed_id: str
    purpose: str
    solution: str
    boundaries: dict[str, object] | None = None
    tier: int | None = None

def check_component_seed_manifest(spec: ComponentSeedManifest) -> bool:
    return bool(spec.component_seed_id.startswith("CS") and spec.component_seed_id[2:].isascii()
                and spec.component_seed_id[2:].isdigit() and spec.purpose.strip() and spec.solution.strip())

declare_entity(
    entity_name="Component Seed Manifest",
    entity_class=ComponentSeedManifest,
    instance_relation_constraints={
        "CONTAINED_BY": {"target_entity_paths": ("Node//Artifact//Component",), "targets_per_source": 1},
    },
    instance_check=check_component_seed_manifest,
)
```
