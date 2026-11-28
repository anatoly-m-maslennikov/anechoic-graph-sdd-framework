"""Run the TypeScript behavior replay with the locked frontend toolchain."""

from pathlib import Path
import subprocess
import unittest


class Replay(unittest.TestCase):
    def test_action(self):
        subprocess.run(
            ["node", str(Path(__file__).with_name("replay.mts"))],
            check=True,
            timeout=30,
        )


if __name__ == "__main__":
    unittest.main()
