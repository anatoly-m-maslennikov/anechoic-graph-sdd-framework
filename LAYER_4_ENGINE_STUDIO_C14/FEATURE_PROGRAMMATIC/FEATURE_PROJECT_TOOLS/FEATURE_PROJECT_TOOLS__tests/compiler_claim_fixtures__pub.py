"""Native claim inputs shared by compiler and Workbench tests."""

CONTENT_PROPERTY = """
from anechoic.formal_claims import Cardinality, declare_entity
from anechoic.model import Requirement, Method, Evaluation, Delivery
declare_entity(entity_name="Semantics", relation_name="IS_PROPERTY_OF", base_path="Atom.Content",
    value_cardinality=Cardinality(minimum=0, maximum=1), dependent_property_cardinality=0,
    applies_to_entity_classes=(Requirement, Method, Evaluation, Delivery))
"""

RECURSIVE_CONTENT = """
from anechoic.formal_claims import Cardinality, declare_entity
from anechoic.model import Requirement, Method, Evaluation, Delivery
declare_entity(entity_name="Content", relation_name="IS_PROPERTY_OF", base_path="Atom",
    property_occurrence_cardinality=1, value_cardinality=0,
    dependent_property_cardinality=Cardinality(minimum=0, maximum=None), dependent_property_name_format=str,
    recursive_dependent_property_cardinality=Cardinality(minimum=0, maximum=None),
    recursive_dependent_property_name_format=str, recursive_dependent_property_value_format="markdown",
    ordered_dependent_property_roles=(Requirement, Method, Evaluation, Delivery),
    ordered_dependent_property_pairs=(("Summary", "Claim"), ("Claim", "Semantics"), ("Semantics", "Details")))
"""

NESTED_CONTENT = """
from anechoic.formal_claims import Cardinality, declare_entity
from anechoic.model import Requirement, Method, Evaluation, Delivery

declare_entity(
    entity_name="Prose Claim",
    relation_name="IS_PROPERTY_OF",
    base_path="Atom.Content.Claim",
    value_cardinality=Cardinality(minimum=0, maximum=1),
    dependent_property_cardinality=0,
    applies_to_entity_classes=(Requirement, Method, Evaluation, Delivery),
)
"""

NESTED_HEADER = """
from anechoic.formal_claims import declare_entity
declare_entity(entity_name="File", relation_name="IS_PROPERTY_OF", base_path="Atom.Header.Destination",
    property_occurrence_cardinality=1, value_cardinality=0, dependent_property_cardinality=2,
    allowed_dependent_property_names=("Name", "Path"), dependent_property_value_format=str)
"""

ROLE_HEADER = """
from anechoic.formal_claims import Cardinality, declare_entity
from anechoic.model import Plan

declare_entity(
    entity_name="Plan",
    relation_name="IS_PROPERTY_OF",
    base_path="Atom.Header.Context",
    property_occurrence_cardinality=Cardinality(minimum=0, maximum=1),
    value_cardinality=0,
    dependent_property_cardinality=Cardinality(minimum=1, maximum=2),
    allowed_dependent_property_names=("Work Sequence Number", "AI Agent Confidence Threshold"),
    applies_to_entity_classes=(Plan,),
)
"""

ROLE = """
from anechoic.formal_claims import declare_entity
from anechoic.model import Atom
class Method(Atom):
    pass
declare_entity(entity_class=Method, entity_name="Method", qualification_property_path="Atom.Header.Context.Role",
    classifications={"Role Order Number": 5})
"""

INSTANCE_CHECK = """
from anechoic.formal_claims import declare_entity
from anechoic.model import Atom

def is_valid_atom(atom: Atom) -> bool:
    return atom.version > 0

declare_entity(entity_name="Atom", instance_check=is_valid_atom)
"""

HEADER_RELATIONS = """
from anechoic.formal_claims import Cardinality, declare_entity
declare_entity(entity_name="Relations", relation_name="IS_PROPERTY_OF", base_path="Atom.Header",
    property_occurrence_cardinality=Cardinality(minimum=0, maximum=1), value_cardinality=0,
    dependent_property_cardinality=Cardinality(minimum=1, maximum=None),
    dependent_property_name_format=str, dependent_property_value_format=str,
    dependent_property_value_cardinality=Cardinality(minimum=1, maximum=None))
"""

FORM_EXAMPLES = [
    (
        """Atom.Header.Context.Form :: Scope Delegation;
FOR EACH $a[<Atom>, (.Header.Context.Form = Scope Delegation)]:
($a.Header.Context.Role:: [in (Requirement, Method, Evaluation, Delivery, Operations)]{::1});""",
        """from anechoic.formal_claims import declare_entity
declare_entity(entity_name='Form', relation_name='IS_PROPERTY_OF', base_path='Atom.Header.Context',
    allowed_values=('Scope Delegation',), form_roles=('Requirement', 'Method', 'Evaluation', 'Delivery', 'Operations'))""",
    ),
    (
        """Atom.Header.Context.Form :: Work Report;
Atom/(.Header.Context.Role in (Plan))/(.Header.Context.Form in (Work Report)).Content.Details:: {::1};
Atom/(.Header.Context.Role in (Plan))/(.Header.Context.Form in (Work Report)).Content.Details.*[]{::0};
Atom/(.Header.Context.Role in (Plan))/(.Header.Context.Form in (Work Report)).Content.Summary ;> Atom/(.Header.Context.Role in (Plan))/(.Header.Context.Form in (Work Report)).Content.Details;
FOR EACH $report[<Atom>, (.Header.Context.Form = Work Report)]: ($report.Header.Context.Role == Plan);""",
        """from anechoic.formal_claims import declare_entity
from anechoic.model import Plan
class WorkReport(Plan):
    pass
declare_entity(entity_name='Work Report', entity_class=WorkReport, qualification_property_path='Atom.Header.Context.Form',
    form_roles=('Plan',), form_content={'required_value': 'Details', 'no_children': 'Details', 'after': 'Summary'})""",
    ),
]

ANALYSIS = """from anechoic.formal_claims import declare_entity
declare_entity(entity_name="Status", relation_name="IS_PROPERTY_OF", base_path="Atom.Header.State", applies_to_role="Analysis and Advisory", applies_to_forms=("Analysis Report", "Rationale"), allowed_values=("Done",))"""

CLASSIFICATION_PYTHON_BODY = '## Claim\n### Formal Claim\n```python\nfrom anechoic.formal_claims import declare_entity\ndeclare_entity(entity_name="Node", allowed_classification_values={"Container": ("yes", "no")})\n```\n'

EVENT_CLAIM = """from anechoic.formal_claims import declare_entity
declare_entity(entity_name="ID", relation_name="IS_PROPERTY_OF", base_path="Event Record",
    property_occurrence_cardinality=1, value_format=str, value_cardinality=1,
    dependent_property_cardinality=0, population_entity_path="Event Record",
    population_unique_constraints=({"keys": ("ID",)},))
"""

EVENT_CLASS = """from anechoic.formal_claims import declare_entity
class Atom:
    pass
declare_entity(entity_name="Atom", entity_class=Atom,
    population_unique_constraints=({"keys": ("Header.Identity.ID", "Header.State.Version")},))
"""

FALLBACK_PLAN = "Atom/(.Header.Context.Role:=Plan)"
FALLBACK_PROP = FALLBACK_PLAN + ".Header.Context.Plan.AI Agent Confidence Threshold"
FALLBACK_PROJECT = "Project.Settings.AI Agent Confidence Threshold"
FALLBACK_CLAIM = f'''from anechoic.formal_claims import Cardinality, declare_entity
declare_entity(entity_name="AI Agent Confidence Threshold", relation_name="IS_PROPERTY_OF",
 base_path="{FALLBACK_PLAN}.Header.Context.Plan", value_format=int,
 value_cardinality=Cardinality(minimum=0, maximum=1), minimum_value=0, maximum_value=100,
 dependent_property_cardinality=0, fallback_chain=(
 {{"lookup_relation":"IS_CONTAINED_BY","lookup_property":"{FALLBACK_PROP}"}},
 {{"project_entity":"Project","project_property":"{FALLBACK_PROJECT}"}},))'''

SEQUENCE_PLAN = "Atom/(.Header.Context.Role:=Plan)"
SEQ = "Header.Context.Plan.Work Sequence Number"
BASE = SEQUENCE_PLAN + ".Header.Context.Plan"
SEQUENCE_PROP = SEQUENCE_PLAN + "." + SEQ
SEQUENCE_CLAIM = f'''from anechoic.formal_claims import Cardinality, declare_entity
declare_entity(entity_name="Work Sequence Number", relation_name="IS_PROPERTY_OF", base_path="{BASE}", value_format=int,
 value_cardinality=Cardinality(minimum=0, maximum=1), minimum_value=1, dependent_property_cardinality=0,
 population_entity_path="{SEQUENCE_PLAN}", population_unique_constraints=(
 {{"keys": ("Header.Context.Container.atom", "{SEQ}"), "status":"Active", "single_value_paths": ("Header.Context.Container.atom", "{SEQ}")}},
 {{"keys": ("Header.Context.Container.scope_unit", "{SEQ}"), "status":"Active", "single_value_paths": ("Header.Context.Container.scope_unit", "{SEQ}")}},))'''

STATUS_PLAN = """from anechoic.model import Plan
from anechoic.formal_claims import declare_entity
declare_entity(entity_name="Status", relation_name="IS_PROPERTY_OF", base_path="Atom.Header.State", applies_to_entity_classes=(Plan,), allowed_values=("Backlog", "Done", "Canceled"), status_order_numbers={"Backlog": 1, "Done": 20, "Canceled": 40}, status_groups={"Backlog": "Backlog"})"""

DEPENDENCIES = """from anechoic.formal_claims import declare_entity
declare_entity(entity_name="ID", relation_name="IS_PROPERTY_OF", base_path="Projection",
    property_occurrence_cardinality=1, value_format=str, value_cardinality=1,
    dependent_property_cardinality=0,
    population_functional_dependencies=(
        {"keys": ("Form", "Scope Unit"), "dependents": ("ID",)},
        {"keys": ("ID",), "dependents": ("Form", "Scope Unit")},
    ))"""

STATUS_GROUPS = """from anechoic.formal_claims import declare_entity
declare_entity(entity_name="Summary", relation_name="IS_PROPERTY_OF", base_path="Atom.Content",
 property_occurrence_cardinality=1, value_cardinality=1, dependent_property_cardinality=0,
 population_entity_path="Atom", population_functional_dependencies=(
 {"keys": ("Header.Identity.ID",), "dependents": ("Content.Summary",),
  "status_groups": ("Current", "Backlog", "Archived")},))"""

THRESHOLD = """from anechoic.formal_claims import declare_entity
declare_entity(entity_name="AI Agent Confidence Threshold", relation_name="IS_PROPERTY_OF", base_path="Project.Settings", property_occurrence_cardinality=1, value_format=int, value_cardinality=1, dependent_property_cardinality=0, minimum_value=0, maximum_value=100, fallback_value=90)
"""

WORKSPACE = """from dataclasses import dataclass, field
from anechoic.formal_claims import Cardinality, declare_entity

@dataclass
class Workspace:
    native_thread_id: str = field(metadata={"property_occurrence_cardinality": Cardinality(minimum=0, maximum=1), "value_cardinality": Cardinality(minimum=0, maximum=1)})
    project_root: str = field(metadata={"property_occurrence_cardinality": 1, "value_cardinality": 1})

declare_entity(entity_name="Workspace", entity_class=Workspace,
    incoming_model_relations=({"source": "View", "relation": "IS_CONTAINED_BY", "source_cardinality": 1, "target_cardinality": Cardinality(minimum=1, maximum=None)},))
"""
