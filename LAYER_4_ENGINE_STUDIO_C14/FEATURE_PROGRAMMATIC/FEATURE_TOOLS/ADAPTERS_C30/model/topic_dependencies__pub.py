"""Validate the reviewed Atom Dependencies Declaration."""

from hashlib import sha256


DEPENDENCIES_CHECK_SOURCE_SHA256 = (
    "b4a849957602a21e516d6c026fff931dfe737a5dc3ec57a5b6a6627cf22a20dd"
)


def validate_dependencies_claim(declaration):
    "Check the exact reviewed native contract without executing its callback."
    args = declaration.get("arguments", {})
    check = declaration.get("instance_check")
    if (
        declaration.get("kind") != "entity"
        or args.get("entity_name") != "Dependencies"
        or args.get("base_path") != "Atom.Header.Context.Topics"
        or args.get("relation_name") != "IS_PROPERTY_OF"
        or not check
        or check.get("name") != "dependencies_are_distinct"
        or check.get("parameter_type") != "Atom"
        or declaration.get("imports", {}).get("Atom") != "anechoic.model"
        or sha256(check["source"].encode()).hexdigest()
        != DEPENDENCIES_CHECK_SOURCE_SHA256
        or args.get("property_occurrence_cardinality")
        != {"minimum": 0, "maximum": 1}
        or args.get("value_format") != "str"
        or args.get("value_cardinality") != {"minimum": 0, "maximum": None}
        or args.get("dependent_property_cardinality") != 0
        or len(args) != 8
    ):
        raise ValueError(
            "instance_check requires the typed Atom Dependencies validator"
        )
    return check
