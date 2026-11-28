from __future__ import annotations
from dataclasses import field

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass

from .atom_fields import (
    AtomConcernContext as AtomConcernContext,
    AtomContainer as AtomContainer,
    AtomContent as AtomContent,
    AtomContext as AtomContext,
    AtomContextFields as AtomContextFields,
    AtomDestination as AtomDestination,
    AtomDestinationFile as AtomDestinationFile,
    AtomHeader as AtomHeader,
    AtomIdentity as AtomIdentity,
    AtomPlanContext as AtomPlanContext,
    AtomState as AtomState,
    AtomTier as AtomTier,
    AtomTopics as AtomTopics,
)

from .value_formats import (
    ValueFormat as ValueFormat,
    BooleanValueFormat as BooleanValueFormat,
    DateTimeValueFormat as DateTimeValueFormat,
    DecimalValueFormat as DecimalValueFormat,
    FloatValueFormat as FloatValueFormat,
    IntegerValueFormat as IntegerValueFormat,
    ScalarValueFormat as ScalarValueFormat,
    StringValueFormat as StringValueFormat,
)


_STRICT = ConfigDict(strict=True, extra="forbid")


@dataclass(config=_STRICT)
class Node:
    pass


@dataclass(config=_STRICT)
class CardinalityContract:
    pass


@dataclass(config=_STRICT)
class Carrier:
    pass


@dataclass(config=_STRICT)
class Relation:
    pass


@dataclass(config=_STRICT)
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


def _atom_field():
    return field(
        metadata={
            "property_occurrence_cardinality": 1,
            "value_cardinality": 0,
            "dependent_property_cardinality": {"minimum": 0, "maximum": None},
        }
    )


@dataclass
class Atom(Continuant):
    header: AtomHeader = _atom_field()
    content: AtomContent = _atom_field()


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
