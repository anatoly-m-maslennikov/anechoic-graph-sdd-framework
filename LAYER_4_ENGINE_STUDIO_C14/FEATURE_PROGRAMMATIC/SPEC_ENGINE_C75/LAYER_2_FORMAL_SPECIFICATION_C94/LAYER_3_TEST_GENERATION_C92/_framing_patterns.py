"""Build framing patterns and enforce the witness budget."""


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


