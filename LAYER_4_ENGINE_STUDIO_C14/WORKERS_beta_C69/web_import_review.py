"Bounded, non-executing review of captured JavaScript and TypeScript modules."

import json
import os
from pathlib import Path
import subprocess
import stat


def web_import_review(root, texts, occurrences):
    """Return source-located evaluation evidence from the captured graph."""
    root = Path(root)
    config_text, nested = _configuration(root, texts)
    links = [
        list(row)
        for row in occurrences
        if row[1].removeprefix("module:") in texts
    ]
    env = {
        key: value
        for key, value in os.environ.items()
        if key not in {"NODE_OPTIONS", "NODE_PATH"}
    }
    timeout = None if env.get("ANECHOIC_TEST_IMAGE_DEADLINES") == "0" else 60
    script = Path(__file__).with_name("web_import_review.ts")
    result = subprocess.run(
        ["node", str(script)],
        input=json.dumps(
            {
                "sources": texts,
                "occurrences": links,
                "config": config_text,
                "nested": nested,
            }
        ),
        text=True,
        capture_output=True,
        timeout=timeout,
        env=env,
        check=False,
    )
    if result.returncode:
        raise ValueError(f"Web import review failed: {result.stderr.strip()}")
    return [tuple(row) for row in json.loads(result.stdout)]


def _configuration(root, texts):
    config = root / "tsconfig.json"
    config_text = None
    try:
        flags = (
            os.O_RDONLY
            | getattr(os, "O_NOFOLLOW", 0)
            | getattr(os, "O_NONBLOCK", 0)
        )
        if not config.is_symlink():
            fd = os.open(config, flags)
            with os.fdopen(fd, "r", encoding="utf-8") as handle:
                if stat.S_ISREG(os.fstat(handle.fileno()).st_mode):
                    config_text = handle.read()
    # fmt: off
    except OSError, UnicodeError:
        pass
    # fmt: on
    nested = []
    for name in texts:
        parent = Path(name).parent
        if parent.is_absolute() or ".." in parent.parts:
            nested.append(name)
            continue
        while parent != Path("."):
            if (
                (root / parent).is_symlink()
                or (root / parent / "tsconfig.json").is_symlink()
                or (root / parent / "tsconfig.json").exists()
            ):
                nested.append(name)
                break
            parent = parent.parent
    return config_text, nested
