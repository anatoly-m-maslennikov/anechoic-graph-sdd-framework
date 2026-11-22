"""Compile and verify the staged Model used for Docker image admission."""

import argparse
from hashlib import sha256
import json
from pathlib import Path

from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.native_manifest_model import reviewed_model_records

from .compiler import write_model
from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_MODEL_VALIDATION.model_generation__pub import verify_model


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("staged_control_root", type=Path, nargs="?")
    parser.add_argument("--attest-model", action="store_true")
    args = parser.parse_args()
    if args.attest_model and (args.staged_control_root is None
                              or not args.staged_control_root.is_dir()
                              or any(args.staged_control_root.iterdir())):
        parser.error("--attest-model requires an empty staging directory")
    if args.staged_control_root is None:
        fingerprint = reviewed_model_records()[2]
    else:
        fingerprint = write_model(args.staged_control_root, args.staged_control_root)
        verify_model(args.staged_control_root, fingerprint)
    if args.attest_model:
        digest = sha256((args.staged_control_root / "model.json").read_bytes()).hexdigest()
        print(json.dumps({"model_sha256": fingerprint, "descriptor_sha256": digest}))
    else:
        print(fingerprint)


if __name__ == "__main__":
    main()
