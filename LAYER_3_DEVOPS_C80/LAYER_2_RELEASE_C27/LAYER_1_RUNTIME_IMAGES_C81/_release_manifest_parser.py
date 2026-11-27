"""Parse a native Project Manifest without executing its claim."""

import ast

from markdown_it import MarkdownIt
import yaml


def _validate_yaml(front: str) -> None:
    depth = 0
    for count, event in enumerate(
        yaml.parse(front, Loader=yaml.SafeLoader), 1
    ):
        if isinstance(event, yaml.events.AliasEvent):
            raise ValueError("YAML aliases are unsupported")
        if isinstance(
            event,
            (yaml.events.MappingStartEvent, yaml.events.SequenceStartEvent),
        ):
            depth += 1
        if isinstance(
            event, (yaml.events.MappingEndEvent, yaml.events.SequenceEndEvent)
        ):
            depth -= 1
        if depth > 64 or count > 100_000:
            raise ValueError("YAML exceeds the parser safety ceiling")
    node = yaml.compose(front, Loader=yaml.SafeLoader)
    pending = [node]
    while pending:
        current = pending.pop()
        if isinstance(current, yaml.MappingNode):
            keys = [
                key.value
                for key, _ in current.value
                if isinstance(key, yaml.ScalarNode)
                and key.tag == "tag:yaml.org,2002:str"
            ]
            if len(keys) != len(current.value) or len(set(keys)) != len(keys):
                raise ValueError("YAML keys must be unique strings")
            pending.extend(child for pair in current.value for child in pair)
        elif isinstance(current, yaml.SequenceNode):
            pending.extend(current.value)


def read_atom_header(text: str) -> tuple[dict, str]:
    text = text.replace("\r\n", "\n")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        raise ValueError("Missing YAML frontmatter")
    front, body = text[4:].split("\n---\n", 1)
    _validate_yaml(front)
    metadata = yaml.safe_load(front)
    if not isinstance(metadata, dict):
        raise ValueError("Atom header must be a mapping")
    return metadata, body


def _literal(node: ast.AST):
    for item in ast.walk(node):
        if isinstance(item, ast.Dict):
            keys = [
                ast.literal_eval(key) if key is not None else None
                for key in item.keys
            ]
            if any(not isinstance(key, str) for key in keys) or len(
                keys
            ) != len(set(keys)):
                raise ValueError("Claim mapping keys must be unique strings")
    return ast.literal_eval(node)


def _formal_claim(body: str) -> tuple[str, bool]:
    headings, claims = [], []
    tokens = MarkdownIt("commonmark").parse(body)
    for index, token in enumerate(tokens):
        if token.type == "heading_open":
            level = int(token.tag[1:])
            headings = [item for item in headings if item[0] < level]
            headings.append(
                (level, tokens[index + 1].content.strip().casefold())
            )
        elif token.type == "fence":
            path = tuple(name for _, name in headings)
            if path == ("formal manifest",):
                if token.info.strip().casefold() not in {
                    "python", "python anechoic-edsl"
                }:
                    raise ValueError("Unsupported Formal Manifest fence")
                claims.append((token.content, True))
            elif (
                path == ("claim", "formal claim")
                and token.info.strip().casefold() == "python"
            ):
                claims.append((token.content, False))
    if len(claims) != 1:
        raise ValueError("Expected one Python Formal Manifest or Formal Claim")
    return claims[0]


def _validate_claim_imports(statements: list[ast.stmt]) -> None:
    imports = (
        ("anechoic.formal_claims", "declare_entity"),
        ("anechoic.model", "ProjectManifest"),
    )
    if len(statements) != 3 or any(
        not isinstance(stmt, ast.ImportFrom)
        or stmt.level
        or stmt.module != module
        or len(stmt.names) != 1
        or stmt.names[0].name != name
        or stmt.names[0].asname is not None
        for stmt, (module, name) in zip(statements[:2], imports, strict=True)
    ):
        raise ValueError("Unsupported Project Manifest claim")


def _claim(body: str) -> dict:
    source, direct = _formal_claim(body)
    statements = ast.parse(source).body
    if direct:
        if (
            len(statements) != 2
            or not isinstance(statements[0], ast.ImportFrom)
            or statements[0].level
            or statements[0].module != "anechoic.model"
            or len(statements[0].names) != 1
            or statements[0].names[0].name != "ComponentManifest"
            or statements[0].names[0].asname is not None
        ):
            raise ValueError("Unsupported Component Manifest import")
        expression = statements[1]
    else:
        _validate_claim_imports(statements)
        expression = statements[2]
    if not isinstance(expression, ast.Expr) or not isinstance(
        expression.value, ast.Call
    ):
        raise ValueError("Unsupported Project Manifest declaration")
    call = expression.value
    if direct:
        instance = call
    else:
        instance = _legacy_instance(call)
    if (
        not isinstance(instance, ast.Call)
        or not isinstance(instance.func, ast.Name)
        or instance.func.id
        != ("ComponentManifest" if direct else "ProjectManifest")
        or instance.args
    ):
        raise ValueError("Expected a Manifest instance")
    fields = {arg.arg: _literal(arg.value) for arg in instance.keywords}
    if (
        len(fields) != len(instance.keywords)
        or not {"name", "prefix"} <= fields.keys()
        or fields.keys() - {"name", "prefix", "parameters", "lens_whitelist"}
    ):
        raise ValueError("Unsupported Manifest fields")
    return fields


def _legacy_instance(call: ast.Call) -> ast.AST:
    if (
        not isinstance(call.func, ast.Name)
        or call.func.id != "declare_entity"
        or call.args
    ):
        raise ValueError("Unsupported Project Manifest declaration")
    args = {arg.arg: arg.value for arg in call.keywords}
    if len(args) != len(call.keywords) or set(args) != {
        "entity_name",
        "instance",
    }:
        raise ValueError("Unsupported Project Manifest declaration arguments")
    instance = args["instance"]
    if _literal(args["entity_name"]) != "Project Manifest":
        raise ValueError("Expected a ProjectManifest instance")
    return instance
