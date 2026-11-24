---
atom_family: SPEC
atom_id: AN-S-1923
container:
  component: C21
tier: 5
context:
  lens: DevOps
state:
  status: active
  version: 22
  updated_at: "2026-11-23T01:51:04.201552+00:00"
---
## Summary

carry the localhost HTTP Gateway and configuration

## Claim

### Prose Claim

Deliver Streamable HTTP at `/anechoic/mcp` on container port 8092. Publish it on `127.0.0.1` at the selected host port. Docker binds that port. Refuse an occupied port. Keep stdin and stdout available through the stdio entry point.

Use the restricted container and exact Project mount. Do not mount the Docker socket or inject credentials. Admit loopback Host and Origin values. Non-browser clients may omit Origin.

Report an endpoint only after verifying its unique binding, running image, and host-side readiness. Verify both MCP transports against the installed runtime. Docker unavailability leaves the real-container check incomplete.
