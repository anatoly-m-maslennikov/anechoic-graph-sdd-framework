from __future__ import annotations
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime

@dataclass
class Node:
    pass

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

@dataclass
class ValueFormat:
    pass

@dataclass
class CardinalityContract:
    pass

@dataclass
class Carrier:
    pass

@dataclass
class Relation:
    pass

@dataclass
class Term:
    name: str

@dataclass
class Aspect(Node):
    pass

@dataclass
class Continuant(Node):
    pass

@dataclass
class Model(Node):
    pass

@dataclass
class Occurrent(Node):
    pass

@dataclass
class ProjectStructure(Node):
    pass

@dataclass
class BooleanValueFormat(ValueFormat):
    pass

@dataclass
class DateTimeValueFormat(ValueFormat):
    pass

@dataclass
class DecimalValueFormat(ValueFormat):
    pass

@dataclass
class FloatValueFormat(ValueFormat):
    pass

@dataclass
class IntegerValueFormat(ValueFormat):
    pass

@dataclass
class ScalarValueFormat(ValueFormat):
    pass

@dataclass
class StringValueFormat(ValueFormat):
    pass

@dataclass
class Database(Carrier):
    pass

@dataclass
class Directory(Carrier):
    pass

@dataclass
class DockerImage(Carrier):
    pass

@dataclass
class File(Carrier):
    pass

@dataclass
class GitBranch(Carrier):
    pass

@dataclass
class GitCommit(Carrier):
    pass

@dataclass
class GitRepository(Carrier):
    pass

@dataclass
class PullRequest(Carrier):
    pass

@dataclass
class Actor(Continuant):
    pass

@dataclass
class Atom(Continuant):
    pass
    header: AtomHeader = field(metadata={'property_occurrence_cardinality': 1, 'value_cardinality': 0, 'dependent_property_cardinality': {'minimum': 0, 'maximum': None}})
    content: AtomContent = field(metadata={'property_occurrence_cardinality': 1, 'value_cardinality': 0, 'dependent_property_cardinality': {'minimum': 0, 'maximum': None}})

@dataclass
class EventRecord(Continuant):
    pass

@dataclass
class Journal(Continuant):
    pass

@dataclass
class NamedSelection(Continuant):
    pass

@dataclass
class Package(Continuant):
    pass

@dataclass
class Projection(Continuant):
    pass

@dataclass
class ScopeUnit(Continuant):
    pass

@dataclass
class Event(Occurrent):
    pass

@dataclass
class Execution(Occurrent):
    pass

@dataclass
class Runtime(Occurrent):
    pass

@dataclass
class Markdown(File):
    pass

@dataclass
class AnalysisAndAdvisory(Atom):
    pass

@dataclass
class Concern(Atom):
    pass

@dataclass
class Delivery(Atom):
    pass

@dataclass
class Evaluation(Atom):
    pass

@dataclass
class Method(Atom):
    pass

@dataclass
class Operations(Atom):
    pass

@dataclass
class Plan(Atom):
    pass

@dataclass
class Requirement(Atom):
    pass

@dataclass
class ProjectPackage(Package):
    pass

@dataclass
class Catalog(Projection):
    pass

@dataclass
class EntityDefinitionAndActiveSubjectCoverage(Projection):
    pass

@dataclass
class Hub(Projection):
    pass

@dataclass
class Map(Projection):
    pass

@dataclass
class PassiveOnlySubjects(Projection):
    pass

@dataclass
class PrimaryEntitiesTree(Projection):
    pass

@dataclass
class PrimaryEntitiesWithDirectProperties(Projection):
    pass

@dataclass
class PrimaryEntitiesWithInheritedFormalClaims(Projection):
    pass

@dataclass
class PrimaryEntitiesWithInheritedPropertyContracts(Projection):
    pass

@dataclass
class SubjectsWithoutRequirementDeclarations(Projection):
    pass

@dataclass
class Project(ScopeUnit):
    pass

@dataclass
class ActionRun(Execution):
    pass

@dataclass
class StepRun(Execution):
    pass

@dataclass
class WorkflowRun(Execution):
    pass

@dataclass
class ExternalLocalRuntime(Runtime):
    pass

@dataclass
class ExternalRemoteRuntime(Runtime):
    pass

@dataclass
class InternalLocalRuntime(Runtime):
    pass

@dataclass
class InternalRemoteRuntime(Runtime):
    pass

@dataclass
class MarkdownAtomCarrier(Markdown):
    pass

@dataclass
class CodeSpecMismatch(Concern):
    pass

@dataclass
class DeliveryDecision(Delivery):
    pass

@dataclass
class DeliveryEngStandard(Delivery):
    pass

@dataclass
class DeliverySolution(Delivery):
    pass

@dataclass
class DeliverySpecPolicy(Delivery):
    pass

@dataclass
class FileLayout(Delivery):
    pass

@dataclass
class EvaluationDecision(Evaluation):
    pass

@dataclass
class EvaluationEngStandard(Evaluation):
    pass

@dataclass
class EvaluationSolution(Evaluation):
    pass

@dataclass
class EvaluationSpecPolicy(Evaluation):
    pass

@dataclass
class MethodDecision(Method):
    pass

@dataclass
class MethodEngStandard(Method):
    pass

@dataclass
class MethodSolution(Method):
    pass

@dataclass
class MethodSpecPolicy(Method):
    pass

@dataclass
class TermDefinition(Method):
    pass

@dataclass
class Action(Operations):
    pass

@dataclass
class OperationsDecision(Operations):
    pass

@dataclass
class Step(Operations):
    pass

@dataclass
class Workflow(Operations):
    pass

@dataclass
class PlanForm(Plan):
    pass

@dataclass
class WorkReport(Plan):
    pass

@dataclass
class Declaration(Requirement):
    pass

@dataclass
class RelationDeclaration(Requirement):
    pass

@dataclass
class RequirementForm(Requirement):
    pass

@dataclass
class RequirementSolution(Requirement):
    pass

@dataclass
class RequirementSpecPolicy(Requirement):
    pass

@dataclass
class ScopeUnitDeclaration(Requirement):
    pass

@dataclass
class Session(ExternalRemoteRuntime):
    pass
