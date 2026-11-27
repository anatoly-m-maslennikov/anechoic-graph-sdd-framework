"""Build state finding rows for publication and lint tests."""


def state_finding_row(
    path,
    action,
    line,
    status,
    *,
    witness=None,
    dead_end=False,
    violations="[]",
    detail="",
):
    return (
        f"module:{path}",
        path,
        "python",
        action,
        line,
        witness,
        status,
        dead_end,
        "[]",
        violations,
        detail,
    )
