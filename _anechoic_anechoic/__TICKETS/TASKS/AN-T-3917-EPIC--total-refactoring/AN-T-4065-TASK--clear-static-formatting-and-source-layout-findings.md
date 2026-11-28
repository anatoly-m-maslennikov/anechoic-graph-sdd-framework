---
atom_family: TKT
atom_id: AN-T-4065
container:
  atom: AN-T-3917
priority: 2
context:
  template: task
  label: Task
state:
  status: in_queue
  version: 1
  updated_at: "2026-11-28T15:17:10+00:00"
---

## Summary

Clear Static formatting and source layout findings

## Acceptance

Use the committed formatter and the full-checkout line and source
size checks. Resolve each finding without changing supported
behavior. Preserve exact fixtures and generated artifact checks.
Retain every selected test and its normal discovery path. Verify
the 6 KiB Module and 45-nonblank-line function limits, the four-level
nesting cap, and the 67 Rule for folders (AN-S-5197).

## Progress

The checked formatting pass preserved Python syntax trees and avoided
new 45/300 violations. It kept the imported Markdown fixtures and the
hash-bound generated Scope predicate intact. Narrow formatter directives
retain required wraps for long imports.

The 2026-11-27 Static run reports 839 files that need formatting,
24,642 overlength lines, and eight size findings. The previous run
reported 869 files, 34,692 lines, and 11 size findings. All remaining
size findings are in Model Generator.

The pinned formatter count fell from 432 to 254 files in the current
cleanup. Each completed batch preserves the 300/45 limits. The pinned
full-checkout Ruff lint has zero findings.

The configured Ruff lint and formatter pass across the checkout.
All 2,129 files in the formatter scope are formatted. The full 300/45
check has zero findings.

The Operator deferred the 79-character findings for v0.5.0. Static
skips the width check. Track the remaining width work in this Task.

The 6 KiB Module check reports 960 findings. The 45-line function check
reports zero findings.

The initial 67 Rule scan reports 75 folders with findings. Of these, 71 exceed the
42 KiB budget and six exceed the five-subfolder cap. Two exceed both.
No folder has more than one direct test subfolder.

After the Terra cleanup, the source layout scan reports zero nesting or
function-length violations, 949 oversized Modules, and 74 folders with
67 Rule findings. Six individual files exceed the entire folder budget.

The revised 67 Rule applies the 42 KiB budget to direct executable files
and caps direct non-executable files at seven. The scan finds 49 folders
over the executable-byte cap, 23 over the asset count, and six over the
ordinary subfolder cap. In all, 74 folders have findings.

The next Terra pass cleared 11 of the 74 folders. The retained moves pass
the Engine Studio and Runtime Images import gates. All ten relocated
registered test paths resolve in the Test Suite. The release input test
observed Project carrier changes during capture.

The Operator kept the Component hierarchy. The 67 Rule excludes declared
child Component folders from the ordinary subfolder count. The scan
no longer flags Engine Studio for its ten Components. Sixty folders
still have findings, including two ordinary subfolder overages.

Terra then cleared 16 folders. The scan now flags 44 folders. All 44
exceed the executable byte budget, and two also exceed the asset count.
Both ordinary subfolder findings are clear. Fixture bytes and the 35
golden case identities remain intact.

The package migration cleared five more folders. Thirty-nine still exceed
the 42 KiB budget; one also exceeds the asset count. The remaining folders
contain 8,644,310 direct executable bytes above their combined budgets.
Import ownership and scoped Engine Studio and Release import checks passed.
The Runtime Images split updated all 18 affected Local Release callers.

The repository-wide 67 Rule scan cleared the last 39 folders. The
Component hierarchy and folder thresholds stayed in force. Moved
test selectors resolve. Import ownership, Engine Studio and Release
Code Access, and configured Ruff lint pass.
