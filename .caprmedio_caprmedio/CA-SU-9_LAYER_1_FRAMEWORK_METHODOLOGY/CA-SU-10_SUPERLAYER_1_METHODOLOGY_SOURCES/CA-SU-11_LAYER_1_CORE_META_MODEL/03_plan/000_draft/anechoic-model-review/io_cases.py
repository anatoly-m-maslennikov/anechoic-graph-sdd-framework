"""Executable review model for Component I/O allowances."""

from collections.abc import Mapping


DIRECTIONS = ("input", "output")
ALL = "all"
_MISSING = object()


def _field(owner):
    if owner is None:
        return _MISSING
    if isinstance(owner, Mapping):
        if "io_allowance" in owner:
            return owner["io_allowance"]
        if any(direction in owner for direction in DIRECTIONS):
            return owner
        return _MISSING
    return owner


def _authored_field(owner):
    value = _field(owner)
    return None if value is _MISSING else value


def _direction_value(field, direction, validate_keys=True):
    if field is _MISSING:
        return _MISSING
    if isinstance(field, Mapping):
        unknown = set(field) - set(DIRECTIONS)
        if validate_keys and unknown:
            raise ValueError(f"unknown io_allowance directions: {sorted(unknown)}")
        return field.get(direction, _MISSING)
    return field


def _normalise(value):
    if value is _MISSING:
        return _MISSING
    if value is None:
        raise ValueError("io_allowance cannot be null")
    if value is False:
        return frozenset()
    if value is True:
        raise ValueError("io_allowance must use 'all', false, a list, or directions")
    if value == ALL:
        return ALL
    if isinstance(value, str):
        raise ValueError("io_allowance channels must be a list")
    try:
        return frozenset(value)
    except TypeError as error:
        raise ValueError(f"invalid io_allowance value: {value!r}") from error


def _chain(owners):
    if isinstance(owners, Mapping) or owners is None:
        return (owners,)
    if isinstance(owners, (list, tuple)) and all(
        isinstance(owner, Mapping) or owner is None for owner in owners
    ):
        return tuple(owners)
    return (owners,)


def _resolve_chain(owners):
    result = {}
    for direction in DIRECTIONS:
        for owner in owners:
            value = _normalise(_direction_value(_field(owner), direction))
            if value is not _MISSING:
                result[direction] = value
                break
        else:
            result[direction] = ALL
    return result


def resolve_allowance(owners, *nearer_owners):
    """Resolve owners ordered nearest-first, with an absent field per direction.

    Each owner may be a Manifest mapping containing ``io_allowance`` or an
    allowance value.  A missing direction continues to the next owner.
    """
    chain = (owners, *nearer_owners) if nearer_owners else _chain(owners)
    return _resolve_chain(chain)


def _intersect(left, right):
    if left == ALL:
        return right
    if right == ALL:
        return left
    return left & right


def narrow_allowance(effective, package=_MISSING):
    """Narrow a Package without silently broadening its Component.

    A Package's explicit ``all`` means all channels already inherited in that
    direction; it does not grant channels the Component cannot use.
    """
    if package is _MISSING:
        return dict(effective)
    if isinstance(package, Mapping) and "io_allowance" in package:
        package = package["io_allowance"]
    narrowed = {}
    for direction in DIRECTIONS:
        parent_value = _normalise(effective.get(direction, ALL))
        package_value = _normalise(_direction_value(package, direction))
        if package_value is _MISSING or package_value == ALL:
            narrowed[direction] = parent_value
            continue
        if parent_value != ALL:
            extra = package_value - parent_value
            if extra:
                channel = sorted(extra)[0]
                raise ValueError(
                    f"package io_allowance broadens {direction} with channel {channel!r}"
                )
        narrowed[direction] = _intersect(parent_value, package_value)
    return narrowed


def allows(effective, direction, channel):
    """Return whether a resolved allowance permits one direction and channel."""
    if direction not in DIRECTIONS:
        raise ValueError(f"unknown I/O direction: {direction!r}")
    value = _normalise(effective.get(direction, ALL))
    return value == ALL or channel in value


def _policy_allowance(policy):
    if not isinstance(policy, Mapping):
        raise TypeError("policy must be a mapping")
    return policy.get("allowance", policy)


def validate_policy(authored, ancestors, policy, package=_MISSING):
    """Check a selected Policy without changing the authored allowance."""
    ancestor_chain = () if ancestors is None else _chain(ancestors)
    effective = _resolve_chain((authored, *ancestor_chain))
    if package is not _MISSING:
        effective = narrow_allowance(effective, package)
    limit = _policy_allowance(policy)
    policy_name = policy.get("id", policy.get("name", policy.get("policy", "<unnamed>")))
    reason = policy.get("reason", "effective allowance exceeds policy")
    violations = []
    for direction in DIRECTIONS:
        actual = effective[direction]
        permitted = _normalise(_direction_value(limit, direction, validate_keys=False))
        if permitted is _MISSING:
            permitted = ALL
        if actual == ALL and permitted != ALL:
            channels = (ALL,)
        elif actual == ALL or permitted == ALL:
            channels = ()
        else:
            channels = tuple(sorted(actual - permitted))
        violations.extend(
            {
                "direction": direction,
                "channel": channel,
                "policy": policy_name,
                "reason": reason,
            }
            for channel in channels
        )
    return {
        "ok": not violations,
        "authored_allowance": _authored_field(authored),
        "effective_allowance": effective,
        "violations": tuple(violations),
    }


def import_allowed(library, effective, library_channels):
    """Reject a mapped library only when its channel is denied both ways."""
    channel = library_channels.get(library)
    if channel is None:
        return True
    channels = (channel,) if isinstance(channel, str) else tuple(channel)
    return any(
        allows(effective, direction, item)
        for item in channels
        for direction in DIRECTIONS
    )


def rest_direction(method):
    """Classify a REST method by its I/O direction."""
    method = method.upper()
    if method in {"GET", "HEAD", "OPTIONS"}:
        return "input"
    if method in {"POST", "PUT", "PATCH", "DELETE"}:
        return "output"
    raise ValueError(f"unsupported REST method: {method!r}")


def run_cases():
    parent = {"io_allowance": ["db", "api"]}
    child = {"io_allowance": {"input": ["db"]}}
    assert resolve_allowance([child, parent]) == {
        "input": frozenset({"db"}),
        "output": frozenset({"db", "api"}),
    }
    assert resolve_allowance([{}, {}]) == {"input": ALL, "output": ALL}
    assert resolve_allowance([{"io_allowance": ALL}, {"io_allowance": False}]) == {
        "input": ALL,
        "output": ALL,
    }
    assert resolve_allowance([{"io_allowance": False}, parent]) == {
        "input": frozenset(),
        "output": frozenset(),
    }
    assert resolve_allowance([{"io_allowance": []}, parent]) == {
        "input": frozenset(),
        "output": frozenset(),
    }
    assert resolve_allowance(
        [{"io_allowance": {"input": ["db"]}}, {"io_allowance": False}]
    )["output"] == frozenset()
    package = narrow_allowance(resolve_allowance([parent]), {"output": []})
    assert package == {
        "input": frozenset({"db", "api"}),
        "output": frozenset(),
    }
    assert not allows(package, "output", "db")
    assert narrow_allowance(resolve_allowance([parent]), {"input": ALL}) == {
        "input": frozenset({"db", "api"}),
        "output": frozenset({"db", "api"}),
    }
    try:
        narrow_allowance(resolve_allowance([parent]), {"input": ["cache"]})
    except ValueError as error:
        assert "input" in str(error) and "cache" in str(error)
    else:
        raise AssertionError("a Package must not broaden its Component allowance")
    try:
        resolve_allowance([{"io_allowance": {"self": ["db"]}}, parent])
    except ValueError as error:
        assert "self" in str(error)
    else:
        raise AssertionError("unknown directional allowance keys must fail")
    try:
        resolve_allowance([{"io_allowance": "db"}])
    except ValueError:
        pass
    else:
        raise AssertionError("scalar channel shorthand must fail")
    policy = {
        "id": "P-no-api-output",
        "allowance": {"input": ["db", "api"], "output": ["db"]},
        "reason": "the adapter must not send API traffic",
    }
    authored = {"io_allowance": ["db", "api"]}
    result = validate_policy(authored, [parent], policy)
    assert not result["ok"]
    assert result["authored_allowance"] == ["db", "api"]
    assert result["violations"] == (
        {
            "direction": "output",
            "channel": "api",
            "policy": "P-no-api-output",
            "reason": "the adapter must not send API traffic",
        },
    )
    assert authored == {"io_allowance": ["db", "api"]}
    assert validate_policy(
        child,
        [parent],
        {"allowance": {"input": ["db"], "output": ["db", "api"]}},
    )["ok"]
    denied = {"input": frozenset(), "output": frozenset()}
    library_channels = {"sqlite3": "db", "requests": "api"}
    assert not import_allowed("sqlite3", denied, library_channels)
    assert import_allowed(
        "sqlite3", {"input": frozenset({"db"}), "output": frozenset()}, library_channels
    )
    assert import_allowed("unknown", denied, library_channels)
    assert all(rest_direction(method) == "input" for method in ("GET", "HEAD", "OPTIONS"))
    assert all(rest_direction(method) == "output" for method in ("POST", "PUT", "PATCH", "DELETE"))
    try:
        rest_direction("TRACE")
    except ValueError:
        pass
    else:
        raise AssertionError("unsupported REST methods must fail")
    print("I/O allowance review-model acceptance cases passed")


if __name__ == "__main__":
    run_cases()
