---
atom_family: SPEC
atom_id: AN-S-129
container:
  component: C16
tier: 2
context:
  lens: DevOps
state:
  status: active
  version: 38
  updated_at: "2026-11-27T17:35:01.150345+00:00"
---
## Summary

Deliver the commit-trigger script

# Deliver the commit-trigger script

Realize COMMIT_TRIGGER through LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/COMMIT_TRIGGER/commit_trigger.py **and** its content-identical carrier **in** the selected installed release. Apply AN-S-101 to Tool and Hook installation.

the user-level Codex carrier is one generic asynchronous PostToolUse command Hook with full-value matcher .* **and** async: true. It resolves the Git root from Hook cwd, requires the exact repository-local anechoic.codex-hooks = v1 activation, exits **without** effect **when** activation **or** the installed launcher is absent, **and** **otherwise** delegates **to** the stable install-owned commit-trigger launcher. The command identity **contains** no repository-specific absolute path **or** release digest.

Apply AN-S-5175 when receiving a COMMIT_TRIGGER event.

Automatic-commit PreToolUse, SessionStart, **and** Stop callbacks are **not** installed. Apply AN-S-1218 to missed delivery and external edits. Runtime event provenance is compacted **to** Journal-resolvable identities **and** receipts **after** canonical Journal acceptance.
