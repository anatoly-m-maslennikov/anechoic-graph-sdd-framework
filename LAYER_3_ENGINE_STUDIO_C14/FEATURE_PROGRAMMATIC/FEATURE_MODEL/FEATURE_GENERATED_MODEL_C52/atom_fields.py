"""Atom carrier fields from the retained Model snapshot."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class AtomConcernContext:
    priority: str = field(metadata={'property_occurrence_cardinality': 1, 'value_cardinality': 1, 'allowed_values': ('High', 'Medium', 'Low')})

@dataclass
class AtomContainer:
    atom: str = field(default=None, kw_only=True, metadata={'value_cardinality': {'minimum': 0, 'maximum': 1}})
    scope_unit: str = field(default=None, kw_only=True, metadata={'value_cardinality': {'minimum': 0, 'maximum': 1}})

@dataclass
class AtomContent:
    summary: str = field(metadata={'property_occurrence_cardinality': 1, 'value_cardinality': 1})
    properties: dict[str, object] = field(default_factory=dict)

@dataclass
class AtomContext:
    container: AtomContainer = field(metadata={'property_occurrence_cardinality': 1, 'value_cardinality': 0, 'dependent_property_cardinality': 1})
    role: str = field(metadata={'property_occurrence_cardinality': 1, 'value_cardinality': 1})
    form: str = field(metadata={'property_occurrence_cardinality': 1, 'value_cardinality': 1})
    label: str = field(default=None, kw_only=True, metadata={'value_cardinality': {'minimum': 0, 'maximum': 1}})
    topics: AtomTopics = field(metadata={'property_occurrence_cardinality': 1, 'value_cardinality': 0, 'dependent_property_cardinality': {'minimum': 1, 'maximum': 2}})
    tier: AtomTier = field(metadata={'property_occurrence_cardinality': 1, 'value_cardinality': 1, 'minimum_value': -1, 'dependent_property_cardinality': {'minimum': 0, 'maximum': 1}})
    plan: AtomPlanContext = field(default=None, kw_only=True, metadata={'property_occurrence_cardinality': {'minimum': 0, 'maximum': 1}, 'value_cardinality': 0, 'dependent_property_cardinality': {'minimum': 1, 'maximum': 2}})
    concern: AtomConcernContext = field(default=None, kw_only=True, metadata={'property_occurrence_cardinality': {'minimum': 0, 'maximum': 1}, 'value_cardinality': 0, 'dependent_property_cardinality': 1})

@dataclass
class AtomContextFields:
    role: str = field(metadata={'property_occurrence_cardinality': 1, 'value_cardinality': 1})
    form: str = field(metadata={'property_occurrence_cardinality': 1, 'value_cardinality': 1})
    label: str = field(default=None, kw_only=True, metadata={'value_cardinality': {'minimum': 0, 'maximum': 1}})

@dataclass
class AtomDestination:
    file: AtomDestinationFile = field(metadata={'property_occurrence_cardinality': 1, 'value_cardinality': 0, 'dependent_property_cardinality': 2})

@dataclass
class AtomDestinationFile:
    name: str = field(metadata={'value_cardinality': 1})
    path: str = field(metadata={'value_cardinality': 1})

@dataclass
class AtomHeader:
    identity: AtomIdentity = field(metadata={'property_occurrence_cardinality': 1, 'value_cardinality': 0, 'dependent_property_cardinality': 2})
    context: AtomContext = field(metadata={'property_occurrence_cardinality': 1, 'value_cardinality': 0, 'dependent_property_cardinality': {'minimum': 5, 'maximum': 7}})
    relations: dict[str, list[str]] = field(default=None, kw_only=True, metadata={'property_occurrence_cardinality': {'minimum': 0, 'maximum': 1}, 'value_cardinality': 0, 'dependent_property_cardinality': {'minimum': 1, 'maximum': None}, 'dependent_property_name_format': 'str', 'dependent_property_value_format': 'str', 'dependent_property_value_cardinality': {'minimum': 1, 'maximum': None}})
    state: AtomState = field(metadata={'property_occurrence_cardinality': 1, 'value_cardinality': 0, 'dependent_property_cardinality': 3})
    destination: AtomDestination = field(metadata={'property_occurrence_cardinality': 1, 'value_cardinality': 0, 'dependent_property_cardinality': 1})

@dataclass
class AtomIdentity:
    id: str = field(metadata={'property_occurrence_cardinality': 1, 'value_cardinality': 1})
    ref_id: str = field(metadata={'property_occurrence_cardinality': 1, 'value_cardinality': 1})

@dataclass
class AtomPlanContext:
    work_sequence_number: int = field(default=None, kw_only=True, metadata={'value_cardinality': {'minimum': 0, 'maximum': 1}, 'minimum_value': 1})
    ai_agent_confidence_threshold: int = field(default=None, kw_only=True, metadata={'value_cardinality': {'minimum': 0, 'maximum': 1}, 'minimum_value': 0, 'maximum_value': 100})

@dataclass
class AtomState:
    status: str = field(metadata={'property_occurrence_cardinality': 1, 'value_cardinality': 1})
    version: int = field(metadata={'property_occurrence_cardinality': 1, 'value_cardinality': 1, 'minimum_value': 1})
    updated_at: datetime = field(metadata={'property_occurrence_cardinality': 1, 'value_cardinality': 1})

@dataclass
class AtomTier:
    value: int = field(metadata={'property_occurrence_cardinality': 1, 'value_cardinality': 1, 'minimum_value': -1})
    label: str = field(default=None, kw_only=True, metadata={'value_cardinality': {'minimum': 0, 'maximum': 1}})

@dataclass
class AtomTopics:
    main_subject: str = field(metadata={'value_cardinality': 1})
    dependencies: list[str] = field(default=None, kw_only=True, metadata={'property_occurrence_cardinality': {'minimum': 0, 'maximum': 1}, 'value_cardinality': {'minimum': 0, 'maximum': None}})
