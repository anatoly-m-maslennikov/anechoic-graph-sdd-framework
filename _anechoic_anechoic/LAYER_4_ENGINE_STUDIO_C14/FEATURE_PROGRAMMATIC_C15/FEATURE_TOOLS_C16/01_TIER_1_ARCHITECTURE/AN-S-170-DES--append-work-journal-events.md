---
atom_family: SPEC
atom_id: AN-S-170
container:
  component: C16
tier: 1
context:
  lens: DES
state:
  status: active
  version: 26
  updated_at: "2026-11-23T00:28:58.970349+00:00"
---
## Summary

Append Work Journal events

# Append Work Journal events

**every** Journal-appending Doer **must** use shared deterministic non-executable logic that validates **and** atomically appends one sealed Work Journal event **without** rewriting **or** rereading the complete logical Journal. the logic **must** validate **and** use the event's already sealed full GitHub username, configured Artifact timestamp timezone, **and** local calendar date **without** resolving **or** recomputing them; serialize competing appends **to** the affected author-date partition; verify the current carrier digest inside that serialization boundary; continue the current `<author>-<YYYY-MM-DD>-part-<N>.ndjson` segment while it **contains** fewer than 100 accepted events; **and** open the next numbered segment **otherwise**. its receipt binds the event identity, canonical event digest, carrier, line position, `previous_carrier_digest`, **and** `appended_carrier_digest`; the carrier digests describe the Journal append **and** never duplicate a governed subject's previous **and** resulting states. reapplying the same sealed event identity with the same canonical event digest **must** return its existing receipt **without** appending a duplicate. reusing an accepted event identity with different canonical event bytes **must** fail **before** mutation with a stable identity-collision diagnostic. the shared logic is **not** an independently executable Tool.

Workbench Saved SQL uses the fixed service author and plain Journal
append in AN-S-2547. The admitted Project identifies its Journal.
