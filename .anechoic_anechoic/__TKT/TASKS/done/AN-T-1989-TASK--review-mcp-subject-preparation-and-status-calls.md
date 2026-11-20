---
identity:
  atom_id: AN-T-1989
context:
  container:
    atom: AN-T-1990
  tier: 3
  template: task
state:
  status: done
  version: 9
  updated_at: 2026-10-25 17:32:27 +0400
---
# Summary

Review MCP Subject preparation and status calls

## Objective

Review one bounded immutable input partition for the five-day scoped MCP audit, without replaying effects or declaring current resolution.

## Details

All 108 direct atom_update Subject-preparation calls and 32 direct change_atom_status calls. Canonical input is .anechoic_tmp/mcp-audit-20261020/corpus-v2/release-v2/partitions/atom_lifecycle_actions.jsonl, filtered by exact tool_name. Verify release SHA256SUMS before reading. Use native_event_id, source_file/source_line, payload start/completion timestamps, exact request and result. Native completed transport is not domain-effect success. The release has 728 project-proven ANECHOIC calls, including 384 lifecycle calls; other-server events and embedded/wrapper annotations are not lifecycle execution counts. Source file hashes are scan-time hashes; 4 KiB header pins do not cover distant evidence lines, so do not claim immutable full-session provenance or complete dynamic-wrapper observability.

Classify success/verified effect, pending/uncertain, expected refusal/caller error, actual defect symptom and missing coverage separately. Retain concise diagnostic text and evidence pins for each suspected Problem; deduplicate by invariant and canonical call ownership later. Do not treat the same validation/lifecycle observation as two independent calls or two new Problems. Exclude Graph UI, release/commit/logging/graph feature analysis unless directly causal to a scoped operation and clearly marked supporting evidence. Do not reread current implementation to replace historical evidence.

Use a Luna worker and at most15minutes own work; split further before exceeding it. No MCP calls, production probes/tests, server lifecycle action, product/Atom/Git mutation or historical effect replay. Reports are non-authoritative scratch evidence. Current-state checking and Concern creation/disposition remain later gated work.

### Accepted bounded input

The corrected immutable direct-native subset is ready for semantic review. This Task is rebound to its exact ownership above; release-v1 is historical candidate evidence only. Source provenance and unobserved operation coverage limitations remain explicit. Stop at 15 minutes of own work and report any unreviewed remainder before further execution.

### Definition of Done

Every assigned record has an explicit evidence-backed outcome or attribution gap, all concrete candidate Problems have exact historical references, and limitations/no-call cases are truthful. Planning checkpoint: Completed all 140 assigned calls: 108 Subject-preparation calls (104 staging, three completed scratch packets, one expected source-boundary refusal) plus 32 status calls (17 previews, 15 queued). Scratch staging is not an Atom update. One follow-up for CA-P-1911 is interrupted_pending with LifecycleError and no effect references; cause and present disposition remain unknown. No Draft promotion success or status effect is inferred. Evidence: .anechoic_tmp/mcp-audit-20261020/semantic/subject-status/.
