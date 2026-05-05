# Reference Data

This folder is for small, reviewable, machine-readable reference data used by the docs and future agents.

## Rules

- Prefer CSV or YAML for small canonical/reference tables.
- Include an adjacent README or header comment explaining source and date.
- Do not store secrets, PII, raw exports, or large platform dumps here.
- If a value is incomplete, use a clear marker such as `pending`; do not guess.

## Current Files

- [cefa-meta-active-object-inventory-2026-04-05-to-2026-05-04.csv](./cefa-meta-active-object-inventory-2026-04-05-to-2026-05-04.csv)
  - Status: `Verified` for live Meta object IDs, current names, delivery window, spend, impressions, and clicks read through the repo-local CEFA Meta CLI.
  - Status: `Partial` for proposed NC2 names and keys because some ad-level values are inferred from incomplete visible names.
  - Scope: CEFA Early Learning `parent` and CEFA Franchisor `franchise` campaigns, ad sets, and ads that delivered from 2026-04-05 through 2026-05-04.
  - Use: active Meta object crosswalk for naming review, UTM planning, and conversion-tracking joins.
  - Guardrail: this is normalized reference data, not a raw Meta export, not a secret source, and not approval to make live Meta changes.

## Planned Files

- `schools.csv`
- `programs.csv`
- `paid-media-accounts.csv`
- `conversion-events.yaml`
