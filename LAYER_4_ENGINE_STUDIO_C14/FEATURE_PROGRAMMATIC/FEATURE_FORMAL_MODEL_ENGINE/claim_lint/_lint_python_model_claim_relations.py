"""Check Relation names in static Python Claims."""

import ast


def _check_relations(
    text,
    relation_names,
    relation_aliases,
    require_declared_aliases,
    path,
    first_line,
):
    known_aliases = (
        {}
        if require_declared_aliases
        else {
            "<+": "CONTAINS",
            ">|": "HAS_AXIS",
            ";>": "IS_ORDERED_RIGHT_BEFORE",
        }
    )
    known_aliases.update(relation_aliases or {})
    for item in ast.parse(text).body:
        call = item.value
        if not isinstance(call, ast.Call) or not isinstance(
            call.func, ast.Name
        ):
            continue
        helper = call.func.id
        args = {kw.arg: ast.literal_eval(kw.value) for kw in call.keywords}
        name = args["name"] if helper == "relation" else None
        symbol = {
            "composition": "<+",
            "classify": ">|",
            "order_before": ";>",
        }.get(helper)
        if helper == "classify" and args.get("notation") == "relation":
            name, symbol = "HAS_AXIS", None
        if symbol:
            name = known_aliases.get(symbol)
            if not name:
                return (
                    f"{path}:{first_line + call.lineno - 1}:{call.col_offset + 1}: unresolved Relation alias: {symbol}",
                )
        if name and name != "*" and name not in relation_names:
            return (
                f"{path}:{first_line + call.lineno - 1}:{call.col_offset + 1}: unknown Relation: {name}",
            )
    return ()


def _project_bound_names(bound_names, exact_addresses):
    for name, target in tuple(bound_names.items()):
        for address in exact_addresses:
            if not address.startswith(target + "."):
                continue
            projected = name + address[len(target) :]
            if projected in exact_addresses or (
                projected in bound_names and bound_names[projected] != address
            ):
                continue
            bound_names[projected] = address
