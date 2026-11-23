---
atom_family: SPEC
atom_id: AN-S-3445
container:
  component: C19
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 8
  updated_at: 2026-10-10 23:57:30 +0400
---
## Summary

Deliver the Release suite driver and JUnit report boundary

# Summary

Deliver the Release suite driver and JUnit report boundary

## Scope

The carrier and sealed-environment boundary for the closed RELEASE_VERSION Unit driver.

## Claim

The Release Unit driver **must** remain the fixed sealed driver at `102_FRAMEWORK_ENGINE/201_PROGRAMMATIC/201_TOOLS/RELEASE_VERSION/run_release_suite.py`, with source-bound JUnit evidence, exactly two 2GiB disposable tmpfs mounts, and a host-independent captured-deadline guard that admits no caller control.

## Details

```toml
entrypoint = "102_FRAMEWORK_ENGINE/201_PROGRAMMATIC/201_TOOLS/RELEASE_VERSION/run_release_suite.py"
command = ["python", "102_FRAMEWORK_ENGINE/201_PROGRAMMATIC/201_TOOLS/RELEASE_VERSION/run_release_suite.py"]
working_directory = "."
report = "ANECHOIC_RELEASE_SUITE_REPORT"
source_bindings = "ANECHOIC_RELEASE_SOURCE_BINDINGS"
source_bindings_sha256 = "ANECHOIC_RELEASE_SOURCE_BINDINGS_SHA256"

[execution]
temporary_mount_options = "rw,nosuid,nodev,exec,size=2g,mode=1777"
temporary_mounts = ["/tmp", "/workspace/.anechoic_tmp"]
workspace = "read-only"
network = "none"
docker_socket = "forbidden"
output = "/output"

[unit_deadline]
authority = "captured effective_unit_timeout_seconds"
maximum_seconds = 7200
enforcement = "fresh locked-uv Unit-runner Python PID 1; reserve=min(1.0, deadline/2); TERM at deadline-reserve; KILL at hard deadline; reap; timeout exit 124"
```

The Suite Owner preflights the inspected/admitted Unit-runner Python `-c` capability before launch; unsupported invocation is non-passing before launch. After exact sealed-command equality and fresh immutable Unit-runner image/PATH inspection, it constructs exactly `--entrypoint <inspected/admitted-unit-runner-python> IMAGE -c CONSTANT_GUARD <canonical-decimal-captured-seconds> -- <exact-sealed-child-argv>`. The constant executor-owned guard validates the finite bounded internal duration, uses `Popen(argv, start_new_session=True)`, and never calls a shell, string evaluator, host interpreter, candidate image, caller command, caller environment, caller timeout, new setting, or new public field. It reserves `min(1.0, deadline / 2)` seconds before hard expiry; it sends TERM at `start + deadline - reserve`, KILL at `start + deadline` if needed, and reaps its own child. Initiating TERM latches timeout and returns `124` after reaping regardless of child status; only a child exit observed before TERM forwards its normal status. Reap/wait failure is non-passing; PID 1 exit terminates remaining container processes. No termination phase extends the configured/effective deadline. The existing host CLI timeout and labelled CID cleanup are observers/best-effort containment only.

The sealed source workspace, source-binding schema-2 envelope, package/reference rows, fixed driver command, phase rules, output-only JUnit path, private deadline snapshot, source probes, revalidation, and refusal behavior remain unchanged. `--rm` is not a receipt. Only normal terminal receipt plus complete source-bound JUnit evidence and currentness revalidation can pass; every timeout, host loss, guard failure, missing receipt, incomplete report, or changed context is non-passing and retains N. This delivery creates no new route, Workflow, gate, manifest/member, CLI, environment variable, setting, or caller field.

The Unit runner is a fresh private immutable image built from the exact sealed dependency inputs (pyproject.toml, uv.lock and the runtime Dockerfile dependency prefix), using locked uv dependency synchronization. It is distinct from the candidate/MCP image, contains no candidate Engine payload, and does not execute or inspect a historical installed image. Existing selected-N selector/package/source-context metadata remains a truthful documentary preservation baseline, not proof of the executing Unit runner; its identity is not replaced by the runner input digest. Its actual image ID, input digest, PATH and build/inspection evidence are reopened before execution; no caller image or bare-host-Python fallback is admitted. Runtime networking is none and a Docker socket mount is forbidden. Candidate-image construction still follows the passing Unit gate; source command, source/JUnit bindings, captured deadline and currentness checks remain exact.
