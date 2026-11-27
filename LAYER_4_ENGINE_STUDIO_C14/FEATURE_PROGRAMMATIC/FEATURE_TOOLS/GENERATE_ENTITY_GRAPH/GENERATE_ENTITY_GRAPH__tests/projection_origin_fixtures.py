OVERRIDE_RULES = (
    "# model\n"
    "relation(source='Node', name='LINKS', "
    "target='Node', source_count='0+')\n"
    "# instances\n"
    "relation(source='Node//$n', "
    "name='LINKS', target='Node//$m', "
    "source_count='0+')"
)


def local_override_carriers(carrier):
    return [
        carrier(
            "CA-R-1",
            "Node",
            OVERRIDE_RULES,
        ),
        carrier(
            "CA-R-2",
            "Node/Child",
            (
                "# model\n"
                "relation(source='Node/Child', name='LINKS', "
                "target='Node', source_count='1')"
            ),
        ),
        carrier(
            "CA-R-3",
            "Node.Status",
            (
                "property_rule(address='Node.Status', "
                "value_format='string', values='1')"
            ),
        ),
        carrier(
            "CA-R-4",
            "Node/Child.Status",
            (
                "property_rule(address='Node/Child.Status', "
                "value_format='integer', values='1')"
            ),
        ),
        carrier(
            "CA-R-5",
            "CFEL <+ Relation//LINKS",
            (
                "classify(address='Relation//LINKS', "
                "axis='Derivation', value='Direct', "
                "notation='relation')"
            ),
            form="Relation Declaration",
        ),
    ]


def authored_relation_carriers(carrier):
    return [
        carrier(
            "CA-R-1",
            "Node",
            (
                "# model\n"
                "relation(source='Node', name='LINKS', "
                "target='Node')\n"
                "relation(source='Node', name='BELONGS', "
                "target='Node', reverse=True)\n"
                "# instances\n"
                "relation(source='Node', name='LINKS', "
                "target='Node')"
            ),
        ),
        carrier(
            "CA-R-2",
            "CFEL <+ Relation//LINKS",
            (
                "classify(address='Relation//LINKS', "
                "axis='Derivation', value='Direct', "
                "notation='relation')"
            ),
            form="Relation Declaration",
        ),
        carrier(
            "CA-R-3",
            "CFEL <+ Relation//BELONGS",
            (
                "classify(address='Relation//BELONGS', "
                "axis='Derivation', value='Derived', "
                "notation='relation')"
            ),
            form="Relation Declaration",
        ),
    ]


def inverse_relation_declaration(carrier):
    declaration = carrier(
        "CA-R-2",
        "CFEL <+ Relation//LINKS",
        "",
        form="Relation Declaration",
    )
    declaration["body"] = (
        "## Claim\n"
        "\n"
        "### Formal Claim\n"
        "\n"
        "```python\n"
        "from anechoic.formal_claims import "
        "declare_relation\n"
        "declare_relation(relation_name='LINKS', "
        "inverse_alias='LINKED_BY', "
        "source_endpoint={'level': 'instances', "
        "'entity_paths': ('Node',)}, "
        "target_endpoint={'level': 'instances', "
        "'entity_paths': ('Node',)})\n"
        "```\n"
    )
    return declaration


INSTANCE_RELATION_CLAIM = (
    "from anechoic.formal_claims import "
    "declare_entity\n"
    "from anechoic.model import Node\n"
    "class Child(Node):\n"
    "    pass\n"
    "declare_entity(entity_class=Child, "
    "entity_name='Child', "
    "instance_relation_constraints={"
    "'IS_CONTAINED_BY': {"
    "'target_entity_paths': ('Node',), "
    "'targets_per_source': 0}})"
)
DIRECT_RELATION_CLAIM = (
    "from anechoic.formal_claims import "
    "declare_relation\n"
    "declare_relation(relation_name='LINKS', "
    "written_alias='<+', source_endpoint={"
    "'level': 'model_entities'}, "
    "target_endpoint={'level': "
    "'model_entities'})"
)
