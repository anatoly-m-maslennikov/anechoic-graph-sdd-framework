"""Test Suite public interface."""

if __package__:
    from .test_suite__shared import main as _main
else:
    from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.test_suite__shared import main as _main

if __name__ == "__main__":
    raise SystemExit(_main())
