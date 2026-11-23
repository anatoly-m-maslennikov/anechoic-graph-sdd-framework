---
atom_family: SPEC
atom_id: AN-S-3863
container:
  component: C20
tier: 4
context:
  lens: DES
state:
  status: archived
  version: 6
  updated_at: 2026-10-24 00:51:05 +0400
---
## Summary

Recover Workflow handoffs without repeating effects

# Recover Workflow handoffs without repeating effects

WORKFLOW_ORCHESTRATOR **must** recover accepted work **and** admitted Run handoffs **after** interruption **without** losing work **or** blindly repeating effects.

- preserve an accepted request durably **before** acknowledging acceptance **to** its client.
- preserve the predecessor's terminal result **and** continuation intent durably **before** dispatching a successor. correlate that intent with the successor Run so repeated delivery **or** recovery cannot independently launch duplicate successors.
- retain execution facts **in** the canonical Project Journal under ANECHOIC-META-REQU-158. scheduling indexes, queues, **and** displayed state **must not** become a second historical authority; derived state is reconciled against its authoritative sources.
- recovery **must** distinguish work **not** started, work started, observed completion, **and** uncertain effect outcomes. an uncertain non-repeatable effect requires evidence reconciliation **or** Operator escalation, **not** an assumed exactly-once guarantee.
- retain the original request, Run associations, exact definition bindings under CA-R-1525, performed effects, **and** remaining retry allowance. changed definitions pause dispatch for recorded revalidation; current authority **and** target freshness remain required **before** further effects.
- a stopped service **or** lost client session **must not** imply successful completion. incomplete **or** conflicting recovery evidence blocks affected execution visibly.
