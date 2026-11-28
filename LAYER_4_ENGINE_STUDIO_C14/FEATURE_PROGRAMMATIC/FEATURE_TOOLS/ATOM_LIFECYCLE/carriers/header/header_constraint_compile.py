"""Compile and validate Header constraint records."""

from . import header_constraints__shared as owner


def _add_direct_cardinalities(args, path, selector, selected, source, records):
    if (occurrence := args.get("property_occurrence_cardinality")) in (0, 1):
        records.add(
            ("property", path, selector, selected, str(occurrence), source)
        )
    if (cardinality := args.get("value_cardinality")) is not None:
        records.add(
            (
                "value",
                path,
                selector,
                selected,
                owner.cardinality_bounds(cardinality),
                source,
            )
        )


def native_header_records(code, source):
    declaration = owner.parse_native_model_claim(code)
    if declaration is None or declaration["kind"] != "entity":
        return set()
    args = declaration["arguments"]
    target = owner._native_header_target(args, source)
    if target is None:
        return set()
    path, selector, selected = target
    records = set()
    _add_direct_cardinalities(args, path, selector, selected, source, records)
    if children := args.get("allowed_dependent_property_names"):
        low, high = owner.cardinality_bounds(
            args["dependent_property_cardinality"]
        )
        if high is not None:
            names = tuple(sorted(owner._path(child) for child in children))
            records.add(
                (
                    "children",
                    path,
                    selector,
                    selected,
                    (low, high, *names),
                    source,
                )
            )
    if (
        cardinality := args.get("dependent_property_value_cardinality")
    ) is not None:
        records.add(
            (
                "value",
                path + ".*",
                selector,
                selected,
                owner.cardinality_bounds(cardinality),
                source,
            )
        )
    if path not in {"role", "form", "status"}:
        for value in args.get("allowed_values", ()):
            records.add(("domain", path, selector, selected, value, source))
    return records


def _record_fields(row, source_ids):
    if not isinstance(row, dict) or set(row) != {
        "kind",
        "path",
        "selector",
        "selected",
        "value",
        "source",
    }:
        raise ValueError("invalid Header constraint record")
    kind, path, selector, selected, value, source = (
        row[k]
        for k in (
            "kind",
            "path",
            "selector",
            "selected",
            "value",
            "source",
        )
    )
    if (
        any(
            not isinstance(v, str)
            for v in (kind, path, selector, selected, source)
        )
        or kind not in {"property", "domain", "children", "value"}
        or not owner.re.fullmatch(
            r"[a-z0-9_]+(?:\.[a-z0-9_]+)*(?:\.\*)?"
            if kind == "value"
            else r"[a-z0-9_]+(?:\.[a-z0-9_]+)*",
            path,
        )
        or selector not in {"", "role", "form"}
        or bool(selector) != bool(selected)
        or source not in source_ids
    ):
        raise ValueError("invalid Header constraint record")
    return kind, path, selector, selected, value, source


def _record_value(kind, value):
    if kind == "value":
        if (
            not isinstance(value, (list, tuple))
            or len(value) != 2
            or type(value[0]) is not int
            or value[0] < 0
            or (
                value[1] is not None
                and (type(value[1]) is not int or value[1] < value[0])
            )
        ):
            raise ValueError("invalid Header value constraint")
        value = tuple(value)
    elif kind == "children":
        if (
            not isinstance(value, (list, tuple))
            or len(value) < 3
            or any(type(bound) is not int for bound in value[:2])
            or not 0 <= value[0] <= value[1]
            or any(
                not isinstance(name, str)
                or not owner.re.fullmatch(r"[a-z0-9_]+", name)
                for name in value[2:]
            )
        ):
            raise ValueError("invalid Header child constraint")
        value = tuple(value)
    elif (
        not isinstance(value, str)
        or not value
        or (kind == "property" and value not in {"0", "1"})
    ):
        raise ValueError("invalid Header constraint value")
    return value


def load_header_constraints(records, source_ids):
    if not isinstance(records, list):
        raise ValueError("invalid Header constraint records")
    seen, properties, domains, children, values = set(), [], {}, [], []
    for row in records:
        kind, path, selector, selected, value, source = _record_fields(
            row, source_ids
        )
        value = _record_value(kind, value)
        key = (kind, path, selector, selected, value, source)
        if key in seen:
            raise ValueError("duplicate Header constraint record")
        seen.add(key)
        if kind == "property":
            properties.append((path, selector, selected, value, source))
        elif kind == "children":
            children.append((path, selector, selected, value, source))
        elif kind == "value":
            values.append((path, selector, selected, value, source))
        else:
            domains.setdefault((path, selector, selected, source), set()).add(
                value
            )
    return owner.HeaderConstraints(
        tuple(properties),
        tuple(
            (*key[:3], frozenset(items), key[3])
            for key, items in sorted(domains.items())
        ),
        tuple(children),
        tuple(values),
    )
