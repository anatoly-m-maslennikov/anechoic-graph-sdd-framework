---
atom_family: SPEC
atom_id: AN-S-476
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 18
  updated_at: 2026-10-29 07:45:30 +0400
---
## Summary

Place Local Environment Injection Carriers

## Claim scope

secret values and local environment injection Carriers.

## Claim

secret values **must** be stored **only** **in**:

- gitignored `.env` File Carriers; **or**
- a dedicated secret vault.

## Details

### File placement

- a repository-local `.env` File Carrier **must** remain outside **every** applicable Project authority Carrier root.
- **every** real `.env` variant **must** be gitignored, untracked, **and** excluded from durable **or** shared Git history **and** ANECHOIC discovery. a Git ignore rule does **not** remove a previously tracked secret from history.
- a tracked `.env.example` **may** contain variable names **and** unmistakable dummy placeholders **only**.

### Runtime injection

secret values **may** reach authorized runtime consumers through host injection from a permitted secret store; the injected value is **not** a separate persisted source.
