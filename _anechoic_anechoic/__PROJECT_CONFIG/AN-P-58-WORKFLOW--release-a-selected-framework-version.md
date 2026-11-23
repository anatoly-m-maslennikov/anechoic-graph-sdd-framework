---
atom_family: PROJECT_CONFIG
atom_id: AN-P-58
structure:
  container:
    component: C27
context:
  template: workflow
state:
  status: "active"
  version: 41
  updated_at: "2026-11-23T14:23:51.238726+00:00"
---
## Summary

Release a selected Framework Version

## Claim

### Formal Claim

```python
release_command(
    operation="local",
    entrypoint="LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/release.py",
)
```

### Semantics

When the Project Manifest enables release Workflows, MCP reads this Active
Project Config Claim and returns the host `uv` command for the selected
Project and run ID. The Operator runs it on the host. MCP performs no
release effects.

## Operation

Validate the selected Project, checkpoint Git, and bump the candidate version.
Run static and required functional checks. Prepare the package and verify the
exact candidate image through end-to-end checks and the disposable canary.

Install the verified package and start the same image on the Project port.
After MCP is ready, tag the image as production and perform final cleanup.
Report the outcome and any incomplete cleanup.

See AN-S-3292 for the Local Release guarantees. The formal steps are
AN-P-30 (validate), AN-P-31 (prepare), and AN-P-35 (install).
