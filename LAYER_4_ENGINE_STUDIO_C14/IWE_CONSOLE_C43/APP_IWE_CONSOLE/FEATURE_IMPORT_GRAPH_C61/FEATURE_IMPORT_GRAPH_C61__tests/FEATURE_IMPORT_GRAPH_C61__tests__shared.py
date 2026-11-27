"""Subprocess support for the Realization Graph provider tests."""

import json
import os
from pathlib import Path
import subprocess
import sys


def run_provider(root, config, **extra):
    engine = Path(__file__).resolve().parents[4]
    env = os.environ | {"PYTHONPATH": str(engine)}
    return subprocess.run(
        [sys.executable, "-B", "-P", "-m",
         "IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IMPORT_GRAPH_C61.realization_graph_cli"],
        input=json.dumps({"root": str(root), "config": config, **extra}),
        text=True, capture_output=True, env=env, check=False,
    )
