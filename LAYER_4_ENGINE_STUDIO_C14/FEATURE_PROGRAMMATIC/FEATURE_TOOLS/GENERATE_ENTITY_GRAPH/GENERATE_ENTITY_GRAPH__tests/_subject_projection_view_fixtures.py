"""Fixtures for Subject projection views."""

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.\
    GENERATE_ENTITY_GRAPH__shared import (
        build_subject_projection_data,
    )  # fmt: skip


def carrier(atom_id, subject, body, *, role="Requirement", form="Declaration"):
    return {
        "source": {
            "atom_id": atom_id,
            "version": 1,
            "path": f"sources/{atom_id}.md",
        },
        "subjects": {"active": subject, "passive": []},
        "body": body,
        "read_view": {"content_role": role, "type": form},
    }


def claim(*lines):
    return "## Claim\n\n" + "\n".join(lines) + "\n"


def native_property(name, base, *arguments):
    return claim(
        "```python",
        "from anechoic.formal_claims import Cardinality, declare_entity",
        f"declare_entity(entity_name={name!r}, "
        f"relation_name='IS_PROPERTY_OF', base_path={base!r},",
        *(f"    {argument}," for argument in arguments),
        ")",
        "```",
    )


def carriers():
    return _base_carriers() + _additional_carriers()


def _base_carriers():
    return [
        carrier(
            "CA-R-NODE",
            "Node",
            claim(
                "```python",
                "from anechoic.formal_claims impo"
                "rt declare_entity, Cardinality",
                "declare_entity(entity_name='Stat"
                "us', relation_name='IS_PROPERTY_"
                "OF', base_path='Node', property_"
                "occurrence_cardinality=1, value_"
                "format='string', value_cardinali"
                "ty=Cardinality(minimum=1, maximu"
                "m=None))",
                "```",
            ),
        ),
        carrier("CA-R-CHILD", "Node/Child", claim("Child declaration.")),
        carrier(
            "CA-R-STATUS",
            "Node.Status",
            claim(
                "```python",
                "from anechoic.formal_claims impo"
                "rt declare_entity, Cardinality",
                "declare_entity(entity_name='Stat"
                "us', relation_name='IS_PROPERTY_"
                "OF', base_path='Node', property_"
                "occurrence_cardinality=1, value_"
                "format='string', value_cardinali"
                "ty=Cardinality(minimum=1, maximu"
                "m=None))",
                "```",
            ),
        ),
    ]


def _additional_carriers():
    return [
        carrier(
            "CA-R-CHILD-STATUS",
            "Node/Child.Status",
            claim(
                "```python",
                "from anechoic.formal_claims impo"
                "rt declare_entity, Cardinality",
                "declare_entity(entity_name='Stat"
                "us', relation_name='IS_PROPERTY_"
                "OF', base_path='Node/Child', pro"
                "perty_occurrence_cardinality=Car"
                "dinality(minimum=0, maximum=1), "
                "value_format='integer', value_ca"
                "rdinality=2)",
                "```",
            ),
        ),
        carrier(
            "CA-M-POISON",
            "Node.Poison",
            claim(
                "### Formal Claim",
                "",
                "```python",
                "from anechoic.formal_claims import declare_entity",
                "declare_entity(entity_name='Pois"
                "on', relation_name='IS_PROPERTY_"
                "OF', base_path='Node')",
                "```",
            ),
            role="Method",
            form="Policy",
        ),
    ]


def projection(*, namespace=False):
    rows = carriers()
    if namespace:
        rows.append(
            carrier(
                "CA-R-NS", "ANECHOIC <+ MODEL", claim("Namespace declaration.")
            )
        )
    data = build_subject_projection_data(rows)
    if namespace:
        data.setdefault("namespaces", []).append(
            {
                "subject": "ANECHOIC <+ MODEL",
                "source": {"atom_id": "CA-R-NS", "version": 1},
            }
        )
    return data
