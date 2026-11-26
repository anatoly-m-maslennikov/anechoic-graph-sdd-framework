---
atom_family: TKT
atom_id: AN-T-3978
container:
  component: C14
priority: 2
context:
  template: question
state:
  status: in_queue
  version: 1
  updated_at: '2026-11-26T02:58:53.436224Z'
---
## Summary

Reconcile Code Access after the ontology merge

## Concern

Which owning Package entries and Manifest revisions should authorize the incoming Spec Engine and typed Model imports?

## Details

The merged checker at `73a994ef47` found 257 denied occurrences, all touching changed source. There were 195 involving C75, including 10 across the C75 boundary, and 62 elsewhere in Studio. All denials were Code Access rules. The running 0.4.4.75 checker reported 71 denied occurrences on the same checkout.

The incoming Spec Engine and eight child Component Manifests are Drafts. Keep publication in their existing review. Resolve required imports through their owning Package entries and narrow Manifest declarations under AN-S-3179. Recheck the graph with a matching checker and Model.

[AN-T-3968](../TASKS/AN-T-3968-EPIC--merge-the-meta-ontology-and-spec-engine-into-amm-dev.md)
