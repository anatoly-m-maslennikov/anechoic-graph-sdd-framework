"""Retry only known transient source-currentness failures with capped backoff."""
import time


_CURRENTNESS = (
    "Native Project carriers changed during capture",
    "Native Project carriers changed during generation",
    "Project source or dependency inputs changed during capture",
)


class CurrentnessRetry:
    def __init__(self):
        self.due = None
        self.delay = .25

    def observe(self, outcome):
        if outcome.get("state") == "succeeded":
            self.due, self.delay = None, .25
        elif any(text in outcome.get("message", "") for text in _CURRENTNESS):
            self.due = time.monotonic() + self.delay
            self.delay = min(self.delay * 2, 5.0)
        else:
            self.due, self.delay = None, .25

    def ready(self):
        return self.due is not None and time.monotonic() >= self.due
