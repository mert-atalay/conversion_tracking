# Source Of Truth Rules

Last updated: 2026-05-03

## Authority Order

Use this order when sources conflict:

1. Live verified systems: WordPress, Gravity Forms, GTM, GA4, Google Ads, Meta, BigQuery, CRM exports, or browser/network proof.
2. This repo's runtime code and current workstream docs for facts that have been migrated, checked, and marked as current.
3. CEFA local conversion-tracking knowledge base in `/Users/matthewbison/Desktop/cefa-nexus/CEFA/cefa conversion tracking/` for unmigrated conversion-tracking evidence.
4. CEFA local NEXUS context in `/Users/matthewbison/Desktop/cefa-nexus/CEFA/.agency/context/`.
5. CEFA Ops vault/source files explicitly cited by a doc.
6. External platform best practices.

If a source is not verified in the current task, mark it as `Partial`, `Pending`, or `Open question`.

## Stable Current Decisions

| Decision | Current source |
|---|---|
| Parent canonical submit event is `school_inquiry_submit`. | Conversion tracking docs and plugin contract |
| Parent platform mapping uses GTM, not hardcoded outbound calls from the helper plugin. | Plugin README and Phase 1A docs |
| Parent school join key is `school_uuid`, emitted as `school_selected_id`. | Master data docs and tracking contract |
| Parent event identity is `event_id`; never use school/program/location IDs as event IDs. | Phase 1A lifecycle docs |
| Parent and franchise measurement boundaries stay separate. | Cross-property and franchise transition docs |
| Gravity Forms Measurement Protocol is audit-only unless explicitly approved as a final conversion source. | Phase 1B MP doc |
| CEFA Meta naming must follow NC1 unless a new naming version is approved. | Naming convention context |
| Runtime plugin code must not replace School Manager, Gravity Forms, GAConnector, KinderTales, Synuma/SiteZeus, GTM, or platform tags. | Plugin README |

## Verification Labels

Use these labels consistently:

| Label | Meaning |
|---|---|
| `Verified` | Confirmed through live system, code, BigQuery/API query, or cited source file. |
| `Partial` | Available but incomplete, mixed-format, source-limited, or not production-normalized. |
| `Pending` | Known needed field or decision, but not confirmed yet. |
| `Open question` | Needs user, agency, platform owner, or source-system confirmation. |
| `Reference only` | Useful background, not a source of operational truth. |

## Cross-Workstream Updates

If a change affects multiple workstreams:

- Update the narrow workstream doc first.
- Add a link from the affected workstream README.
- Update this governance folder only if the decision changes how agents should operate.
- Do not duplicate the same long explanation in several folders.
