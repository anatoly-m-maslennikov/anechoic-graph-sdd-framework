_FIXTURE_TEXT_1 = (
    "from anechoic.formal_claims import declare_entity, Cardinality"
)
_FIXTURE_TEXT_2 = (
    "declare_entity(entity_name='Status', "
    "relation_name='IS_PROPERTY_OF', "
    "base_path='Node', "
    "property_occurrence_cardinality=1, "
    "value_format='string', "
    "value_cardinality=Cardinality(minimum=1,"
    " maximum=None))"
)
_FIXTURE_TEXT_3 = (
    "from anechoic.formal_claims import declare_entity, Cardinality"
)
_FIXTURE_TEXT_4 = (
    "declare_entity(entity_name='Status', "
    "relation_name='IS_PROPERTY_OF', "
    "base_path='Node', "
    "property_occurrence_cardinality=1, "
    "value_format='string', "
    "value_cardinality=Cardinality(minimum=1,"
    " maximum=None))"
)
_FIXTURE_TEXT_5 = (
    "from anechoic.formal_claims import declare_entity, Cardinality"
)
_FIXTURE_TEXT_6 = (
    "declare_entity(entity_name='Status', "
    "relation_name='IS_PROPERTY_OF', "
    "base_path='Node', allowed_values=("
    "'Poison',))"
)
_FIXTURE_TEXT_7 = (
    "from anechoic.formal_claims import declare_entity, Cardinality"
)
_FIXTURE_TEXT_8 = (
    "declare_entity(entity_name='Status', "
    "relation_name='IS_PROPERTY_OF', "
    "base_path='Node', allowed_values=("
    "'Poison',))"
)


def inherited_format_carriers(carrier, claim):
    return [
        carrier("CA-R-1", "Node", claim("Node declaration.")),
        carrier("CA-R-2", "Node/Child", claim("Child declaration.")),
        carrier(
            "CA-R-3",
            "Node.Name",
            claim(
                "```python",
                "# model",
                (
                    "property_rule(address='Node.Name', "
                    "value_format='string', values='1')"
                ),
                "# instances",
                (
                    "property_rule(address='Node//$n.Name', "
                    "value_format='string', values='1')"
                ),
                "```",
            ),
        ),
        carrier(
            "CA-R-4",
            "Node.Name",
            claim(
                "```python",
                "# model",
                (
                    "property_rule(address='Node.Name', "
                    "value_format='integer', values='1')"
                ),
                "```",
            ),
            form="Rule",
        ),
    ]


def duplicate_property_carriers(carrier, claim):
    return [
        carrier("CA-R-1", "Node", claim("Node declaration.")),
        carrier(
            "CA-R-2",
            "Node.Status",
            claim(
                "```python",
                (
                    "from anechoic.formal_claims import "
                    "declare_entity, Cardinality"
                ),
                (
                    "declare_entity(entity_name='Status', "
                    "relation_name='IS_PROPERTY_OF', "
                    "base_path='Node', allowed_values=("
                    "'Draft',))"
                ),
                "```",
            ),
        ),
        carrier(
            "CA-R-3",
            "Node.Status",
            claim(
                "```python",
                (
                    "from anechoic.formal_claims import "
                    "declare_entity, Cardinality"
                ),
                (
                    "declare_entity(entity_name='Status', "
                    "relation_name='IS_PROPERTY_OF', "
                    "base_path='Node', allowed_values=("
                    "'Review',))"
                ),
                "```",
            ),
        ),
    ]


def inherited_contract_carriers(carrier, claim):
    return [
        carrier(
            "CA-R-1",
            "Node",
            claim(
                "```python",
                _FIXTURE_TEXT_1,
                _FIXTURE_TEXT_2,
                "```",
            ),
        ),
        carrier("CA-R-2", "Node/Child", claim("Child declaration.")),
        carrier(
            "CA-R-3",
            "Node.Status",
            claim(
                "```python",
                _FIXTURE_TEXT_3,
                _FIXTURE_TEXT_4,
                "```",
            ),
        ),
        carrier(
            "CA-R-4",
            "Node/Child.Status",
            claim(
                "```python",
                (
                    "from anechoic.formal_claims import "
                    "declare_entity, Cardinality"
                ),
                (
                    "declare_entity(entity_name='Status', "
                    "relation_name='IS_PROPERTY_OF', "
                    "base_path='Node/Child', "
                    "property_occurrence_cardinality=Cardinal"
                    "ity(minimum=0, maximum=1), "
                    "value_format='integer', "
                    "value_cardinality=2)"
                ),
                "```",
            ),
        ),
    ]


def nondeclaration_carriers(carrier, claim):
    return [
        carrier("CA-R-1", "Node", claim("Node declaration.")),
        carrier(
            "CA-R-2",
            "Node.Status",
            claim(
                "```python",
                (
                    "from anechoic.formal_claims import "
                    "declare_entity, Cardinality"
                ),
                (
                    "declare_entity(entity_name='Status', "
                    "relation_name='IS_PROPERTY_OF', "
                    "base_path='Node', allowed_values=("
                    "'Draft',))"
                ),
                "```",
            ),
        ),
        *_excluded_carriers(carrier, claim),
    ]


def _excluded_carriers(carrier, claim):
    return [
        carrier(
            "CA-M-3",
            "Node.Status",
            claim(
                "```python",
                _FIXTURE_TEXT_5,
                _FIXTURE_TEXT_6,
                "```",
            ),
            role="Method",
            form="Policy",
        ),
        carrier(
            "CA-R-4",
            "Node.Status",
            claim(
                "```python",
                _FIXTURE_TEXT_7,
                _FIXTURE_TEXT_8,
                "```",
            ),
            form="Rule",
        ),
        carrier(
            "CA-R-5",
            "Node.Status",
            claim(
                "```python",
                (
                    "from anechoic.formal_claims import "
                    "declare_entity, Cardinality"
                ),
                (
                    "declare_entity(entity_name='Status', "
                    "relation_name='IS_PROPERTY_OF', "
                    "base_path='Node', allowed_values=("
                    "'Poison',))"
                ),
                "```",
            ),
            form="Entity Definition",
        ),
    ]


def namespace_carriers(carrier, claim):
    return [
        carrier("CA-R-1", "ANECHOIC <+ MODEL", claim("Model root.")),
        carrier(
            "CA-R-2",
            "ANECHOIC <+ MODEL <+ Node",
            claim("Node declaration."),
        ),
        carrier(
            "CA-R-3",
            "ANECHOIC <+ STRUCTURE <+ Project",
            claim("Project declaration."),
        ),
        carrier(
            "CA-R-4",
            "ANECHOIC <+ OTHER <+ Ignored",
            claim("Other declaration."),
        ),
    ]


INHERITED_EXPECTED = (
    "# model\n"
    "property_rule(address='Node.Name', "
    "value_format='string', values='1')\n"
    "# instances\n"
    "property_rule(address='Node//$n.Name', "
    "value_format='string', values='1')"
)
