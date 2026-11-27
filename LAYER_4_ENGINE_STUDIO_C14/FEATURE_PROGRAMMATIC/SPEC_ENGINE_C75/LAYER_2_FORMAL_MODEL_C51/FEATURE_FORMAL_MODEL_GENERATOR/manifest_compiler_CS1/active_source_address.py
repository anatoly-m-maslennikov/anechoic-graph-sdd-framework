"""Check Continuant Model addresses."""

import ast
from pathlib import PurePosixPath
from .....FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    CUSTOM_MODEL_DIRECTORY,
    parse_native_model_claim,
)
from .....FEATURE_TOOLS.ADAPTERS_C30.model_ontology_path__pub import (
    is_ontology_model_source,
)


def _check_continuant_address(
    source, scope, text, kind, addresses, claim=None
):
    path = PurePosixPath(source.rsplit("@", 1)[0])
    if not is_ontology_model_source(path) or path.parts[-3:-1] != (
        "_DOM",
        "CONT",
    ):
        if kind != "manifest_node" or path.parts[1:2] != (
            CUSTOM_MODEL_DIRECTORY,
        ):
            return
    local = scope.split(" <+ ", 1)[1]
    cls = next(
        item for item in ast.parse(text).body if isinstance(item, ast.ClassDef)
    )
    if kind == "manifest_node":
        if (
            local.rfind("//") >= 0
            and local.rfind("/") == local.rfind("//") + 1
        ):
            parent = local.rsplit("//", 1)[0]
            bases = {
                addresses.get(base.id)
                for base in cls.bases
                if isinstance(base, ast.Name)
            }
            if parent not in bases:
                raise ValueError(
                    f"{source}: Concern parent is not a direct node base"
                )
    else:
        _check_field_address(source, kind, addresses, claim, local)


def _check_field_address(source, kind, addresses, claim, local):
    if kind in {"manifest_property", "manifest_relation"}:
        args = parse_native_model_claim(claim)["arguments"]
        if kind == "manifest_relation":
            expected = (
                addresses.get("Relation", "Graph/Relation")
                + "//"
                + args["relation_name"]
            )
            valid = local == expected
        elif "entity_name" in args and args.get("entity_kind") == "Property":
            base = args["base_path"]
            suffix = base.partition(".")[2]
            paths = [base] + [
                path + ("." + suffix if suffix else "")
                for path in args.get("applies_to_entity_classes", ())
            ]
            valid = local in {
                path + "." + args["entity_name"] for path in paths
            }
        else:
            return
        if not valid:
            raise ValueError(
                f"{source}: Concern address does not match Formal Manifest"
            )
