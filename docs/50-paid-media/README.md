# Paid Media Workstream

This folder is for ad-account execution context that depends on conversion tracking, naming, BigQuery, and budget guardrails.

## Local Source References

- `/Users/matthewbison/Desktop/cefa-nexus/CEFA/.agency/context/cefa-paid-media-skill-reference-2026-04-30.md`
- `/Users/matthewbison/Desktop/cefa-nexus/CEFA/.agency/context/cefa-meta-naming-convention-2026-04-28.md`
- CEFA budget workbook path and guardrails from the CEFA repo `AGENTS.md`.

## Rules

- Do not change live budgets from spreadsheet math alone.
- Do not change live campaigns or bidding without explicit approval.
- Do not use platform-reported conversions as business truth when CRM/KinderTales/BigQuery reconciliation is unresolved.
- Keep micro-conversions out of Google Ads bidding unless CEFA explicitly changes that decision.
- Conversion action definitions should link back to `docs/10-conversion-tracking/`.
- Naming should link back to `docs/40-naming-convention/`.

## Suggested Next Files

- `ads-conversion-action-status.md`
- `meta-dataset-and-pixel-status.md`
- `google-ads-primary-secondary-conversions.md`
- `launch-qa-checklist.md`
