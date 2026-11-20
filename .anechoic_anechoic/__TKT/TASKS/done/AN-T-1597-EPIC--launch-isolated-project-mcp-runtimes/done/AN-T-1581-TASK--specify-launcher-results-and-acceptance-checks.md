---
atom_family: TKT
atom_id: AN-T-1581
structure:
  container:
    atom: AN-T-1597
  priority: 2
context:
  template: task
state:
  status: done
  version: 8
  updated_at: 2026-10-25 17:32:27 +0400
---
# Summary

Specify launcher results **and** acceptance checks

## Objective

the AI Agent specifies the observable success **and** failure contract for the Project MCP launcher.

## Details

- input: the reviewed selection **and** startup authority **and** existing HTTP authentication **and** Evaluation specifications.
- output: reviewed source E **and** D for authenticated host-side readiness, the MCP URL, safe structured metadata, bounded waiting, non-success outcomes, **and** the mock **and** real-Docker acceptance matrix. document endpoint readiness separately from Workflow-worker readiness.
- verification: bind each required result **to** an observable check; credentials remain separate from the URL **and** are absent from ordinary logs **and** results.
- effort: **`<=15`** minutes for **`=1`** AI Agent; the Epic's decomposition rule applies **before** execution **if** the estimate no longer holds.

### Definition of Done

- completion evidence: O188, E601 **and** D595; independent launcher_security review passed bounded host-authenticated MCP readiness, URL admission, safe structured failures **and** credential redaction.

the Plan is **not** Done **if** ((a success URL can be returned **before** authenticated readiness) **or** (a required startup outcome lacks an Evaluation) **or** (the output contract permits credential disclosure)).
