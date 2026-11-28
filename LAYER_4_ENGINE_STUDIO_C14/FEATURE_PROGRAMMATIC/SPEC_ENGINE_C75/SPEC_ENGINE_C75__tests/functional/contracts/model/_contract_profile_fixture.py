"""Build trace machines for Contract profile tests."""

from ..model import test_contract_profiles as runtime


def _edge(destination, kind, *, target=None, outcome=None, detail=None):
    expectation = {"kind": kind}
    expectation.update(
        {
            key: value
            for key, value in (
                ("target", target),
                ("outcome", outcome),
                ("detail", detail),
            )
            if value is not None
        }
    )
    return {
        "target": destination,
        "guard": {"type": "matchesTrace", "params": expectation},
    }


def _machine(binding, success, failure, *, forbidden=None):
    states = {
        "idle": {
            "on": {
                "start": runtime._edge(
                    "start", "trigger", target="suite", detail=binding
                )
            }
        },
        "start": {
            "on": {
                "approve": runtime._edge(
                    "approved", "effect", target="review", outcome="passed"
                ),
                "fail": runtime._edge(
                    "done", "output", outcome="failed", detail=failure
                ),
            }
        },
        "approved": {
            "on": {
                "render": runtime._edge(
                    "ready", "effect", target="draft", outcome="ready"
                )
            }
        },
        "ready": {
            "on": {
                "return": runtime._edge(
                    "done", "output", outcome="succeeded", detail=success
                )
            }
        },
        "done": {"type": "final"},
    }
    if forbidden is not None:
        states["abort"] = {"on": {"fail": states["start"]["on"]["fail"]}}
        states["start"]["on"]["fail"] = runtime._edge(
            "abort", "effect", target=forbidden, outcome="attempted"
        )
    return {"id": "suite", "initial": "idle", "states": states}
