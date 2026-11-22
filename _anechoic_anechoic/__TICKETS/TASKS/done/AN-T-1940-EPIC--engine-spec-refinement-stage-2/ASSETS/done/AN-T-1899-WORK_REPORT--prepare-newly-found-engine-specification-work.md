---
atom_family: TKT
atom_id: AN-T-1899
container:
  atom: AN-T-1940
priority: 2
context:
  template: work_report
state:
  status: done
  version: 3
  updated_at: 2026-11-10 21:20:58 +0400
---

## Summary

Prepare newly found Engine specification work

## Details

Completed the plugin-free hook/session and Frontend source preparation and review. R3014 declares CODEX_HOOK; R3016 now requires each Project/session to obtain its own active Workflow Runs and recorded history. R3022 and the adopted Frontend sources preserve Frontend Engineering, Visual Design, Query Authoring and interface boundaries. The thin topic rows are in canonical-topics.tsv; the adoption manifest pins the reviewed sources.

The hook boundary uses codex_session_id; generic runtime uses session_id. These are source decisions, not implementation or native-plugin acceptance. P2855 and P2856 are Done; no blanket hook or Frontend hold remains.
