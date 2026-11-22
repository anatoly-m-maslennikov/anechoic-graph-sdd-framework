---
atom_family: TKT
atom_id: AN-T-2792
container:
  component: C00
priority: 2
context:
  template: question
state:
  status: resolved
  version: 1
  updated_at: '2026-11-19T05:21:51.934877+00:00'
---
## Summary

Choose a nonconflicting MCP endpoint for the isolated Local Release

## Concern

May the final isolated startup use a separate MCP port in the copied
Project settings after the clean rebuild has verified the original inputs?

## Details

CA-P-3095 needs a clean Local Release in a checkout containing both trees.
The isolated test image built with all 1,108 selected legacy inputs and
three verified migrated carriers. Its build did not start Project MCP.

The live MCP owns port 56317. The installed launcher reads that port from
the protected Project settings. Its CLI port argument checks the setting.
A second startup on the same Docker host cannot bind that port.

Keep the source proof and clean rebuild on the original settings. For the
startup rehearsal, record one isolated-only port change in the copied
settings. An isolated Docker host can instead keep the exact settings.
The live settings, running container, and retained images stay in place.

The Operator approved a free port in the isolated checkout for the startup
check. Verify the clean rebuild and compare the protected input digests
with the original Settings before changing the copied port. Record the
startup exception and verify the original bytes after the check.

## References

CA-P-3075, CA-P-3095, CA-D-562.