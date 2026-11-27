"""Build finite framing witnesses from normalized claims."""

from ..LAYER_2_SPEC_READING_C83.SPECIFICATION_MODEL_C85._package__shared \
    import normalize_spec  # fmt: skip


def _patterns(claim, role):
    if role == "contract":
        groups = ([claim["delimiter"]], claim["line_endings"])
    elif role == "solution":
        groups = (claim["opening_prefixes"], claim["closing_prefixes"])
    else:
        raise ValueError("invalid framing role")
    _check_witness_budget(groups, role)
    if role == "contract":
        delimiter = bytes(claim["delimiter"])
        endings = [bytes(value) for value in claim["line_endings"]]
        return (
            [delimiter + ending for ending in endings],
            [
                before + delimiter + after
                for before in endings
                for after in endings
            ],
        )
    return (
        [bytes(value) for value in claim["opening_prefixes"]],
        [bytes(value) for value in claim["closing_prefixes"]],
    )


def _check_witness_budget(groups, role):
    if any(len(group) > 8 for group in groups):
        raise ValueError("framing witness budget exceeded")
    lengths = [[len(pattern) for pattern in group] for group in groups]
    if (
        any(length > 32 for group in lengths for length in group)
        or sum(map(sum, lengths)) > 128
    ):
        raise ValueError("framing witness budget exceeded")
    if role == "contract":
        delimiter = lengths[0][0]
        openings = [delimiter + ending for ending in lengths[1]]
        closings = [
            before + delimiter + after
            for before in lengths[1]
            for after in lengths[1]
        ]
    else:
        openings, closings = lengths
    budget = (
        2
        + sum(length + 1 for length in openings + closings)
        + sum(
            6 + 2 * close + min(opening, close)
            for opening in openings
            for close in closings
        )
    )
    if budget > 512:
        raise ValueError("framing witness budget exceeded")


def framing_expectation(raw, claim, role):
    openings, closings = _patterns(claim, role)
    opening = next(
        (len(value) for value in openings if raw.startswith(value)), None
    )
    if opening is None:
        return None, None
    for pos in range(opening - 1, len(raw)):
        if role == "contract":
            endings = [bytes(value) for value in claim["line_endings"]]
            delimiter = bytes(claim["delimiter"])
            before = next(
                (value for value in endings if raw.startswith(value, pos)),
                None,
            )
            if before is None or not raw.startswith(
                delimiter, pos + len(before)
            ):
                continue
            end = pos + len(before) + len(delimiter)
            after = next(
                (value for value in endings if raw.startswith(value, end)),
                None,
            )
            stop = end + len(after) if after is not None else None
        else:
            close = next(
                (value for value in closings if raw.startswith(value, pos)),
                None,
            )
            stop = pos + len(close) if close is not None else None
        if stop is not None:
            return (opening, pos, stop), raw[stop:]
    return None, None


def framing_witnesses(claim, role, *, include_overlap_cases=False):
    """Generate a finite set of byte witnesses for the declared delimiters."""
    openings, closings = _patterns(claim, role)
    cases = {b"", b"\x00", *openings, *closings}
    for pattern in openings + closings:
        cases.update(pattern[:i] for i in range(len(pattern)))
    for opening in openings:
        for closing in closings:
            for middle in (b"", b"\x00"):
                base = opening + middle + closing
                cases.update(
                    (base, base + b"\x00\xff", base + closing + b"\xff")
                )
                cases.update(
                    base[: len(opening) + len(middle) + i]
                    for i in range(len(closing))
                )
            for overlap in range(1, min(len(opening), len(closing)) + 1):
                if opening[-overlap:] == closing[:overlap]:
                    base = opening + closing[overlap:]
                    cases.add(base + b"\xff")
                    if include_overlap_cases:
                        cases.update((base, base[:-1], base + b"\x00\xff"))
    if len(cases) > 512:
        raise ValueError("framing witness budget exceeded")
    return sorted(cases)


def _framing_cases(claims):
    witnesses = {
        raw
        for role in ("contract", "solution")
        for raw in framing_witnesses(
            claims[role], role, include_overlap_cases=True
        )
    }
    delimiter = bytes(claims["contract"]["delimiter"])
    ending = bytes(claims["contract"]["line_endings"][0])
    witnesses.add(
        delimiter + ending + b"\x00" + ending + delimiter + b" " + ending
    )
    if len(witnesses) > 512:
        raise ValueError("framing witness budget exceeded")
    cases = []
    for raw in sorted(witnesses):
        case = {"input": list(raw)}
        for role, label in (
            ("contract", "manifest"),
            ("solution", "solution"),
        ):
            bounds, body = framing_expectation(raw, claims[role], role)
            case[label] = {
                "bounds": list(bounds) if bounds is not None else None,
                "body": list(body) if body is not None else None,
            }
        cases.append(case)
    return cases


def build_python_framing_cases(model):
    """Build finite byte cases from the admitted framing claims."""
    if not model.get("embedded_contract"):
        raise ValueError("an embedded Contract is required")
    for role in ("contract", "solution"):
        if [language for language, _ in model[role]["claims"]] != [
            "python framing"
        ]:
            raise ValueError(f"expected one {role} framing claim")
    normalized = normalize_spec(model)
    errors = normalized["issues"] + [
        issue
        for issue in normalized["unresolved"]
        if issue["field"] in ("contract", "solution")
    ]
    if errors:
        raise ValueError(f"invalid framing source: {errors}")
    claims = normalized["claims"]
    cases = _framing_cases(claims)
    boundaries = claims.get("manifest", {}).get("boundaries") or {}
    io = boundaries.get("io") if isinstance(boundaries, dict) else None
    servers = io.get("server") if isinstance(io, dict) else None
    framing = (
        servers.get("carrier_body_framing")
        if isinstance(servers, dict)
        else None
    )
    operations = (
        framing.get("operations") if isinstance(framing, dict) else None
    )
    return {
        "sources": {
            "manifest": model["manifest"]["source"],
            "solution": model["solution"]["source"],
        },
        "operations": operations,
        "cases": cases,
        "unresolved": normalized["unresolved"],
    }
