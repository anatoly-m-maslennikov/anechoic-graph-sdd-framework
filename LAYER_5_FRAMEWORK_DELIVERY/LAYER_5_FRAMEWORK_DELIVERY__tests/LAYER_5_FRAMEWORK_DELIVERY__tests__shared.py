"""Shared data and invocation helper for release CLI tests."""

from contextlib import redirect_stdout
import io
import json

import LAYER_5_FRAMEWORK_DELIVERY__shared as release

DRAFT = {
    "base_commit": "a" * 40,
    "head_commit": "b" * 40,
    "changes": [
        {"title": "Host command", "details": "Route through the host CLI.", "evidence": ["AN-T-1"], "highlight": True}
    ],
}



class ReleaseCliFixture:
    def invoke(self, arguments: list[str]) -> tuple[int, dict[str, object]]:
        output = io.StringIO()
        with redirect_stdout(output):
            status = release.main(arguments)
        return status, json.loads(output.getvalue())

