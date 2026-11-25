The before state is an **uncommitted integration canary**, not a Git revision. The parent Git launcher used legacy selection and is not the failing state. The generic revision-only replay cannot represent this case; use the shared checkout scanner with the byte-evidenced overlay described below.

BB thread `thr_8zxi7bmrvv`, event 16909, recorded the full native selection and backend source in the integration checkout. The selection lacks `compose_project`. The backend requires it. Event 16921 recorded the staged launcher diff, which matches the fixed Git launcher exactly.

Event 16902 recorded the complete native startup source, which matches the fixed Git blob. Event 17179 reported an isolated native launcher attempt ending in `DOCKER_START_FAILED`, with the missing property reported as its cause. Event 17412 reported the isolated canary passing after the fix.

For replay, check out `overlay_base` as detached Git state. Verify the SHA-256 of each `overlay` fixture in `case.json` and copy it to its listed path in the scratch checkout. Scan the fixed checkout and the overlay separately.

The overlay reconstructs these four relevant observed files; it does not claim every byte in the integration worktree was recovered at the failure instant.

`check.lean` and the analyzer model the selected native path and property boundary. They do not prove end-to-end launch, arbitrary Python behavior, or a production outage. The recorded canary is historical evidence, not a new Docker run.
