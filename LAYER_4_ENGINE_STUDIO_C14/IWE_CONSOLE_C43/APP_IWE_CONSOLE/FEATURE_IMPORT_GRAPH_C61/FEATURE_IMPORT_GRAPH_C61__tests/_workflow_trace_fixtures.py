def sample():
    return {
        "complete": True,
        "model": {
            "initial": "idle",
            "states": [
                {
                    "name": "idle",
                    "final": False,
                    "transitions": [
                        {
                            "event": "save",
                            "target": "done",
                            "expect": {
                                "kind": "effect",
                                "target": None,
                                "outcome": "ok",
                                "detail": {"id": 1},
                            },
                        }
                    ],
                },
                {"name": "done", "final": True, "transitions": []},
            ],
        },
        "events": [
            {
                "kind": "effect",
                "name": "save",
                "target": None,
                "outcome": "ok",
                "detail": {"id": 1, "extra": True},
            }
        ],
    }


def machine():
    def branch(target, **params):
        return {
            "target": target,
            "guard": {"type": "matchesTrace", "params": params},
        }

    return {
        "id": "flow",
        "initial": "start",
        "states": {
            "start": {
                "on": {
                    "NEXT": [
                        branch("done", kind="output", outcome="success"),
                        branch("start", kind="effect", outcome="retry"),
                    ]
                }
            },
            "done": {"type": "final"},
        },
    }


def correlation_machine():
    return {
        "id": "reply",
        "initial": "idle",
        "states": {
            "idle": {
                "on": {
                    "start": {
                        "to": "waiting",
                        "expect": {
                            "kind": "trigger",
                            "bind": {
                                "request": "id",
                                "generation": "generation",
                            },
                        },
                    }
                }
            },
            "waiting": {
                "on": {
                    "retry": {
                        "to": "waiting",
                        "expect": {
                            "kind": "effect",
                            "bind": {"request": "id"},
                        },
                    },
                    "finish": {
                        "to": "done",
                        "expect": {
                            "kind": "output",
                            "outcome": "ok",
                            "detail": {"sql": "current"},
                            "same_as": {
                                "reply_id": "request",
                                "generation": "generation",
                            },
                        },
                    },
                }
            },
            "done": {"type": "final"},
        },
    }


GUARD_PAIRS = [
    (
        {"kind": "output"},
        {"kind": "output", "outcome": "success"},
        True,
    ),
    ({"kind": "output", "target": None}, {"kind": "output"}, True),
    (
        {"kind": "output", "detail": {"a": 1}},
        {"kind": "output", "detail": {"a": 1, "b": 2}},
        True,
    ),
    (
        {"kind": "output", "detail": {"a": {"x": 1, "y": 2}}},
        {"kind": "output", "detail": {"a": {"y": 2, "x": 1}}},
        True,
    ),
    (
        {"kind": "output", "target": None},
        {"kind": "output", "target": "x"},
        False,
    ),
    (
        {"kind": "output", "detail": {"a": 1}},
        {"kind": "output", "detail": {"a": 2}},
        False,
    ),
    (
        {"kind": "output", "detail": {"a": {"x": 1}}},
        {"kind": "output", "detail": {"a": {"x": 1, "y": 2}}},
        False,
    ),
    (
        {"kind": "output", "detail": {"a": True}},
        {"kind": "output", "detail": {"a": 1}},
        False,
    ),
    (
        {"kind": "output", "detail": {"a": {"at_most": 45}}},
        {"kind": "output", "detail": {"a": 45}},
        True,
    ),
    (
        {"kind": "output", "detail": {"a": 45.0}},
        {"kind": "output", "detail": {"a": {"at_most": 45}}},
        True,
    ),
    (
        {"kind": "output", "detail": {"a": {"at_most": 45}}},
        {"kind": "output", "detail": {"a": 46}},
        False,
    ),
    (
        {"kind": "output", "detail": {"a": {"at_most": 45}}},
        {"kind": "output", "detail": {"a": True}},
        False,
    ),
    (
        {"kind": "output", "detail": {"a": {"at_most": 45}}},
        {"kind": "output", "detail": {"a": {"at_most": 2}}},
        True,
    ),
]
