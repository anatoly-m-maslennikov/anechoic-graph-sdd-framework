import subprocess
import sys
import unittest
import os
from pathlib import Path


class BootstrapTest(unittest.TestCase):
    def test_reviewed_model_is_cached_without_importing_builder(self):
        source = """
import sys
from concurrent.futures import ThreadPoolExecutor
from KERNEL_MIXER_C59.MANIFEST_RUNTIME_C62.model_host_CS2.model_host_CS2__shared import reviewed_native_model
with ThreadPoolExecutor(max_workers=4) as executor:
    models = list(executor.map(lambda _: reviewed_native_model(), range(4)))
assert all(model is models[0] for model in models)
assert not any('FEATURE_FORMAL_MODEL_GENERATOR' in name for name in sys.modules)
"""
        code_root = Path(__file__).resolve().parents[5]
        environment = {**os.environ, "PYTHONPATH": str(code_root / "LAYER_4_ENGINE_STUDIO_C14")}
        subprocess.run([sys.executable, "-B", "-P", "-c", source], cwd=code_root,
                       env=environment, timeout=30, check=True)
