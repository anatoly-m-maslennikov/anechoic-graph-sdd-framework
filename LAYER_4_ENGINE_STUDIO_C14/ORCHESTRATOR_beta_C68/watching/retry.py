"Retry only known transient source-currentness failures with capped backoff."

import time


COVERAGE_RECOVERED = "coverage_recovered"
_CURRENTNESS = (
    "Native Project carriers changed during capture",
    "Native Project carriers changed during generation",
)


def source_changed(outcome):
    return any(text in outcome.get("message", "") for text in _CURRENTNESS)


class CurrentnessRetry:
    def __init__(self):
        self.due = None
        self.delay = 0.25

    def observe(self, outcome):
        if outcome.get("state") == "succeeded":
            self.due, self.delay = None, 0.25
        elif source_changed(outcome):
            self.due = time.monotonic() + self.delay
            self.delay = min(self.delay * 2, 5.0)
        else:
            self.due, self.delay = None, 0.25

    def ready(self):
        return self.due is not None and time.monotonic() >= self.due
