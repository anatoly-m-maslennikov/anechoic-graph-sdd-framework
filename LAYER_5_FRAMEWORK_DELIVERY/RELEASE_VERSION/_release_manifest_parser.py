"""Parse a native Project Manifest without executing its claim."""

import ast

from markdown_it import MarkdownIt
import yaml


def read_atom_header(text: str) -> tuple[dict, str]:
    text = text.replace("\r\n", "\n")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        raise ValueError("Missing YAML frontmatter")
    front, body = text[4:].split("\n---\n", 1)
    depth = 0
    for count, event in enumerate(yaml.parse(front, Loader=yaml.SafeLoader), 1):
        if isinstance(event, yaml.events.AliasEvent):
            raise ValueError("YAML aliases are unsupported")
        if isinstance(event, (yaml.events.MappingStartEvent, yaml.events.SequenceStartEvent)):
            depth += 1
        if isinstance(event, (yaml.events.MappingEndEvent, yaml.events.SequenceEndEvent)):
            depth -= 1
        if depth > 64 or count > 100_000:
            raise ValueError("YAML exceeds the parser safety ceiling")
    node = yaml.compose(front, Loader=yaml.SafeLoader)
    pending = [node]
    while pending:
        current = pending.pop()
        if isinstance(current, yaml.MappingNode):
            keys = [key.value for key, _ in current.value
                    if isinstance(key, yaml.ScalarNode) and key.tag == "tag:yaml.org,2002:str"]
            if len(keys) != len(current.value) or len(set(keys)) != len(keys):
                raise ValueError("YAML keys must be unique strings")
            pending.extend(child for pair in current.value for child in pair)
        elif isinstance(current, yaml.SequenceNode):
            pending.extend(current.value)
    metadata = yaml.safe_load(front)
    if not isinstance(metadata, dict):
        raise ValueError("Atom header must be a mapping")
    return metadata, body


def _literal(node: ast.AST):
    for item in ast.walk(node):
        if isinstance(item, ast.Dict):
            keys = [ast.literal_eval(key) if key is not None else None for key in item.keys]
            if any(not isinstance(key, str) for key in keys) or len(keys) != len(set(keys)):
                raise ValueError("Claim mapping keys must be unique strings")
    return ast.literal_eval(node)


def _claim(body: str) -> dict:
    headings, claims = [], []
    tokens = MarkdownIt("commonmark").parse(body)
    for index, token in enumerate(tokens):
        if token.type == "heading_open":
            level = int(token.tag[1:])
            headings = [item for item in headings if item[0] < level]
            headings.append((level, tokens[index + 1].content.strip().casefold()))
        elif (token.type == "fence" and token.info.strip().casefold() == "python"
              and tuple(name for _, name in headings) == ("claim", "formal claim")):
            claims.append(token.content)
    if len(claims) != 1:
        raise ValueError("Expected one Python Formal Claim")
    tree = ast.parse(claims[0])
    imports = (("anechoic.formal_claims", "declare_entity"), ("anechoic.model", "ProjectManifest"))
    statements = tree.body
    if len(statements) != 3 or any(
        not isinstance(stmt, ast.ImportFrom) or stmt.level or stmt.module != module
        or len(stmt.names) != 1 or stmt.names[0].name != name or stmt.names[0].asname is not None
        for stmt, (module, name) in zip(statements[:2], imports)
    ):
        raise ValueError("Unsupported Project Manifest claim")
    expression = statements[2]
    if not isinstance(expression, ast.Expr) or not isinstance(expression.value, ast.Call):
        raise ValueError("Unsupported Project Manifest declaration")
    call = expression.value
    if not isinstance(call.func, ast.Name) or call.func.id != "declare_entity" or call.args:
        raise ValueError("Unsupported Project Manifest declaration")
    args = {arg.arg: arg.value for arg in call.keywords}
    if len(args) != len(call.keywords) or set(args) != {"entity_name", "instance"}:
        raise ValueError("Unsupported Project Manifest declaration arguments")
    instance = args["instance"]
    if (_literal(args["entity_name"]) != "Project Manifest" or not isinstance(instance, ast.Call)
            or not isinstance(instance.func, ast.Name) or instance.func.id != "ProjectManifest" or instance.args):
        raise ValueError("Expected a ProjectManifest instance")
    fields = {arg.arg: _literal(arg.value) for arg in instance.keywords}
    if (len(fields) != len(instance.keywords) or not {"name", "prefix"} <= fields.keys()
            or fields.keys() - {"name", "prefix", "parameters", "lens_whitelist"}):
        raise ValueError("Unsupported ProjectManifest fields")
    return fields


