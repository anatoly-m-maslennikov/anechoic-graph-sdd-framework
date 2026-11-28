"""Exact Python claims used by the native graph parity cases."""

WORKSPACE_CLAIM = (
    "from dataclasses import dataclass, field\n"
    "from anechoic.formal_claims import Cardinality, "
    "declare_entity\n"
    "@dataclass\n"
    "class Workspace:\n"
    "    name: str = "
    'field(metadata={"property_occurrence_cardinality": 1,'
    ' "value_cardinality": 1})\n'
    'declare_entity(entity_name="Workspace", '
    "entity_class=Workspace, "
    'incoming_model_relations=({"source": "View", '
    '"relation": "IS_CONTAINED_BY", "source_cardinality": '
    '1, "target_cardinality": Cardinality(minimum=1, '
    "maximum=None)},))"
)

STEP_CLAIM = (
    "from anechoic.formal_claims import declare_entity\n"
    "from anechoic.model import Operations\n"
    "\n"
    "class Step(Operations):\n"
    "    pass\n"
    "\n"
    "def step_has_one_execution_form(step: Step) -> bool:\n"
    "    return (len(step.runs) == 1 and not "
    "step.contains) or (not step.runs and "
    "bool(step.contains))\n"
    "\n"
    "declare_entity(\n"
    '    entity_name="Step",\n'
    "    entity_class=Step,\n"
    "    instance_check=step_has_one_execution_form,\n"
    "    instance_relation_constraints={\n"
    '        "RUNS": {"target_entity_paths": ("Action", '
    '"Workflow")},\n'
    '        "CONTAINS": {"target_entity_paths": '
    '("Step",)},\n'
    "    },\n"
    ")\n"
)
