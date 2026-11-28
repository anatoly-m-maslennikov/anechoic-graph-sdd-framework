"""Source carriers for contract-binding tests."""

from importlib import import_module

_support = import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH."
    "GENERATE_ENTITY_GRAPH__tests.contracts.contracts__shared"
)
carrier, body = _support.carrier, _support.body


def carriers_1_1():
    return [
        carrier("CA-R-1", "ANECHOIC_MODEL <+ Atom", body("Atom.")),
        carrier("CA-R-2", "ANECHOIC_MODEL <+ Atom.Header", body("Header.")),
        carrier("CA-R-3", "ANECHOIC_MODEL <+ Atom.Header.Role", body("Role.")),
    ]


def carriers_1_2():
    return [
        carrier("CA-R-4", "ANECHOIC_MODEL <+ Atom.Header.Form", body("Form.")),
        carrier(
            "CA-R-5",
            "ANECHOIC_MODEL <+ Atom/(.Header.Role:=Requirement)",
            body("Role rule."),
            form="Rule",
        ),
        carrier(
            "CA-R-6",
            "ANECHOIC_MODEL <+ Atom/(.Header.Form:=Declaration)",
            body("Form rule."),
            form="Rule",
        ),
    ]


def carriers_1_3():
    return [
        carrier(
            "CA-R-7",
            "ANECHOIC_MODEL <+ (Node, Node.**)",
            body("Scope."),
            form="Rule",
        ),
        carrier("CA-R-8", "ANECHOIC_MODEL <+ Node", body("Node.")),
        carrier(
            "CA-R-9",
            (
                "ANECHOIC_MODEL <+ Atom/(.Header.Role:=Re"
                "quirement)/(.Header.Form:=Declaration)"
            ),
            body("Combined rule."),
            form="Rule",
        ),
    ]


def carriers_1_4():
    return [
        carrier(
            "CA-R-10",
            (
                "ANECHOIC_MODEL <+ Atom/(.Header.Role: Me"
                "thod)/(.Header.Form: Declaration)"
            ),
            body("Combined colon rule."),
            form="Rule",
        ),
        carrier(
            "CA-R-11", "ANECHOIC_MODEL <+ Atom.Content.Claim", body("Claim.")
        ),
        carrier(
            "CA-R-12",
            "ANECHOIC_MODEL <+ Atom/(.Header.Role: Delivery).Content.Claim",
            body("Claim rule."),
            form="Rule",
        ),
    ]


def carriers_2_1():
    return [
        carrier("CA-R-1", "Node", body("Node declaration.")),
        carrier("CA-R-2", "Node/Parent", body("Parent declaration.")),
        carrier("CA-R-3", "Node/Parent/Child", body("Child declaration.")),
    ]


def carriers_2_2():
    return [
        carrier(
            "CA-R-4",
            "Node/Parent.Status",
            body(
                "### Formal Claim",
                "```python",
                "from anechoic.formal_claims import declare_entity",
                (
                    "declare_entity(entity_name='Status', rel"
                    "ation_name='IS_PROPERTY_OF', base_path='"
                    "Node/Parent',"
                ),
                "  value_format=str, value_cardinality=1)",
                "```",
            ),
        ),
        carrier(
            "CA-R-5", "Node/Parent/Child", body("Rule for Child."), form="Rule"
        ),
        carrier(
            "CA-D-6",
            "Node/Parent/Child",
            body("Delivery for Child."),
            role="Delivery",
            form="Markdown",
        ),
    ]


def carriers_2_3():
    return [
        carrier(
            "CA-R-7",
            "Node/Unknown",
            body(
                "### Formal Claim",
                "```python",
                "# model",
                (
                    "property_rule(address='Node/Unknown.Stat"
                    "us', value_format='string', values='1')"
                ),
                "```",
            ),
            form="Rule",
        ),
    ]


def carriers_3_1():
    return [
        carrier("CA-R-1", "Atom", body("Atom declaration.")),
        carrier("CA-R-2", "Atom.Status", body("Status declaration.")),
        carrier("CA-R-3", "Projection", body("Projection declaration.")),
    ]


def carriers_3_2():
    return [
        carrier("CA-R-4", "Projection.Form", body("Form declaration.")),
        carrier(
            "CA-R-5",
            "Atom.Status:Draft",
            body("Draft status rule."),
            form="Rule",
        ),
        carrier(
            "CA-R-6",
            "Projection/(.Form:=ApplicableMethodology)",
            body("Projection form rule."),
            form="Rule",
        ),
    ]


def carriers_3_3():
    return [
        carrier(
            "CA-R-7",
            "Atom.Kind:Unknown",
            body("Unknown property rule."),
            form="Rule",
        ),
        carrier(
            "CA-M-8",
            "Method/PlanProcess",
            body("Method evidence."),
            role="Method",
            form="Policy",
        ),
    ]


def carriers_4_1():
    return [
        carrier(
            "CA-R-1", "ANECHOIC <+ MODEL <+ Node", body("Node declaration.")
        ),
        carrier(
            "CA-R-2",
            "ANECHOIC <+ MODEL <+ Node.Status",
            body("Status declaration."),
        ),
        carrier(
            "CA-R-3",
            "ANECHOIC <+ MODEL <+ Node//Example",
            body("Example declaration."),
        ),
    ]


def carriers_4_2():
    return [
        carrier(
            "CA-R-4",
            "ANECHOIC <+ MODEL <+ CFEL <+ Format",
            body("Format declaration."),
        ),
        carrier(
            "CA-R-5",
            "ANECHOIC <+ MODEL <+ CFEL <+ Relation//depends_on",
            body("Relation declaration."),
            form="Relation Definition",
        ),
        carrier(
            "CA-R-6",
            "ANECHOIC <+ STRUCTURE <+ Project",
            body("Project declaration."),
        ),
    ]


def carriers_4_3():
    return [
        carrier(
            "CA-R-7",
            "ANECHOIC <+ STRUCTURE <+ Project//anechoic",
            body("Project declaration context."),
            form="Scope Unit Declaration",
        ),
        carrier(
            "CA-R-8",
            "ANECHOIC <+ MODEL <+ Node",
            body("Node rule."),
            form="Rule",
        ),
        carrier(
            "CA-R-9",
            "ANECHOIC <+ MODEL <+ CFEL <+ Relation//depends_on",
            body("Relation rule."),
            form="Rule",
        ),
    ]


def carriers_4_4():
    return [
        carrier(
            "CA-R-10",
            "ANECHOIC <+ STRUCTURE <+ Project//anechoic",
            body("Project rule."),
            form="Rule",
        ),
        carrier(
            "CA-R-11",
            "ANECHOIC <+ MODEL <+ Projection",
            body("Projection declaration."),
        ),
        carrier(
            "CA-R-12",
            "ANECHOIC <+ MODEL <+ Named Selection",
            body("Selection declaration."),
        ),
    ]


def carriers_4_5():
    return [
        carrier(
            "CA-R-13",
            "ANECHOIC <+ MODEL <+ (Node, Node.**)",
            body("Node scope."),
            form="Rule",
        ),
        carrier(
            "CA-R-14",
            "ANECHOIC <+ MODEL <+ (Node, Node.**)",
            body("Node scope."),
            form="Rule",
        ),
        carrier(
            "CA-R-15",
            "ANECHOIC <+ STRUCTURE <+ Projection//PROJECT_SCOPE_UNIT_GRAPH",
            body("Projection context."),
            form="Rule",
        ),
    ]


def carriers_4_6():
    return [
        carrier(
            "CA-R-16",
            "ANECHOIC <+ STRUCTURE <+ Projection//PROJECT_SCOPE_UNIT_GRAPH",
            body("Projection context."),
            form="Rule",
        ),
        carrier(
            "CA-R-17",
            "ANECHOIC <+ STRUCTURE <+ Named Selection//Extension Sources",
            body("Selection context."),
            form="Rule",
        ),
    ]
