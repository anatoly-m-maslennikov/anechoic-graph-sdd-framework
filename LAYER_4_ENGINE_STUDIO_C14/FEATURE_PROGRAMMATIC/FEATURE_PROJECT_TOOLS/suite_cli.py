"""Dispatch Test Suite CLI phases and the release canary."""

import json
import sys

from .functional_suite import valid_test_request


def run_phase(root, arguments, report, run_full_suite):
    phase = arguments.phase
    image = arguments.candidate_image
    canary_args = (arguments.canary_package, arguments.canary_selection, arguments.run_id)
    canary_options = (*canary_args, arguments.canary_project_root)
    if phase == "image-tests":
        if (any(value is not None for value in canary_options) or
                not valid_test_request("image", image, arguments.test_modules, arguments.required)):
            print("Image-tests phase requires only an exact candidate image", file=sys.stderr)
            return 1
        return run_full_suite(root, phase="image", candidate_image=image, report=report)
    if phase in ("image", "canary"):
        if (not all(canary_args) or not valid_test_request("image", image, arguments.test_modules, arguments.required)):
            print(f"{phase.capitalize()} phase requires an exact candidate image and all canary arguments", file=sys.stderr)
            return 1
        return _run_canary_phase(root, arguments, report, run_full_suite)
    if image is not None or any(value is not None for value in canary_options):
        print("Image arguments require the image phase", file=sys.stderr)
        return 1
    return run_full_suite(
        root, test_modules=tuple(arguments.test_modules) if arguments.test_modules is not None else None,
        phase=phase, required=arguments.required, report=report,
    )


def _run_canary_phase(root, arguments, report, run_full_suite):
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
    if arguments.phase == "image":
        status = run_full_suite(root, phase="image", candidate_image=arguments.candidate_image, report=report)
    else:
        status = run_full_suite(root, phase="canary", report=report)
    if status:
        return status
    report["step"] = "canary"
    try:
        from ._release_canary import verify_candidate_image

        endpoint = verify_candidate_image(
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
