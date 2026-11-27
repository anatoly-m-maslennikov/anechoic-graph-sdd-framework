"""Validate named performance obligations without executing their source."""

import ast
import math


def _fields(node, literal_string):
    if not isinstance(node, ast.Dict):
        raise ValueError("expected a performance mapping")
    keys = [literal_string(key) for key in node.keys]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate performance field")
    return dict(zip(keys, node.values))


def _positive(node, *, integer=False):
    value = ast.literal_eval(node)
    types = (int,) if integer else (int, float)
    if (
        type(value) not in types
        or value <= 0
        or (type(value) is float and not math.isfinite(value))
    ):
        raise ValueError("expected a positive finite performance value")
    return value


def parse_performance(node, literal_string):
    fields = _fields(node, literal_string)
    if set(fields) != {"resources", "measurements"}:
        raise ValueError("performance requires resources and measurements")
    resources = _fields(fields["resources"], literal_string)
    if set(resources) != {"cpu_cores", "ram_mib", "disk_mib"}:
        raise ValueError("performance requires CPU, RAM and disk resources")
    resources = {
        key: _positive(value, integer=key != "cpu_cores")
        for key, value in resources.items()
    }
    rows = _fields(fields["measurements"], literal_string)
    if not rows:
        raise ValueError("expected named performance measurements")
    measurements = {}
    for name, body in rows.items():
        if not name.strip():
            raise ValueError("empty performance measurement name")
        row = _fields(body, literal_string)
        base = {"from", "to", "workload"}
        latency = base | {"statistic", "max_ms"}
        throughput = base | {"min_requests_per_second"}
        if set(row) not in (latency, throughput):
            raise ValueError("invalid performance bound")
        parsed = {key: literal_string(row[key]) for key in base}
        if (
            any(not value.strip() for value in parsed.values())
            or parsed["from"] == parsed["to"]
        ):
            raise ValueError("invalid performance milestones or workload")
        if set(row) == latency:
            statistic = literal_string(row["statistic"])
            if statistic not in ("p10", "p50", "p90", "p95", "max"):
                raise ValueError("invalid latency statistic")
            parsed.update(
                statistic=statistic,
                max_ms=_positive(row["max_ms"], integer=True),
            )
        else:
            parsed["min_requests_per_second"] = _positive(
                row["min_requests_per_second"]
            )
        measurements[name] = parsed
    return {"resources": resources, "measurements": measurements}
