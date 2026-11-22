"""Test Suite public interface."""

if __package__:
    from .run_full_test_suite import main as _main, run_full_suite
else:
    from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.run_full_test_suite import main as _main, run_full_suite

__all__ = ["run_full_suite"]

if __name__ == "__main__":
    raise SystemExit(_main())
