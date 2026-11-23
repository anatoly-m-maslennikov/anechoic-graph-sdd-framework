"""Run the Studio plot generator at its documented CLI path."""

from pathlib import Path
from runpy import run_path


if __name__ == "__main__":
    run_path(str(Path(__file__).with_name("plots__shared.py")), run_name="__main__")
