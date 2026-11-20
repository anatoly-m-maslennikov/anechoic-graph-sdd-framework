---
identity:
  atom_id: AN-P-72
context:
  container:
    component: C9
state:
  status: draft
  version: 4
  updated_at: 2026-09-23 17:20:35 +0000
---
# Summary

Initialize the ANECHOIC session

## Claim

ANECHOIC Session Initialization **means** the Action that prepares the bounded context needed for a session using the ANECHOIC Main Skill, at session start **or** **after** context compaction, **without** treating restored context as new authority **to** execute work.

### Inputs and preconditions

- the session entry **or** compaction event, the current Operator request, **and** available Project identity evidence.
- the registered Project Settings, effective Framework Instance Settings, Project Structure, canonical ANECHOIC Routing Tree, **and** **any** existing bounded Session-State Envelope.
- references **to** current active authority **and** existing authorization; missing inputs remain explicit rather than being inferred from another Project.

### Behavior

1. identify the owning Project **and** current Scope Unit. reuse CA-O-052 for initialization inputs **before** interpreting Project Structure; resolve declared ownership from Project Structure rather than inventing it from folder names.
2. prepare a new session's bounded context from the resolved sources, **or** restore existing context **after** compaction **and** check its freshness. include **only** the context admitted by ANECHOIC-GOV-REQU-371 **and** ANECHOIC-METHODOLOGY-REQU-509. retain references for on-demand authority loading, **not** another authoritative copy of the Methodology **or** session history.
3. check the registered ANECHOIC Routing Tree under its existing validation authority CA-E-483. an absent, invalid, **or** stale required input blocks affected routing; do **not** silently substitute a cached tree **or** fabricate a successful check.
4. classify the current request using CA-R-1558. preserve Exploration Mode for exploratory input; retain an explicit executable request as a pending request subject **to** current authorization **and** applicable checks. revalidate restored delegation under CA-R-852 **and** CA-R-1552 **before** relying on it.
5. return the prepared context **and** references **to** the calling session. restoration does **not** itself replay an effect, resume unfinished work, persist a Plan, **or** authorize an additional change.

### Results and effects

- ready: the identified Project **and** Scope Unit, effective settings references, checked routing reference, compact context, request classification, **and** **any** pending request.
- blocked: missing, stale, conflicting, **or** invalid inputs with the evidence **and** decision needed **to** resolve them.
- failed: the failed initialization operation **and** recoverable partial session state; do **not** report the session ready.

the Action changes **only** the admitted session context. it does **not** modify governing Atoms, Settings, Project Structure, **or** Implementation. host hooks, provider integration, **and** storage mechanics remain outside this Action definition.
