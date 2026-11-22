import subprocess
import sys
import unittest

from KERNEL_MIXER_C59.MANIFEST_RUNTIME_C62.process import _CODE_ROOT, _environment


class BootstrapTest(unittest.TestCase):
    def test_reviewed_model_is_cached_without_importing_builder(self):
        source = """
import sys
from concurrent.futures import ThreadPoolExecutor
from KERNEL_MIXER_C59.MANIFEST_RUNTIME_C62.model_host_CS2.model_host_CS2__pub import reviewed_native_model
with ThreadPoolExecutor(max_workers=4) as executor:
    models = list(executor.map(lambda _: reviewed_native_model(), range(4)))
assert all(model is models[0] for model in models)
assert not any('FEATURE_FORMAL_MODEL_GENERATOR' in name for name in sys.modules)
"""
        subprocess.run([sys.executable, "-B", "-P", "-c", source], cwd=_CODE_ROOT,
                       env=_environment(), timeout=30, check=True)
