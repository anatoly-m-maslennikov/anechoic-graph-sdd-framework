"""Validate the fixed C88 public witness report."""

_ROWS = [
    ["matched", "unresolved", "matched"],
    ["matched", "unresolved", "conflicting"],
    ["matched", "conflicting"],
]


def _expected_report(pins):
    values = {
        "manifest": {"a": 2, "m": 8, "z": 1},
        "contract": {"a": 2, "z": 1},
        "solution": {"a": 2, "z": 3},
    }
    pairs = [
        ("manifest", "contract"),
        ("manifest", "solution"),
        ("contract", "solution"),
    ]
    directions = {}
    for (left, right), statuses in zip(pairs, _ROWS, strict=True):
        facts = [
            {
                "key": key,
                "left": value,
                "right": values[right].get(key),
                "status": status,
            }
            for (key, value), status in zip(
                values[left].items(), statuses, strict=True
            )
        ]
        status = "conflicting" if "conflicting" in statuses else "unresolved"
        directions[f"{left}_{right}"] = {"status": status, "facts": facts}
    sources = {**pins, "contract": pins["manifest"]}
    return {
        "status": "conflicting",
        "sources": sources,
        "directions": directions,
    }


def _valid_fact(fact):
    statuses = ("matched", "conflicting", "unresolved")
    return (
        isinstance(fact, dict)
        and fact.keys() == {"key", "left", "right", "status"}
        and isinstance(fact["key"], str)
        and type(fact["left"]) is int
        and (fact["right"] is None or type(fact["right"]) is int)
        and fact["status"] in statuses
    )


def _valid_report(actual, expected):
    statuses = ("matched", "conflicting", "unresolved")
    if (
        not isinstance(actual, dict)
        or actual.keys() != expected.keys()
        or actual["sources"] != expected["sources"]
        or actual["status"] not in statuses
    ):
        return False
    if any(
        type(pin.get("version")) is not int
        for pin in actual["sources"].values()
    ):
        return False
    directions = actual["directions"]
    if (
        not isinstance(directions, dict)
        or directions.keys() != expected["directions"].keys()
    ):
        return False
    for name, reference in expected["directions"].items():
        row = directions[name]
        if (
            not isinstance(row, dict)
            or row.keys() != reference.keys()
            or row["status"] not in statuses
            or not isinstance(row["facts"], list)
            or len(row["facts"]) != len(reference["facts"])
            or not all(map(_valid_fact, row["facts"]))
        ):
            return False
    return True


def _result_status(observed, pins):
    if not isinstance(observed, dict) or observed.keys() != {
        "status",
        "report",
        "direction_order",
        "observations",
        "unresolved",
        "formal_path",
    }:
        raise ValueError("C88 witness did not return a complete public report")
    if observed["formal_path"] not in ("matched", "unresolved"):
        raise ValueError("C88 authored comparison evidence is invalid")
    if observed["direction_order"] != [
        "manifest_contract",
        "manifest_solution",
        "contract_solution",
    ]:
        raise ValueError("C88 witness has invalid direction order")
    if observed["observations"] != [
        "native join strings",
        "real Lean worker rows",
    ]:
        raise ValueError("C88 witness has invalid observation evidence")
    if observed["unresolved"] != [
        "Python facade initialization",
        "runtime effect events",
        "other inputs and effects",
    ]:
        raise ValueError("C88 witness has invalid unresolved evidence")
    actual, expected = observed["report"], _expected_report(pins)
    if not _valid_report(actual, expected):
        raise ValueError("C88 public report has invalid typed rows")
    if observed["status"] == "conflicting" and actual != expected:
        return "mismatch"
    if observed["formal_path"] != "matched":
        raise ValueError("C88 authored comparison path is unresolved")
    if observed["status"] == "matched" and actual == expected:
        return "no_mismatch_in_cases"
    raise ValueError("C88 witness result is inconsistent or incomplete")
