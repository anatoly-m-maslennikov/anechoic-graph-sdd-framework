"""Lower a scoped node-constraints class through the existing static parser."""

import ast
import re

_DOTTED_FIELDS = {
    "model_relations": "model_relation_constraints",
    "instance_relations": "instance_relation_constraints",
    "population_unique": "population_unique_constraints",
    "instance_check": "instance_check",
}
_ALLOWED = {*_DOTTED_FIELDS.values(), "bearer"}


def _lower_relation_targets(fields, imported, addresses):
    for field in (
        "model_relation_constraints",
        "instance_relation_constraints",
    ):
        if (relations := fields.get(field)) is None:
            continue
        if not isinstance(relations, ast.Dict):
            raise ValueError(f"{field} requires a dictionary")
        for constraint in relations.values:
            if not isinstance(constraint, ast.Dict):
                raise ValueError("Relation constraint requires a dictionary")
            _lower_constraint_targets(constraint, imported, addresses)


def lower_node_constraints(text, subject, addresses):
    cls, imports, functions = _parse_constraints(text, subject)
    imported = {
        alias.name
        for item in imports
        if item.module == "anechoic.model"
        for alias in item.names
        if not alias.asname
    }
    if "NodeConstraints" not in imported:
        raise ValueError("NodeConstraints must be imported")
    fields = _constraint_fields(cls)
    bearer = fields.pop("bearer", None)
    if (
        not isinstance(bearer, ast.Name)
        or bearer.id not in imported
        or bearer.id not in addresses
    ):
        raise ValueError("NodeConstraints requires an imported known bearer")
    path = addresses[bearer.id]
    if subject != "MODEL//ANECHOIC <+ " + path + ".Constraints":
        raise ValueError("NodeConstraints bearer does not match its scope")
    _lower_relation_targets(fields, imported, addresses)
    return _render_constraints(text, imports, functions, fields, path)


def _constraint_fields(cls):
    fields = {}
    for item in cls.body:
        if not isinstance(item, ast.Assign) or len(item.targets) != 1:
            raise ValueError("NodeConstraints body requires assignments")
        match item.targets[0]:
            case ast.Name(id=name):
                pass
            case ast.Attribute(
                value=ast.Attribute(
                    value=ast.Name(id="node"), attr="constraints"
                ),
                attr=field,
            ):
                name = _DOTTED_FIELDS.get(field)
            case _:
                raise ValueError("NodeConstraints body requires assignments")
        if name in fields or name not in _ALLOWED:
            raise ValueError("unsupported NodeConstraints field")
        fields[name] = item.value
    return fields


def _lower_constraint_targets(constraint, imported, addresses):
    for key, value in zip(constraint.keys, constraint.values, strict=True):
        if (
            isinstance(key, ast.Constant)
            and key.value == "target_entity_paths"
        ):
            if not isinstance(value, (ast.Tuple, ast.List)):
                raise ValueError(
                    "target_entity_paths requires Model class references"
                )
            for index, target in enumerate(value.elts):
                if (
                    not isinstance(target, ast.Name)
                    or target.id not in imported
                    or target.id not in addresses
                ):
                    raise ValueError(
                        "target_entity_paths requires imported known "
                        "Model classes"
                    )
                value.elts[index] = ast.Constant(addresses[target.id])


def _render_constraints(text, imports, functions, fields, path):
    display = re.split(r"/+", path)[-1]
    prefix = []
    for item in imports:
        if item.level or item.module not in {
            "anechoic.model",
            "anechoic.formal_claims",
        }:
            raise ValueError("unsupported NodeConstraints import")
        names = [a for a in item.names if a.name != "NodeConstraints"]
        if names:
            prefix.append(
                ast.unparse(
                    ast.ImportFrom(module=item.module, names=names, level=0)
                )
            )
    prefix.append("from anechoic.formal_claims import declare_entity")
    prefix.extend(ast.get_source_segment(text, item) for item in functions)
    args = ", ".join(
        f"{name}={ast.unparse(value)}" for name, value in fields.items()
    )
    prefix.append(
        f"declare_entity(entity_name={display + ' Constraints'!r}, "
        f"constraints_for={path!r}" + (", " + args if args else "") + ")"
    )
    return "\n\n".join(prefix) + "\n"


def _parse_constraints(text, subject):
    if not subject or not subject.endswith(".Constraints"):
        raise ValueError(
            "NodeConstraints requires its canonical Constraints scope"
        )
    tree = ast.parse(text)
    classes = [item for item in tree.body if isinstance(item, ast.ClassDef)]
    imports = [item for item in tree.body if isinstance(item, ast.ImportFrom)]
    functions = [
        item for item in tree.body if isinstance(item, ast.FunctionDef)
    ]
    if (
        len(tree.body) != len(classes) + len(imports) + len(functions)
        or len(classes) != 1
    ):
        raise ValueError("unsupported NodeConstraints statements")
    cls = classes[0]
    if (
        cls.decorator_list
        or cls.keywords
        or len(cls.bases) != 1
        or not isinstance(cls.bases[0], ast.Name)
        or cls.bases[0].id != "NodeConstraints"
    ):
        raise ValueError("expected NodeConstraints class")
    return cls, imports, functions
