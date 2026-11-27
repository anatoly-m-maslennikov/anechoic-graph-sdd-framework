"""Fixture cases for lifecycle process tests."""


def _scenarios(UNKNOWN):
    return _scenarios_a(UNKNOWN) + _scenarios_b(UNKNOWN)


def _scenarios_a(UNKNOWN):
    return [
        (
            {
                "write_state": "known",
                "projection": {"state": "blocked"},
                "lifecycle": {
                    "outcome": "blocked",
                    "errors": [{"code": "write_blocked"}],
                },
            },
            "blocked",
            [{"code": "write_blocked"}],
        ),
        (
            {
                "write_state": "known",
                "projection": {"state": "ready"},
                "lifecycle": {"outcome": "blocked", "warnings": ["wait"]},
            },
            "blocked",
            [
                {
                    "code": "backend_failure",
                    "message": "Lifecycle operation failed.",
                }
            ],
        ),
    ]


def _scenarios_b(UNKNOWN):
    return [
        (
            {
                "write_state": "known",
                "projection": {"state": "ready"},
                "lifecycle": {
                    "outcome": "failed",
                    "requested_input": {"target": {"error": "required"}},
                },
            },
            "failed",
            [
                {
                    "code": "invalid_input",
                    "field": "target",
                    "message": "required",
                }
            ],
        ),
        (
            {"write_state": "unknown", "projection": {"state": "ready"}},
            "failed",
            [UNKNOWN],
        ),
        (
            {
                "write_state": "known",
                "projection": {
                    "state": "failed",
                    "error": {"code": "projection_failed"},
                },
                "lifecycle": {"outcome": "completed"},
            },
            "failed",
            [{"code": "projection_failed"}],
        ),
    ]


def check_failures(self, UNKNOWN):
    scenarios = _scenarios(UNKNOWN)
    for outcome, status, errors in scenarios:
        self.jobs.response = {"result": outcome}
        value = self.call("atom_lifecycle_archive", {"target": {}})["result"][
            "value"
        ]
        self.assertEqual((status, errors), (value["status"], value["errors"]))
    self.jobs.response = {
        "error": {"code": "lifecycle_active", "message": "busy"}
    }
    self.assertEqual(
        "lifecycle_active",
        self.call("atom_lifecycle_archive", {"target": {}})["error"]["code"],
    )
    check_invalid_failures(self, UNKNOWN)


def check_invalid_failures(self, UNKNOWN):
    missing_error = {
        "write_state": "known",
        "projection": {"state": "failed"},
        "lifecycle": {"outcome": "completed"},
    }
    blocked = {
        "write_state": "known",
        "projection": {"state": "blocked"},
        "lifecycle": {"outcome": "completed"},
    }
    unknown_blocked = {
        **blocked,
        "write_state": "unknown",
        "lifecycle": {"outcome": "blocked"},
    }
    for response in (
        {"result": {"write_state": "known"}},
        {"result": missing_error},
        {"result": blocked},
        {"result": unknown_blocked},
        b"not JSON",
    ):
        self.jobs.response = response
        value = self.call("atom_lifecycle_archive", {"target": {}})["result"][
            "value"
        ]
        self.assertEqual([UNKNOWN], value["errors"])


def tool_cases():
    return {
        "atom_lifecycle_create_draft": {
            "newAtom": {"body": "text", "extra": [1, None]}
        },
        "atom_lifecycle_update": {"sourceCurrent": {}},
        "atom_lifecycle_promote_draft": {
            "target": {},
            "targetStatus": "active",
        },
        "atom_lifecycle_change_status": {
            "target": {},
            "targetStatus": "active",
        },
        "atom_lifecycle_archive": {"target": {}},
        "atom_lifecycle_create_asset": {"newAtom": {}},
        "atom_lifecycle_direct_update": {"target": {}, "changes": {}},
    }
