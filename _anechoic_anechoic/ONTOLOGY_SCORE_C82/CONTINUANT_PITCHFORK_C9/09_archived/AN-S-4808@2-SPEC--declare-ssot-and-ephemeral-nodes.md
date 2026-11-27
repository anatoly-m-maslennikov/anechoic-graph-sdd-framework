---
atom_family: SPEC
atom_id: AN-S-4808
container:
  component: C9
tier: 2
context:
  lens: SPEC
relations:
  IS_REFERENCE:
  - AN-T-3904
state:
  status: "archived"
  version: 2
  updated_at: '2026-11-24T14:05:42+00:00'
---

## Summary

Declare SSOT and ephemeral Nodes

## Semantics

Nodes represent Project entities. SSOT Nodes capture prescribed, recorded, or realized information. Ephemeral Nodes represent temporary working information. The Component parent tree applies to both Specification and Realization.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import declare_model
from anechoic.model import Node, Carrier, Artifact, Ephemeral, Continuant, Occurrent

class SSOT(Node): pass
class Prescribed(SSOT): pass
class Recorded(SSOT): pass
class Realization(SSOT): pass

class AtomFamily(Prescribed): pass
class Atom(Prescribed): pass
class Specification(Atom): pass
class Ticket(Atom): pass
class ProjectConfig(Atom): pass
class AtomCompanionContainer(Prescribed): pass
class EventRecord(Recorded): pass

class Package(Realization): pass
class ImplementationPackage(Package): pass
class ProjectRealization(Package): pass
class ComponentPackage(ImplementationPackage): pass
class TestPackage(Package): pass
class Module(Realization): pass
class Unit(Realization): pass
class Prompt(Realization): pass
class Asset(Realization): pass

class Component(Prescribed): pass
class ProjectSpec(Component): pass
class SpecBinding(Carrier): pass

class SessionContext(Node): pass
class SessionTask(Node): pass
class OperativePlan(Node): pass

declare_model(
    classification_axes=(
      { Artifact: (SSOT,),
        Ephemeral: (SessionContext, SessionTask, OperativePlan), },
      { Continuant: (Specification, ProjectConfig, EventRecord),
        Occurrent: (Ticket,), },
    ),
    model_parts={
        Prescribed: {"Content": (Atom,), "Structure": (AtomFamily, Component, AtomCompanionContainer)},
        Realization: {"Content": (Module, Unit, Asset, Prompt), "Structure": (Package,)},
    },
    containment={
        Component: (Component, Atom, ComponentPackage),
        AtomCompanionContainer: (Atom,),
        Package: (Package, Module, Prompt, Asset),
        Module: (Unit,),
    },
    project_singletons=(ProjectRealization, ProjectSpec),
    component_tree={"nodes": Component, "parent_relation": "CHILD_OF",
                    "views": (Specification, ComponentPackage)},
    relations={"HAS_REALIZATION": {"source": Atom, "targets": (Package, Module),
                                   "carrier": SpecBinding}},
    carriers={SpecBinding: {"owner": Package, "path": "{package}__spec_bind.yaml"}},
    atom_families={Specification: ("Specification", "S"), Ticket: ("Ticket", "T"),
                   ProjectConfig: ("project_config", "C")},
    legacy_family_markers={"P": ProjectConfig},
)
```
