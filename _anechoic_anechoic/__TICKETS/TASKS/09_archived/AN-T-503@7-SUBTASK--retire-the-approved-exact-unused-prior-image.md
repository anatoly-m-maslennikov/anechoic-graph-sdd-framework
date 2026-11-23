---
atom_family: TKT
atom_id: AN-T-503
container:
  component: C00
priority: 2
context:
  template: task
  label: Subtask
state:
  status: archived
  version: 7
  updated_at: 2026-10-24 11:29:41 +0400
---
## Summary

Retire the approved exact unused prior image

# Summary

Retire the approved exact unused prior image

## Objective

After independent P1704 acceptance of D573@2, complete the conditional exact-removal path within <=15 minutes.

## Details

Own only RELEASE_VERSION/release_image.py and tests/test_release_image.py. Current observer frontier is37 fake-image methods, no removal. Read exact D573@2 SHA5db7045ec34fbd9aea129d63262f6fce1ac5a6bff2b147af90a9fad6e560adad. Reopen the actual authoritative Framework Instance Settings file and require its full digest to match the sealed candidate/promotion frontier. Parse only the closed explicit retention table: missing/stale/malformed/unknown remains pending; retain_prior retains; until_verified_promotion requires every actual successful same-candidate gate and known absence of required old-image refs plus all running/stopped containers. Historical evidence stays intact and does not automatically become required retention.

Only then issue one exact docker image rm immutable-prior-ID without force/prune and independently observe whether that identity is absent. Missing/mismatched/used/unknown identities, CLI denial/failure, race and recording uncertainty yield truthful effects/outcomes; no mutable tag or caller flag admits removal. Never remove the candidate image. Golden-first fake executor only, including configured success and all conservative refusal/recovery paths. No actual image/container operation, settings value, source/Plan/Git/provider edit or C447/C449 workaround. Current fifteen-route production manifest remains unchanged; P1706 completes separate source-admission packaging before any selected runtime exposure.

## Definition of Done

Save exact hashes/API and focused configured-removal/retention/refusal/recording evidence. Actual image execution, source admission/provider registration and full Release proof remain separate.
