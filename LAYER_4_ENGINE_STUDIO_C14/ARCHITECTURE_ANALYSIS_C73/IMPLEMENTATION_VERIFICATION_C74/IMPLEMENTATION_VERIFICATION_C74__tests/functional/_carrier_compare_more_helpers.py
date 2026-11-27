import hashlib
import tempfile
from pathlib import Path

if __package__:
    from ._carrier_compare_helpers import ROOT, _pins, _formal_witnesses
    from ._carrier_compare_helpers import _SOURCE, compare
else:
    from _carrier_compare_helpers import ROOT, _pins, _formal_witnesses
    from _carrier_compare_helpers import _SOURCE, compare


def _test_direct_comparison_replays_digest_pins(self):
    formal = _formal_witnesses()
    pins = formal["sources"]
    source_digest = hashlib.sha256((ROOT / _SOURCE).read_bytes()).hexdigest()

    def verify(*args, **kwargs):
        return formal

    report = compare(
        ROOT,
        "/missing/lean",
        **pins,
        formal_verifier=verify,
        implementation_sha256=source_digest,
    )
    self.assertEqual(report["evidence"]["source_sha256"], source_digest)
    self.assertIn(
        "Lean executable unavailable", report["evidence"]["unresolved"]
    )
    stale = compare(
        ROOT,
        "/missing/lean",
        **pins,
        formal_verifier=verify,
        implementation_sha256="0" * 64,
    )
    self.assertEqual(
        stale["evidence"]["unresolved"],
        ["Implementation source digest changed"],
    )
    self.assertEqual(stale["cases"], [])
    changed = {
        **pins,
        "solution": {**pins["solution"], "sha256": "0" * 64},
    }
    stale = compare(ROOT, "/missing/lean", **changed, formal_verifier=verify)
    self.assertEqual(
        stale["evidence"]["unresolved"],
        ["Solution receipt does not match the requested pin"],
    )


def _test_direct_comparison_reads_the_manifest_operations(self):
    formal = _formal_witnesses()
    with tempfile.TemporaryDirectory() as folder:
        root = Path(folder)
        for role, source in formal["sources"].items():
            relative = source["path"]
            raw = (ROOT / relative).read_bytes()
            if role == "manifest":
                old = b"'operations': ['frontmatter_bounds', 'source_body']"
                self.assertIn(old, raw)
                raw = raw.replace(
                    old, b"'operations': ['parse_settings_bytes']"
                )
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
            source["sha256"] = hashlib.sha256(raw).hexdigest()
        report = compare(
            root, **_pins(formal), formal_verifier=lambda *a, **kw: formal
        )
    self.assertEqual(report["status"], "unresolved")
    self.assertIn(
        "Manifest does not declare the two checked framing operations",
        report["evidence"]["unresolved"],
    )
