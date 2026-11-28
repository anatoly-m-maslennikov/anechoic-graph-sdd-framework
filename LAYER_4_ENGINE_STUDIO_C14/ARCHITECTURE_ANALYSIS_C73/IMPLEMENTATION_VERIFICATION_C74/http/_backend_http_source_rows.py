"""Build observations from verified backend source locations."""


def build_rows(
    success_status,
    success_line,
    invalid_status,
    json_line,
    rejection_line,
    input_status,
    input_line,
    internal_status,
    unexpected_line,
):
    rows = [
        ("success", "result", success_status, success_line, "success"),
        (
            "invalid_input",
            "typed_error",
            invalid_status,
            json_line,
            "invalid_json",
        ),
        (
            "invalid_input",
            "typed_error",
            invalid_status,
            rejection_line,
            "invalid_envelope",
        ),
        (
            "invalid_input",
            "typed_error",
            input_status,
            input_line,
            "tool_input_validation",
        ),
        (
            "internal_error",
            "typed_error",
            internal_status,
            unexpected_line,
            "unexpected",
        ),
    ]
    return _as_observations(rows)


def _as_observations(rows):
    return [
        {
            "outcome": name,
            "envelope": kind,
            "status_code": status,
            "source_line": line,
            "case": case,
        }
        for name, kind, status, line, case in rows
    ]
