# Ad Launch Readiness Test

Last updated: 2026-05-04

## Scope

This check covers whether the current live conversion tracking is safe to use for ads on:

- Parent: `cefa.ca`
- Franchise Canada: `franchise.cefa.ca`
- Franchise USA: `franchisecefa.com` / `www.franchisecefa.com`

No live GTM, GA4, Google Ads, Meta, or WordPress setting changes were made during this check.

No new live lead submissions were created during this pass. The evidence below uses live GTM runtime, GA4 processed reports, BigQuery export, Google Ads API, Meta Events Manager UI, and WP-CLI/GF feed checks.

## Executive Decision

| Surface | Launch readiness | Decision |
|---|---|---|
| Parent `cefa.ca` | Ready for Google Ads launch/use | The helper path maps to the existing primary Google Ads action `Inquiry Submit_ollo` and GA4/BigQuery show helper events processing. Meta shared dataset has recent `Inquiry Submit` activity. |
| Franchise Canada `franchise.cefa.ca` | Ready for Meta/GA4 reporting; not fully ready for Google Ads bidding without one decision | The helper events process in GA4 and the shared Meta dataset has recent `Fr Inquiry Submit` / `Fr Site Form Submit` activity. Google Ads currently sends the new helper inquiry event to secondary `fr_inquiry_submit`, while the existing primary bidding action remains `fr_application_submit` on the old trigger. |
| Franchise USA `franchisecefa.com` | Ready for Meta/GA4 reporting; not ready for Google Ads final-submit bidding without one GTM change | USA helper events process in GA4 and Meta Events Manager shows standard `Lead` received on the new USA dataset. Google Ads has an existing primary `Application Submit (USA)` action, but the live USA GTM helper submit path does not yet fire a final Google Ads conversion tag. |

## Parent `cefa.ca`

### Evidence

| Check | Result |
|---|---|
| Live GTM container | `GTM-NZ6N7WNC`, live Version `7`: `CEFA parent Ads label correction - Inquiry Submit_ollo - 2026-05-04`. |
| Website event | `school_inquiry_submit`. |
| GA4 mapping | Active tag sends `school_inquiry_submit` to GA4 `generate_lead` on `G-T65G018LYB`. |
| Google Ads mapping | Active tag sends `school_inquiry_submit` to `AW-802334988/cFt-CMrLufgCEIzSyv4C`, which is `Inquiry Submit_ollo`. |
| Google Ads action | `Inquiry Submit_ollo` / ID `789472714` is `ENABLED`, `primary_for_goal=true`, `include_in_conversions_metric=true`. |
| Google Ads recent reporting | Last 30 days: `Inquiry Submit_ollo` had `646.231258` all conversions and `638.231258` conversions. |
| GA4 processed report | Last 7 days: helper `generate_lead` for Form `4` / `parent_inquiry` had `175` events and `175` key events. |
| BigQuery export | Last 7 days: `160` helper `generate_lead` rows, `160` distinct event IDs, `0` missing event IDs, `0` duplicate event-ID delta. |
| Historical event-ID caveat | BigQuery still contains one 2026-05-03 row where `event_id=school_selected_id`; plugin `0.4.3` was deployed after this and is intended to guard against that failure mode. |
| Gravity Forms add-on feed | No Gravity Forms Google Analytics feed found. Only Mailchimp feed is active. |
| Meta Events Manager | Shared dataset `918227085392601` shows `Inquiry Submit` active, `4.9K` total events, last received roughly 3 hours before the UI check. |

### Decision

Parent can be used for ads now.

Recommended bidding action:

- Google Ads: keep existing primary `Inquiry Submit_ollo`.
- GA4: use helper-filtered `generate_lead` for reporting; do not use unfiltered GA4 `generate_lead` as the business truth.
- Meta: current shared dataset event is active; keep monitoring before Phase 1B CAPI/server-side work.

## Franchise Canada `franchise.cefa.ca`

### Evidence

| Check | Result |
|---|---|
| Live GTM container | `GTM-TPJGHFS`, live Version `52`: `CEFA Franchise Canada Phase 1 helper-event mapping - 2026-05-01`. |
| Website events | `franchise_inquiry_submit` and `real_estate_site_submit`. |
| GA4 mapping | Active tags send both helper dispatch events to GA4 `generate_lead` on `G-6EMKPZD7RD`. |
| GA4 processed report | Last 7 days: helper `generate_lead` Form `1` / `franchise_inquiry` had `1` event and `1` key event. Non-helper `generate_lead` rows also exist. |
| Meta Events Manager | Shared dataset `918227085392601` shows `Fr Inquiry Submit` active, `6` total events, last received roughly 3 hours before the UI check; `Fr Site Form Submit` active, `14` total events, last received roughly 2 hours before the UI check. |
| Gravity Forms add-on feed | No Gravity Forms Google Analytics feed found. |
| Google Ads account | `3820636025` / `CEFA Franchisor`. |
| Existing primary action | `fr_application_submit` / ID `6472168961` is `ENABLED`, `primary_for_goal=true`, `include_in_conversions_metric=true`, label `AW-11088792613/cys-CIHslY4YEKWYxqcp`. |
| Current helper inquiry Ads tag | `franchise_inquiry_submit` fires secondary action `fr_inquiry_submit` / ID `6472168964`, label `AW-11088792613/MfYYCITslY4YEKWYxqcp`. |
| Current helper site Ads tag | `real_estate_site_submit` fires secondary action `fr_site_form_submit` / ID `6472168970`, label `AW-11088792613/vq7GCIrslY4YEKWYxqcp`. |
| Google Ads recent reporting | Last 30 days: `fr_application_submit` had `4` all conversions and `2` conversions; `generate_lead (GA4)` had `4` all conversions and `0` conversions. |

### Decision

Franchise Canada is safe for Meta and GA4 reporting, but Google Ads bidding is not fully aligned to the new helper form path yet.

The issue is not that tracking is missing. The issue is which Google Ads conversion should receive the new confirmed form event:

- Current primary learning action: `fr_application_submit`.
- Current helper inquiry action: `fr_inquiry_submit`, which is secondary and not included in conversions.

Recommended fix before scaling Google Ads franchise Canada:

1. Preserve learning by mapping the new `franchise_inquiry_submit` helper event to the existing primary action `fr_application_submit` label `AW-11088792613/cys-CIHslY4YEKWYxqcp`, or explicitly approve making `fr_inquiry_submit` primary.
2. Keep `real_estate_site_submit` as secondary unless real-estate site submissions should be a bidding event.
3. Keep Meta on the shared dataset during the transition to avoid a learning reset.

## Franchise USA `franchisecefa.com`

### Evidence

| Check | Result |
|---|---|
| Live GTM container | `GTM-5LZMHBZL`, live Version `18`: `CEFA Franchise USA Meta Lead reliability fix - 2026-05-04`. |
| Website events | `franchise_inquiry_submit` and `real_estate_site_submit`. |
| GA4 mapping | Active tags send both USA helper dispatch events to GA4 `generate_lead` on `G-YL1KQPWV0M`. |
| GA4 processed report | Last 7 days: helper Form `1` / `franchise_inquiry` had `2` `generate_lead` events and `2` key events; helper Form `2` / `site_inquiry` had `2` `generate_lead` events and `2` key events. |
| Meta dataset | USA dataset `1531247935333023` is active through GTM. |
| Meta Events Manager | USA dataset shows standard `Lead` active, `2` total events, last received roughly 21 minutes before the UI check. |
| Meta custom conversion | `USA Franchise Lead` / ID `1915200622465036` exists for standard `Lead` plus `/inquiry-thank-you/`. |
| Old shared pixel | Public USA GTM/runtime uses `1531247935333023`; prior checks found zero active `918227085392601` occurrences on USA form pages. |
| Gravity Forms add-on feed | USA still has an active Gravity Forms Google Analytics feed: feed ID `1`, Form `1`, active `1`. |
| Google Ads account | `3820636025` / `CEFA Franchisor`. |
| Existing primary USA action | `Application Submit (USA)` / ID `7482298930` is `ENABLED`, `primary_for_goal=true`, `include_in_conversions_metric=true`, label `AW-11088792613/fnFOCLKk6-8bEKWYxqcp`, value `600`, currency `CAD`. |
| Current USA helper Ads tag | No final Google Ads helper-submit tag is active for USA Form `1` or Form `2`; only Google Ads remarketing remains active. |
| GA4 currency | USA GA4 property `519783092` is still `CAD`; this should be reviewed if USA reporting should be USD. |

### Decision

Franchise USA is safe for Meta and GA4 reporting, and Meta can start using the new USA dataset/custom conversion if the intentional tradeoff is to separate USA from the shared dataset.

Franchise USA is not ready for Google Ads final-submit bidding until the helper event is mapped to a Google Ads conversion action.

Recommended fix before scaling Google Ads franchise USA:

1. Add a GTM Google Ads final conversion tag on `cefa_franchise_us_inquiry_dispatch`.
2. Use the existing primary action `Application Submit (USA)` label `AW-11088792613/fnFOCLKk6-8bEKWYxqcp` if the goal is to preserve the existing USA Ads action rather than creating a new action.
3. Decide whether Form `2` / `real_estate_site_submit` should stay reporting-only or receive a separate secondary Ads action.
4. Disable the USA Gravity Forms Google Analytics Form `1` feed or prove it is audit-only and not imported/mapped as a final conversion.
5. Review USA GA4 currency `CAD` vs `USD` before reporting signoff.

## Cross-Property Notes

- GA4 processed reports contain both helper and non-helper `generate_lead` rows. For reporting, filter to `tracking_source=helper_plugin` when measuring the new clean path.
- Parent and franchise Canada still use the shared Meta dataset `918227085392601`. USA is separated to dataset `1531247935333023`.
- Micro-conversions should remain reporting-only unless explicitly approved for bidding.
- Gravity Forms Measurement Protocol should remain audit-only for now. Do not send a second `generate_lead` through Measurement Protocol.

## Next Actions Before Ads Scaling

| Priority | Surface | Action | Owner decision needed |
|---:|---|---|---|
| 1 | Franchise Canada Google Ads | Decide whether to map `franchise_inquiry_submit` to existing primary `fr_application_submit` or make `fr_inquiry_submit` primary. | Yes |
| 2 | Franchise USA Google Ads | Add a final helper Ads tag for `cefa_franchise_us_inquiry_dispatch`, preferably to existing primary `Application Submit (USA)`. | Yes |
| 3 | Franchise USA duplicate source | Disable or prove audit-only the active Gravity Forms Google Analytics Form `1` feed. | Yes |
| 4 | USA reporting | Decide whether GA4 property `CEFA Franchise - USA.` should stay `CAD` or move to `USD`. | Yes |
| 5 | Parent | Start/continue ads using `Inquiry Submit_ollo`; monitor helper-filtered GA4 and BigQuery. | No blocker |

