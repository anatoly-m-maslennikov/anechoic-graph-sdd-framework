"""Assertions for the full suite scheduler and image lifecycle."""

import threading
import time

from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS import (
    test_suite__shared as full,
)
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.release_image import (
    release_image__shared as docker,
)


def interrupt_when_queued(test, pending, ready, release, canceled, watchers):
    test.assertTrue(ready.wait(5))
    queued = [future for future in pending if not future.running()]
    queued_modules = [pending[future] for future in queued]
    test.assertEqual(6, len(queued))
    test.assertEqual(
        4,
        sum(
            not full._docker_module(test.case.root, module)
            for module in queued_modules
        ),
    )
    test.assertEqual(
        2,
        sum(
            full._docker_module(test.case.root, module)
            for module in queued_modules
        ),
    )

    def release_after_cancellation():
        deadline = time.monotonic() + 3
        while (
            not all(future.cancelled() for future in queued)
            and time.monotonic() < deadline
        ):
            time.sleep(0.01)
        if all(future.cancelled() for future in queued):
            canceled.set()
        release.set()

    watcher = threading.Thread(target=release_after_cancellation)
    watchers.append(watcher)
    watcher.start()
    raise KeyboardInterrupt


def assert_build_call(test, build, scratch):
    engine = docker.CODE_ROOT.parent / (
        "LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine"
    )
    args = build.args[0]
    expected = (
        "uv",
        "run",
        "--no-compile-bytecode",
        "--project",
        str(engine),
        "--locked",
        "--python",
        "3.14",
        "--managed-python",
        "--no-env-file",
        "python",
        "-B",
        "-P",
    )
    test.assertEqual(expected, args[: len(expected)])
    assert_build_environment(test, build.kwargs["env"])
    test.assertTrue(build.kwargs["check"])
    test.assertEqual(docker.CODE_ROOT, build.kwargs["cwd"])
    attempt = args[args.index("--attempt") + 1]
    test.assertRegex(attempt, r"^[0-9a-f]{32}$")
    boundary = ("-m", docker.IMAGE_CLI, "build")
    target = ("--project-root", str(test.root), "--attempt", attempt)
    offset = args.index("-m")
    test.assertEqual(
        (
            *boundary,
            *target,
            "--scratch",
            str(scratch),
            "--packaged-assets",
        ),
        args[offset:],
    )
    return attempt, offset


def assert_build_environment(test, env):
    test.assertEqual(str(docker.CODE_ROOT), env["PYTHONPATH"])
    test.assertEqual(
        str(docker.CODE_ROOT / ".venv-dev"), env["UV_PROJECT_ENVIRONMENT"]
    )
    test.assertNotIn("PYTHONHOME", env)
    test.assertNotIn("VIRTUAL_ENV", env)
    test.assertNotIn("UV_COMPILE_BYTECODE", env)
