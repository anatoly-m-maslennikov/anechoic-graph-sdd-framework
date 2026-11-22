"""Test Suite public interface."""

if __package__:
    from .run_full_test_suite import main as _main
else:
    from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.run_full_test_suite import main as _main

if __name__ == "__main__":
    raise SystemExit(_main())
