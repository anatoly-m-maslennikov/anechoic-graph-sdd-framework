from __future__ import annotations
from dataclasses import dataclass
from dataclasses import field
from typing import ClassVar

@dataclass
class Node:
    pass

@dataclass
class Cardinality:
    pass

@dataclass
class Carrier:
    pass

@dataclass
class ComponentSpecSection:
    pass

@dataclass
class Continuant:
    pass

@dataclass
class EDSL:
    pass

@dataclass
class Format:
    pass

@dataclass
class Graph:
    pass

@dataclass
class Model:
    pass

@dataclass
class Module:
    pass

@dataclass
class Occurrent:
    pass

@dataclass
class Relation:
    pass

@dataclass
class SSOT:
    pass

@dataclass
class Unit:
    pass

@dataclass
class View:
    pass

@dataclass
class Artifact(Node):
    pass

@dataclass
class Ephemeral(Node):
    pass

@dataclass
class Atom(Artifact):
    atom_id: str
    version: int = field(metadata={'minimum_value': 1})
    ref_id: str
    family_marker: ClassVar[str | None] = None

@dataclass
class Component(Artifact):
    pass

@dataclass
class EventRecord(Artifact):
    pass

@dataclass
class Package(Artifact):
    pass

@dataclass
class PMETAAtom(Atom):
    family_marker: ClassVar[str] = 'P'

@dataclass
class SpecAtom(Atom):
    family_marker: ClassVar[str] = 'S'

@dataclass
class TicketAtom(Atom):
    family_marker: ClassVar[str] = 'T'

@dataclass
class Project(Component):
    pass

@dataclass
class ComponentPackage(Package):
    pass

@dataclass
class Contract(SpecAtom):
    guarantee: str
    tier: int | None = None

@dataclass
class Manifest(SpecAtom):
    control_flow: ClassVar[str] = 'Declarative'
    lens_whitelist: list[str] | None = field(default=None, kw_only=True)

@dataclass
class PackageSpec(SpecAtom):
    package_id: str
    purpose: str
    contract: str
    tier: int | None = None

@dataclass
class Purpose(SpecAtom):
    purpose: str

@dataclass
class ComponentContract(Contract):
    tier: int = field(metadata={'allowed_values': (1,)})

@dataclass
class ComponentManifest(Manifest):
    tier: int = field(metadata={'allowed_values': (0,)})
    component_id: str
    name: str
    layer: int | None = None

@dataclass
class ProjectManifest(Manifest):
    tier: int = field(metadata={'allowed_values': (-1,)})
    name: str
    prefix: str
    parameters: dict[str, object] = field(default_factory=dict)

@dataclass
class ComponentPurpose(Purpose):
    tier: int = field(metadata={'allowed_values': (0,)})
    component_id: str

@dataclass
class ProjectGoal(Purpose):
    tier: int = field(metadata={'allowed_values': (-1,)})
