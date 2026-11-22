"""Run one closed native lifecycle operation using a fresh attested generation."""
import json
from pathlib import Path
import sys
import tempfile

from .WORKERS_beta_C69__shared import _capture, _run_job, build_generation

_NAMES = frozenset({"atom_lifecycle_create_draft", "atom_lifecycle_update", "atom_lifecycle_promote_draft"})
_OWNER = "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.native_lifecycle_cli"


def run(request):
    if (not isinstance(request, dict) or set(request) != {"binding", "name", "arguments"}
            or request["name"] not in _NAMES or not isinstance(request["arguments"], dict)):
        raise ValueError("Invalid lifecycle request")
    binding = request["binding"]
    before = _capture(binding)["stability_sha256"]
    with tempfile.TemporaryDirectory(prefix="anechoic-lifecycle-") as temporary:
        generation = Path(temporary).resolve()
        built = build_generation(binding, generation)
        if _capture(binding)["stability_sha256"] != before:
            raise ValueError("Native Project carriers changed before lifecycle operation")
        payload = {**request, "generation": str(generation), "receipt": built["receipt"],
                   "stability_sha256": before}
        return _run_job(_OWNER, payload)


def main():
    try:
        outcome = run(json.load(sys.stdin))
        print(json.dumps(outcome, ensure_ascii=False, separators=(",", ":")))
    except (OSError, RuntimeError, TypeError, ValueError, KeyError) as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
