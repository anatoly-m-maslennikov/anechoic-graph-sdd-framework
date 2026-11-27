---
atom_family: TKT
atom_id: AN-T-4054
container:
  atom: AN-T-3476
priority: 2
context:
  template: task
  label: Task
state:
  status: done
  version: 1
  updated_at: "2026-11-27T10:48:07+00:00"
---
## Summary

Generate and run local Programmatic tests from formal Specs

## Acceptance

Use the existing Spec Engine generator on in-scope Programmatic Specs. Run generated cases at normal local entry points with disposable fixtures. Record source pins, observed outcomes, and obligations without generated cases.

## Evidence

Ran the existing C92 generator for C30 using AN-S-3069@63-draft and
AN-S-4742@2-draft. All 134 witnesses matched the Adapter byte results
and errors. The negative control detected the historical defect.

Ran four C16 exact-Draft outcomes in six fixture variants through the
lifecycle CLI using AN-S-3056@68-draft and AN-S-5042@1-draft. All passed.

Derived the two C19 CLI exit classes from AN-S-3287@9-draft with the
AN-S-3055@26-draft Manifest and AN-S-3365@4-draft Decision. The public
CLI ran a real test Module in each case and returned 0 and 1 as declared.

The generic generator covers bounded carrier framing. Symbolic traces
without concrete fixtures or observation rules still need authored test
inputs. The C49 implementation binding pins a prose Contract. Its local
Hook tests use manually defined inputs. This task used host tests.
