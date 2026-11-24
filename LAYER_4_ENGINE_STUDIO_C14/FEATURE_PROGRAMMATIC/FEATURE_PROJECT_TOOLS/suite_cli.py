"""Dispatch Test Suite CLI phases and the release canary."""

import json
import re
import sys

from . import _release_canary


def run_phase(root, arguments, report, run_full_suite):
    canary_args = (arguments.candidate_image, arguments.canary_package,
                   arguments.canary_selection, arguments.run_id)
    if arguments.phase == "image":
        if (not all(canary_args) or arguments.test_modules is not None or arguments.required or
                not re.fullmatch(r"sha256:[0-9a-f]{64}", arguments.candidate_image)):
            print("Image phase requires an exact candidate image and all canary arguments", file=sys.stderr)
            return 1
        try:
            selection = json.loads(arguments.canary_selection)
            canary_root = (arguments.canary_project_root or root).resolve(strict=True)
            if not canary_root.is_dir():
                raise ValueError(f"canary Project root is not a directory: {canary_root}")
        except (OSError, TypeError, ValueError) as error:
            report["error"] = str(error)
            print(f"Invalid canary input: {error}", file=sys.stderr)
            return 1
        report["canary_project_root"] = str(canary_root)
        status = run_full_suite(root, phase="image", candidate_image=arguments.candidate_image, report=report)
        if status:
            return status
        report["step"] = "canary"
        try:
            endpoint = _release_canary.verify_candidate_image(
                canary_root, arguments.canary_package, arguments.candidate_image,
                run_id=arguments.run_id, selection=selection,
            )
        except Exception as error:
            report["error"] = str(error)
            print(f"Canary failed: {error}", file=sys.stderr)
            return 1
        report["canary_endpoint"] = endpoint
        print(f"ANECHOIC_CANARY_ENDPOINT {endpoint}")
        return 0
    if arguments.canary_project_root is not None or any(value is not None for value in canary_args):
        print("Image arguments require the image phase", file=sys.stderr)
        return 1
    return run_full_suite(
        root, test_modules=tuple(arguments.test_modules) if arguments.test_modules is not None else None,
        phase=arguments.phase, required=arguments.required, report=report,
    )
