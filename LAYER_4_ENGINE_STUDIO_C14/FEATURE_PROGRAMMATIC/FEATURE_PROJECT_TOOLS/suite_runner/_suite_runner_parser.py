"""Command-line arguments for the test suite."""

import argparse
from pathlib import Path


def _suite_parser(description):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--test-module", action="append", dest="test_modules", metavar="PATH"
    )
    parser.add_argument(
        "--phase",
        default="unit",
        choices=(
            "preflight",
            "static",
            "functional",
            "unit",
            "image",
            "image-tests",
            "canary",
        ),
    )
    parser.add_argument(
        "--functional-suite", choices=("full", "fast"), default="full"
    )
    parser.add_argument(
        "--image-suite", choices=("full", "fast"), default="full"
    )
    parser.add_argument(
        "--required",
        action="store_true",
        help="run the configured required host selection with the unit phase",
    )
    parser.add_argument("--candidate-image")
    parser.add_argument("--canary-package", type=Path)
    parser.add_argument("--canary-project-root", type=Path)
    parser.add_argument("--canary-selection")
    parser.add_argument("--run-id")
    return parser


