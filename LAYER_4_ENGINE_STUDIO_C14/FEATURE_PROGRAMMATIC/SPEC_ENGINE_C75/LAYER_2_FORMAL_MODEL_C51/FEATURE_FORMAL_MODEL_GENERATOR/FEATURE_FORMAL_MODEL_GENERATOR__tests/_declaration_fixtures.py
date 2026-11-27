import importlib

base = (
    "FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51."
    "FEATURE_FORMAL_MODEL_GENERATOR."
)
shared = importlib.import_module(
    base + "FEATURE_FORMAL_MODEL_GENERATOR__shared"
)
catalog = importlib.import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30."
    "relation_declaration_catalog__pub"
)
select_model_claims = shared.select_model_claims
_check_relation_references = shared._check_relation_references
_class_property_aliases = shared._class_property_aliases
build_relation_declaration_catalog = catalog.build_relation_declaration_catalog

CLAIM = (
    "from anechoic.formal_claims import "
    "declare_entity\ndeclare_entity(entity_name='Atom')\n"
)


def carrier(
    subject="ANECHOIC_MODEL <+ Atom",
    *,
    identifier="CA-R-1",
    status="active",
    body=None,
):
    if body is None:
        body = f"## Claim\n\n### Formal Claim\n\n```python\n{CLAIM}```\n"
    return {
        "source": {"path": f"{identifier}.md", "atom_id": identifier},
        "read_view": {"status": status, "content_role": "Requirement"},
        "subjects": {"governs": subject},
        "body": body,
    }


def relation_setup():
    def model(subject, identifier, claim):
        body = f"## Claim\n### Formal Claim\n```python\n{claim}\n```\n"
        return carrier(
            "ANECHOIC_MODEL <+ " + subject,
            identifier=identifier,
            body=body,
        )

    def entity(name, base="", constraints=""):
        imports = "from anechoic.model import Animal\n" if base else ""
        return (
            "from anechoic.formal_claims import declare_entity\n"
            + imports
            + f"class {name}{base}:\n    pass\n"
            + f"declare_entity(entity_name='{name}', "
            f"entity_class={name}{constraints})"
        )

    animal = model("Animal", "CA-R-10", entity("Animal"))
    cat = model(
        "Cat",
        "CA-R-11",
        entity(
            "Cat",
            "(Animal)",
            ", instance_relation_constraints={'EATS': "
            "{'target_entity_paths': ('Food',)}}",
        ),
    )
    food = model("Food", "CA-R-12", entity("Food"))
    toy = model("Toy", "CA-R-13", entity("Toy"))
    relation = (
        "from anechoic.formal_claims import declare_relation\n"
        "declare_relation(relation_name='EATS', inverse_alias='EATEN_BY', "
        "endpoint_pairs=("
        "{'source_endpoint': {'level': 'instances', 'entity_paths': "
        "('Animal',)}, "
        "'target_endpoint': {'level': 'instances', 'entity_paths': "
        "('Food',)}}, "
        "{'source_endpoint': {'level': 'instances', 'entity_paths': "
        "('Food',)}, "
        "'target_endpoint': {'level': 'instances', 'entity_paths': "
        "('Toy',)}}))"
    )
    link = model("Relation//EATS", "CA-R-14", relation)
    return model, entity, animal, cat, food, toy, link


def registry_native(name, extra, identifier):
    claim = (
        "from anechoic.formal_claims import declare_relation\n"
        f"declare_relation(relation_name='{name}', source_endpoint={{}}, "
        f"target_endpoint={{}}{extra})"
    )
    return carrier(
        "ANECHOIC_MODEL <+ Relation//" + name,
        identifier=identifier,
        body=f"## Claim\n### Formal Claim\n```python\n{claim}\n```\n",
    )


def property_setup():
    root = "Atom/(.Header.Context.Role:=Operations)/Workflow"

    def declaration(subject, identifier, claim):
        return carrier(
            "ANECHOIC_MODEL <+ " + subject,
            identifier=identifier,
            body=f"## Claim\n### Formal Claim\n```python\n{claim}\n```\n",
        )

    workflow = declaration(
        root,
        "CA-R-30",
        "from anechoic.formal_claims import declare_entity\n"
        "class Workflow:\n    pass\n"
        "declare_entity(entity_name='Workflow', entity_class=Workflow)",
    )
    content = declaration(
        root + ".Content",
        "CA-R-31",
        "from anechoic.formal_claims import declare_entity\n"
        f"declare_entity(entity_name='Content', "
        f"relation_name='IS_PROPERTY_OF', base_path='{root}')",
    )
    relation = declaration(
        "Relation//IS_PROPERTY_OF",
        "CA-R-32",
        "from anechoic.formal_claims import declare_relation\n"
        "declare_relation(relation_name='IS_PROPERTY_OF', "
        "source_endpoint={}, target_endpoint={})",
    )
    child = declaration(
        root + ".Content.Name",
        "CA-R-33",
        "from anechoic.formal_claims import declare_entity\n"
        "declare_entity(entity_name='Name', "
        "relation_name='IS_PROPERTY_OF', base_path='Workflow.Content')",
    )
    return root, workflow, content, relation, child


def inheritance_setup():
    def model(subject, identifier, claim):
        return carrier(
            "ANECHOIC_MODEL <+ " + subject,
            identifier=identifier,
            body=f"## Claim\n### Formal Claim\n```python\n{claim}\n```\n",
        )

    atom = model("Atom", "CA-R-40", cls("Atom"))
    ops = model(
        "Atom/(.Header.Context.Role:=Operations)",
        "CA-R-41",
        cls("Operations", "Atom"),
    )
    flow = model(
        "Atom/(.Header.Context.Role:=Operations)/Workflow",
        "CA-R-42",
        cls("Workflow", "Operations"),
    )
    prop = model(
        "Atom.Content",
        "CA-R-43",
        "from anechoic.formal_claims import declare_entity\n"
        "declare_entity(entity_name='Content', "
        "relation_name='IS_PROPERTY_OF', base_path='Atom')",
    )
    child = model(
        "Workflow.Content.Claim",
        "CA-R-44",
        "from anechoic.formal_claims import declare_entity\n"
        "declare_entity(entity_name='Claim', "
        "relation_name='IS_PROPERTY_OF', base_path='Workflow.Content')",
    )
    rel = model(
        "Relation//IS_PROPERTY_OF",
        "CA-R-45",
        "from anechoic.formal_claims import declare_relation\n"
        "declare_relation(relation_name='IS_PROPERTY_OF', "
        "source_endpoint={}, target_endpoint={})",
    )
    return model, atom, ops, flow, prop, child, rel


def endpoint_setup():
    def model(subject, identifier, claim):
        return carrier(
            "ANECHOIC_MODEL <+ " + subject,
            identifier=identifier,
            body=f"## Claim\n### Formal Claim\n```python\n{claim}\n```\n",
        )

    plan_path = "Atom/(.Header.Context.Role:=Plan)"
    step_path = "Atom/(.Header.Context.Role:=Operations)/Step"
    plan = model(
        plan_path,
        "CA-R-50",
        "from anechoic.formal_claims import declare_entity\n"
        "class Plan:\n    pass\n"
        "declare_entity(entity_name='Plan', entity_class=Plan)",
    )
    step = model(
        step_path,
        "CA-R-51",
        "from anechoic.formal_claims import declare_entity\n"
        "class Step:\n    pass\n"
        "declare_entity(entity_name='Step', entity_class=Step, "
        "instance_relation_constraints={'LINKS': "
        "{'target_entity_paths': ('Atom/(.Header.Context.Role := "
        "Plan)',)}})",
    )
    rel = model(
        "Relation//LINKS",
        "CA-R-52",
        "from anechoic.formal_claims import declare_relation\n"
        "declare_relation(relation_name='LINKS', "
        "source_endpoint={'level': 'instances', 'entity_paths': "
        "('Atom/(.Header.Context.Role := Plan)',)}, "
        "target_endpoint={'level': 'instances', 'entity_paths': "
        "('Atom/(.Header.Context.Role := Plan)',)})",
    )
    return model, plan, step, rel


def endpoint_relation_setup():
    def with_claim(subject, identifier, claim):
        return carrier(
            subject,
            identifier=identifier,
            body=f"## Claim\n### Formal Claim\n```python\n{claim}\n```\n",
        )

    relation = (
        "from anechoic.formal_claims import declare_relation\n"
        "declare_relation(relation_name='LINKS', "
        "source_endpoint={'level': 'instances', 'entity_paths': "
        "('Atom',)}, "
        "target_endpoint={'level': 'instances', 'entity_paths': "
        "('Node',)})"
    )
    entity = (
        "from anechoic.formal_claims import declare_entity\n"
        "declare_entity(entity_name='Node', instance_relation_constraints="
        "{'LINKS': {'target_entity_paths': ('Atom',)}})"
    )
    atom = carrier()
    node = with_claim("ANECHOIC_MODEL <+ Node", "CA-R-2", entity)
    link = with_claim(
        "ANECHOIC_MODEL <+ CFEL <+ Relation//LINKS", "CA-R-3", relation
    )
    return with_claim, relation, entity, atom, node, link


def inverse_setup(model, entity):
    inverse = model(
        "Food",
        "CA-R-12",
        entity(
            "Food",
            constraints=", instance_relation_constraints={'EATEN_BY': "
            "{'target_entity_paths': ('Cat',)}}",
        ),
    )
    return inverse


def cls(name, base=None):
    imports = f"from anechoic.model import {base}\n" if base else ""
    return (
        "from anechoic.formal_claims import declare_entity\n"
        + imports
        + f"class {name}{f'({base})' if base else ''}:\n    pass\n"
        + f"declare_entity(entity_name='{name}', entity_class={name})"
    )
