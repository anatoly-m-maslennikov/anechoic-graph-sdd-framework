---
atom_family: TKT
atom_id: AN-T-3902
container:
  atom: AN-T-3476
priority: 2
context:
  template: task
  label: Task
state:
  status: done
  version: 3
  updated_at: '2026-11-24T11:49:32.819433+00:00'
---
## Summary

Build a golden corpus of seven-day bug fixes

## Work

Build a reusable golden corpus from the confirmed already found and fixed bugs in AN-T-3901. Do not review current code or scan sibling paths. Record exact buggy and fixed revision provenance for each case, or record a gap when it cannot be established.

Independently state expected behavior from requirements and evidence, not from the fix alone. Translate the actual historical buggy and fixed code into Lean where supported. Document the correspondence and abstraction limits.

Measure each supported case in Lean: the exact buggy revision must fail the independent expectation and the fixed revision must pass it. Preserve corpus inputs, commands, revision identifiers, outcomes, and evidence so the corpus can be rerun. Record unsupported translations, missing provenance, and cases that cannot be reproduced.

## Acceptance

A reusable golden corpus records each supported case with exact old and fix provenance, independent expected behavior, code-linked Lean translations, measured old failure and fixed pass, and reproducible commands. It identifies explicit coverage gaps and unsupported or unresolved cases.

## Result

The reusable corpus is `LAYER_4_ENGINE_STUDIO_C14/ARCHITECTURE_ANALYSIS_C73/IMPLEMENTATION_VERIFICATION_C74/IMPLEMENTATION_VERIFICATION_C74__tests/functional/golden_bugs`. Its 10 cases preserve exact committed old and fixed provenance and independently stated invariants. They cover CRLF carriers, stale Ref ID, renumbered alias, excluded watcher roots, prior carrier read errors, duplicate currentness, first SPEC ordinary and pinned publication, MCP direct-update response, and release run identifiers.

`test_golden_bugs.py` is registered in host Functional. The focused run recorded in `$BB_THREAD_STORAGE/golden-bug-corpus.log` passed both tests: 20 source fixture digests and 15 frozen Lean files. The Lean checks demonstrate the old failure and fixed pass within each recorded case scope. The corpus README gives the rerun command.

The runner verifies preserved source and frozen Lean checks, including expected output suffixes. It does not automatically translate the source, execute the Python fixtures, establish Python-to-Lean equivalence, or test current runtime. The Lean results support bounded models only; they do not prove the actual source translations equivalent. Corpus completeness against the seven-day inventory remains a coverage gap pending AN-T-3901.
