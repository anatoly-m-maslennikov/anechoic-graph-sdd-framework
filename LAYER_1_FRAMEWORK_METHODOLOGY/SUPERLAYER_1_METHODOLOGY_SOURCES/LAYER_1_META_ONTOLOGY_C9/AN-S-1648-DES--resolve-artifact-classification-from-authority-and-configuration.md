---
atom_family: SPEC
atom_id: AN-S-1648
container:
  component: C9
tier: 2
context:
  lens: DES
state:
  status: active
  version: 45
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary
Resolve Artifact Classification from Authority and Configuration

## Claim

### Prose Claim


Artifact classifications resolved from Applicable Methodology and Project Configuration with structural context from authoritative Project Structure.


ANECHOIC **must** resolve **every** Artifact's applicable classification from Applicable Methodology **and** Project Configuration, with structural context from authoritative Project Structure:

- resolve Artifact Type under the applicable Type authority.
- resolve Content Role **only** for an Atom; do **not** require a Journal **or** Projection **to** have an Atom Content Role.
- resolve a semantic route **only** **where** the applicable authority defines that classification.
- classify an unknown, disabled, stale, multiply mapped, **or** ambiguous value as an unresolved **or** failed classification, **not** as an accepted one.

a derived Scope Unit Graph **must not** replace Project Structure as structural authority. reporting a classification failure does **not** itself impose a universal mutation **or** execution prohibition; the applicable Authority Mode **and** admission rules govern that consequence.
