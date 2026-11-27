---
atom_family: SPEC
atom_id: AN-S-2786
container:
  component: C45
tier: 7
context:
  lens: QA
state:
  status: archived
  version: 3
  updated_at: 2026-11-09 19:30:15 +0400
---

## Summary

Verify relation registry delivery on every image rebuild

## Claim

### Prose Claim

Verify the generated relation registry on every supported image-build entry point, including local release:

- Generate before computing image identity and assembling its context. Changing a selected Declaration changes the generated asset and its recorded build identity.
- Identical selected inputs produce identical bytes. Record the selected source Atom IDs, versions, paths and fingerprints without a changing timestamp in the fingerprint.
- Include the asset and its digest in the staged package and image verification. Do not include Project authority carriers in the image context.
- A stale output is regenerated. A missing output or generator failure prevents acceptance of that build or package rather than accepting the stale asset.
- Verify the installed runtime consumes the delivered metadata. A later relevant Current Declaration change uses the same compiler and refreshes the selected Project's registry and graph.
- Keep the code/config MCP tool registry separate. Registering MCP tools does not scan the Project's full Atom inventory.

Run focused build-hook checks with controlled inputs and one local-release check with the real selected Project. Record the installed release, source registry fingerprint and observed relation-query results. A successful generator test alone does not prove the installed image is aligned.
