# Historical VALIDATE_ATOMS golden corpus

The retired VALIDATE_ATOMS command and its broad adapter pipeline are no longer
shipped. The source-authored requests, expected reports, fixtures, manifest and
source bindings remain here as historical evidence of the earlier test corpus;
they do not demonstrate current command behavior or an acceptance gate.

The corpus checks validate the manifest and expected report shapes, referenced
fixture paths, expected result/exit-code consistency, and the SHA-256 digests
of the copied authority fixtures. The fingerprint utility is also checked.
The `/__fixture__` prefix in historical requests is a transport placeholder.
The fixture authority copies are test inputs, not active governing Project Atoms.

Run the historical corpus checks from the repository root:

```sh
PYTHONPATH="$PWD/LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS" \
  .venv/bin/python -B -m unittest discover \
  -s LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/VALIDATE_ATOMS/VALIDATE_ATOMS__tests
```
