---
atom_id: ANECHOIC-GOV-REQU-290
cce_version: cce_1
cce_form: prohibition
subjects:
  governs:
    continuant:
      - external-boundary
version: 12
updated_at: "2026-09-14 06:21:07 +0400"
relations: {}
---
# Requirement — Exclude secrets from ANECHOIC

ANECHOIC never stores, transmits, summarizes, **or** reproduces secret values. secrets include passwords, API keys, access **or** refresh tokens, session cookies, private keys, signing **or** encryption keys, authentication certificates, one-time **or** recovery codes, **and** connection strings **or** URLs containing credentials.

the prohibition covers atomic **and** evergreen artifacts, settings, generated files, runtime traces, logs, prompts, checkpoints, Evaluation inputs **and** results, Test fixtures **and** snapshots, evidence, support bundles, issues, pull requests, commits, **and** release records. a secret **must** be redacted **before** **any** such surface enters ANECHOIC; encoding **or** encrypting a value does **not** make it ordinary ANECHOIC data.

production **and** shared automation use the host's secret injection **or** a dedicated secret manager, **not** a committed file **or** ANECHOIC setting.

email addresses, usernames, **and** account identifiers are identifiers rather than authenticators. they **may** appear **in** ANECHOIC **when** necessary **and** authorized, but **must** be minimized **and** treated as potentially personal data. ANECHOIC does **not** become the runtime owner merely because a human-readable artifact names it.

**if** a secret reaches **any** durable **or** shared surface, stop propagation, revoke **or** rotate it immediately, **then** clean affected carriers **and** record the incident **without** reproducing the value. deleting a current file is **not** sufficient remediation for a value already present **in** durable history **or** another replica.
