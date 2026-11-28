"""Validate and materialize Model class fields."""

import ast


def _reject_quoted_annotations(node: ast.ClassDef) -> None:
    """Use postponed references; preserve strings in Literal values."""

    def validate(part: ast.AST) -> None:
        if (
            isinstance(part, ast.Subscript)
            and isinstance(part.value, ast.Name)
            and part.value.id == "Literal"
        ):
            literals = (
                part.slice.elts
                if isinstance(part.slice, ast.Tuple)
                else (part.slice,)
            )
            if any(not isinstance(value, ast.Constant) for value in literals):
                raise ValueError(
                    f"{node.name}: Literal requires constant values"
                )
            return
        if isinstance(part, ast.Constant) and isinstance(part.value, str):
            raise ValueError(f"{node.name}: use an unquoted Python annotation")
        for child in ast.iter_child_nodes(part):
            validate(child)

    for field in node.body:
        if isinstance(field, ast.AnnAssign):
            validate(field.annotation)


def _materialize_field_metadata(
    node: ast.ClassDef, fields: list[dict]
) -> None:
    """Keep parsed field constraints as generated Python literals."""
    metadata_by_field = {
        field["name"]: field.get("field", {}).get("metadata")
        for field in fields
    }
    for item in node.body:
        if not isinstance(item, ast.AnnAssign) or not isinstance(
            item.value, ast.Call
        ):
            continue
        for keyword in item.value.keywords:
            if keyword.arg == "metadata":
                keyword.value = ast.parse(
                    repr(metadata_by_field[item.target.id]), mode="eval"
                ).body
