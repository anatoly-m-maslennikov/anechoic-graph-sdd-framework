import ast
import re


def _name(value):
    if not isinstance(value, str) or not re.fullmatch(
        r"[A-Za-z][A-Za-z0-9_]*", value
    ):
        raise ValueError("shape names must be simple ASCII identifiers")
    return value


def parse_shape(source, role):
    tree = ast.parse(source)
    if role == "contract":
        return _parse_contract(tree)
    return _parse_solution(tree, role)


def _parse_contract(tree):
    if len(tree.body) != 1 or not isinstance(tree.body[0], ast.Expr):
        raise ValueError("expected one shape contract")
    call = tree.body[0].value
    if (
        not isinstance(call, ast.Call)
        or not isinstance(call.func, ast.Name)
        or call.func.id != "declare_shape_contract"
        or call.args
        or len(call.keywords) != 3
        or {k.arg for k in call.keywords} != {"record", "fields", "subtype"}
    ):
        raise ValueError("expected record, fields and subtype")
    args = {k.arg: k.value for k in call.keywords}
    fields_node = args["fields"]
    if not isinstance(fields_node, ast.Dict) or not fields_node.keys:
        raise ValueError("expected nonempty literal fields")
    pairs = [
        (ast.literal_eval(k), ast.literal_eval(v))
        for k, v in zip(fields_node.keys, fields_node.values)
    ]
    fields = {_name(k): _name(v) for k, v in pairs}
    if len(fields) != len(pairs):
        raise ValueError("duplicate field")
    record, subtype = (
        _name(ast.literal_eval(args["record"])),
        _name(ast.literal_eval(args["subtype"])),
    )
    if record == subtype or {record, subtype} & set(fields.values()):
        raise ValueError("record, subtype and field types must be distinct")
    return {
        "record": record,
        "fields": fields,
        "subtype": subtype,
        "base": record,
    }


def _parse_solution(tree, role):
    if (
        role != "solution"
        or len(tree.body) != 2
        or any(not isinstance(c, ast.ClassDef) for c in tree.body)
    ):
        raise ValueError("expected one record and one subtype class")
    record, subtype = tree.body
    if (
        record.name == subtype.name
        or record.bases
        or record.keywords
        or record.decorator_list
        or getattr(record, "type_params", ())
        or getattr(subtype, "type_params", ())
        or subtype.keywords
        or subtype.decorator_list
        or len(subtype.bases) > 1
        or any(not isinstance(base, ast.Name) for base in subtype.bases)
        or len(subtype.body) != 1
        or not isinstance(subtype.body[0], ast.Pass)
    ):
        raise ValueError("unsupported shape class syntax")
    fields = _solution_fields(record)
    base = _name(subtype.bases[0].id) if subtype.bases else None
    if base not in (None, record.name):
        raise ValueError("subtype base must be the record")
    if {record.name, subtype.name} & set(fields.values()):
        raise ValueError("record, subtype and field types must be distinct")
    return {
        "record": _name(record.name),
        "fields": fields,
        "subtype": _name(subtype.name),
        "base": base,
    }


def _solution_fields(record):
    fields = {}
    for field in record.body:
        if isinstance(field, ast.Pass) and len(record.body) == 1:
            continue
        if (
            not isinstance(field, ast.AnnAssign)
            or not isinstance(field.target, ast.Name)
            or not isinstance(field.annotation, ast.Name)
            or field.value is not None
            or not field.simple
        ):
            raise ValueError(
                "record fields must be typed names without values"
            )
        name = _name(field.target.id)
        if name in fields:
            raise ValueError("duplicate field")
        fields[name] = _name(field.annotation.id)
    return fields


def manifest_shape(boundaries):
    """Extract the supported bundled record and subtype, if present."""
    if not isinstance(boundaries, dict) or not isinstance(
        boundaries.get("io"), dict
    ):
        return None
    io = boundaries["io"]
    server = io.get("server")
    legacy = isinstance(server, dict) and "bundled_model_classes" in server
    if "class_shapes" in io:
        if legacy:
            raise ValueError("Declare class_shapes once")
        classes = io["class_shapes"]
    elif legacy:
        declaration = server["bundled_model_classes"]
        if not isinstance(declaration, dict) or set(declaration) != {
            "classes"
        }:
            raise ValueError("Bundled model classes must contain only classes")
        classes = declaration["classes"]
    else:
        return None
    return _manifest_classes(classes)


def _manifest_classes(classes):
    if not isinstance(classes, dict) or len(classes) != 2:
        raise ValueError("Expected one record and one subtype class")
    records = [
        (name, value["fields"])
        for name, value in classes.items()
        if isinstance(value, dict) and set(value) == {"fields"}
    ]
    subtypes = [
        (name, value["base"])
        for name, value in classes.items()
        if isinstance(value, dict) and set(value) == {"base"}
    ]
    if len(records) != 1 or len(subtypes) != 1:
        raise ValueError("Expected record fields and subtype base only")
    record, fields = records[0]
    subtype, base = subtypes[0]
    record, subtype, base = _name(record), _name(subtype), _name(base)
    if not isinstance(fields, dict) or not fields:
        raise ValueError("Expected nonempty record fields")
    fields = {_name(key): _name(value) for key, value in fields.items()}
    if (
        record == subtype
        or base != record
        or {record, subtype} & set(fields.values())
    ):
        raise ValueError("Invalid record, subtype or field types")
    return {
        "record": record,
        "fields": fields,
        "subtype": subtype,
        "base": base,
    }
