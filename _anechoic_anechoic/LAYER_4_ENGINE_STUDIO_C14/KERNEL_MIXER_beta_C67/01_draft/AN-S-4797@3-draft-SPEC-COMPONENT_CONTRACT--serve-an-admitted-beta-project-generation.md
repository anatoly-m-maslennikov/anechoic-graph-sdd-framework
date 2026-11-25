---
atom_family: SPEC
atom_id: AN-S-4797
container:
  component: C67
tier: 0
context:
  template: component_contract
  lens: SPEC
relations:
  ANSWERS:
  - AN-S-3332
state:
  status: draft
  version: 3
  updated_at: '2026-11-25T10:46:01Z'
---

## Summary

Serve an admitted Beta Project generation

## Guarantee

Keep the Database Server and Model and Structure Hosts within the Kernel process. Bind the server to one Project instance. Admit and serve the generation built by C69 through CS4 and CS1. If Kernel admission fails, retain the prior generation.

For an invalid Model candidate, CS1 selects the last accepted Model or, if none exists, the reviewed bundle. Report the candidate diagnostics.

Serve the accepted Model and generation ID to requests for that instance. Reconstruct canonical Structure JSON from the accepted `mrt_project_structure` rows and the accepted generation facts. Return it with that generation ID. Publish changed rows atomically through ingestion.

Reject requests for another instance. Report candidate admission failures and diagnostics. Before an accepted generation is available, report that state.

## Claim

### Prose Claim

A successful read validates the Project binding, reads accepted content
through C71, and returns the content with its generation ID. A foreign
instance or a request before generation admission gets no artifact response.
These outcomes apply to either Structure representation.

### Formal Claim

```python trace
declare_trace_contract(
    action='beta_artifact_read',
    output='succeeded',
    must_effect=(('project_binding', 'matched'), ('artifact_content_generation', 'paired'), ('artifact_response', 'paired')),
    must_precede=((('project_binding', 'matched'), ('artifact_content_generation', 'paired')),
                  (('artifact_content_generation', 'paired'), ('artifact_response', 'paired'))),
)
```

```python trace
declare_trace_contract(
    action='beta_artifact_read',
    output='foreign_instance',
    forbid_effect=('artifact_response',),
)
```

```python trace
declare_trace_contract(
    action='beta_artifact_read',
    output='no_generation',
    forbid_effect=('artifact_response',),
)
```

## Source alignment to resolve

AN-S-4797@1 says the Server admits paired artifacts and a Project snapshot,
and serves accepted Model or Structure bytes. AN-S-4797@2-draft instead
says to reconstruct Structure JSON from accepted rows and generation facts.
The active AN-S-4798@1 describes the Host reading an artifact under a lock.
Resolve how the Structure representation and read sequence agree before
activation. This Draft preserves both accounts without deciding that issue.
