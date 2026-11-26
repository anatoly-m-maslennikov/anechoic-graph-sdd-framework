"""Statically verify the generated query_run contract."""

from pathlib import Path
import subprocess
import sys
import unittest


class QueryContractTest(unittest.TestCase):
    def test_generated_artifacts_match_model(self):
        subprocess.run([sys.executable, "-B", "-m", "API_MIXER_beta_C91.query_contract", "--check"],
                       cwd=Path(__file__).resolve().parents[3], check=True)


if __name__ == "__main__":
    unittest.main()
