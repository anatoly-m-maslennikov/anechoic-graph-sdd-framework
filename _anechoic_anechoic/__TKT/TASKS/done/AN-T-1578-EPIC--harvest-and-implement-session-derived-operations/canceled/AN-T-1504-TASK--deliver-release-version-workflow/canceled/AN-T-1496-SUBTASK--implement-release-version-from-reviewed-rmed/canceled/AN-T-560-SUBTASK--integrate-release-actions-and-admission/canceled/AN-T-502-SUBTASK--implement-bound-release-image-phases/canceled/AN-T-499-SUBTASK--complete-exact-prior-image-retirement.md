---
atom_family: TKT
atom_id: AN-T-499
structure:
  container:
    atom: AN-T-502
  priority: 2
context:
  template: task
  label: Subtask
state:
  status: "canceled"
  version: 8
  updated_at: "2026-11-20T20:03:59.998363+00:00"
---
# Summary

Complete exact prior-image retirement

## Objective

After P1693, complete exact prior-image retirement within <=15 minutes.

## Details

Own only release_image.py and tests/test_release_image.py. Consume actual observed promotion evidence, current matching N+1 selector and actual immutable prior-image identity. Independently observe all retaining containers and required rollback references before exact removal; unknown or retained identity yields truthful retained/pending result. Do not accept caller flags, mutable tags, broad prune or force. Golden-first fake execution only; no actual image/container operation or C449 workaround. Preserve the already accepted build/verification API and other Agents' work.

## Definition of Done

Save exact code/test hashes and actual focused case outcomes, distinguishing mock evidence from actual image execution. Parent and actual release gates remain separate.

### Current partial frontier

The bounded observer/refusal implementation passes37 focused fake-image methods at release_image.py 46d43156559387016f5695a30f45669338bfe9b8fb27db491ba4489b16a0569e and tests240322a9ea8eeadf7b25301bba4ffb1264bfea12283ee90714dcd9ac86ef9711. retire_prior_image now consumes verified completed promotion/current selection, inspects the exact immutable prior image and every running/stopped container, and retains actual reference/receipt evidence. Unknown observations stay None; historical selector evidence is not automatically required rollback use. No removal is admitted because approved retention release is unbound. C466 and the bounded source/provider binding remain required; this Task is Active, not full retirement completion. No real Docker image/container operation occurred.
