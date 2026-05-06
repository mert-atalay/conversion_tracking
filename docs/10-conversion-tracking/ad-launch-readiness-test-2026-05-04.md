# Ad Launch Readiness Test

Last updated: 2026-05-05

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
| Franchise Canada `franchise.cefa.ca` | Directionally ready after post-Version-54 browser QA | The helper event remains `franchise_inquiry_submit`, but GTM Version `54` now maps Form `1` to existing learning destinations: Google Ads primary `fr_application_submit` and Meta `Fr Application Submit`. Browser QA confirmed the Ads/GA4 path and Meta script execution. Meta Events Manager and delayed platform reporting confirmation remain before aggressive spend. |
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
| Live GTM container | `GTM-TPJGHFS`, live Version `54`: `CEFA Franchise Canada legacy thank-you duplicate guard - 2026-05-05`. |
| Website events | `franchise_inquiry_submit` and `real_estate_site_submit`. |
| GA4 mapping | Active tags send both helper dispatch events to GA4 `generate_lead` on `G-6EMKPZD7RD`. |
| GA4 processed report | Last 7 days: helper `generate_lead` Form `1` / `franchise_inquiry` had `1` event and `1` key event. Non-helper `generate_lead` rows also exist. |
| Meta destination | Shared dataset `918227085392601`; GTM tag `52` now sends Form `1` as `Fr Application Submit` with helper `event_id`, matching custom conversion `Fr Application Submit_CAD` ID `1146840919855743`. Prior UI evidence for `Fr Inquiry Submit` is now historical/reference only. |
| Gravity Forms add-on feed | No Gravity Forms Google Analytics feed found. |
| Google Ads account | `3820636025` / `CEFA Franchisor`. |
| Existing primary action | `fr_application_submit` / ID `6472168961` is `ENABLED`, `primary_for_goal=true`, `include_in_conversions_metric=true`, label `AW-11088792613/cys-CIHslY4YEKWYxqcp`; GTM tag `27` now fires this action from helper dispatch trigger `197`. |
| Secondary inquiry Ads tag | `fr_inquiry_submit` / ID `6472168964`, label `AW-11088792613/MfYYCITslY4YEKWYxqcp`, is paused in GTM tag `28` to avoid duplicate final Ads hits. |
| Current helper site Ads tag | `real_estate_site_submit` fires secondary action `fr_site_form_submit` / ID `6472168970`, label `AW-11088792613/vq7GCIrslY4YEKWYxqcp`. |
| Google Ads recent reporting | Last 30 days: `fr_application_submit` had `4` all conversions and `2` conversions; `generate_lead (GA4)` had `4` all conversions and `0` conversions. |
| Legacy duplicate guard | Old `/thank-you` pageview trigger `38` is renamed `Legacy DISABLED - Fr Application Submit_ollo` and only matches `__cefa_disabled_legacy_thank_you_application_submit__`; old Meta pageview tag `51` is paused. |
| Post-Version-54 browser QA | Controlled Form `1` submit reached `/inquiry-thank-you/` with event ID `ad5901f8-0dbb-4281-97cc-88dd0c2d86d3`. Browser proof showed one `franchise_inquiry_submit`, one dispatch `cefa_franchise_inquiry_dispatch`, Google Ads label `cys-CIHslY4YEKWYxqcp`, GA4 `generate_lead`, no secondary Ads label `MfYYCITslY4YEKWYxqcp`, and Meta `Fr Application Submit` script execution. |

### Decision

Franchise Canada has been corrected for continuity in GTM, and the post-Version-54 browser QA passed for the core Ads/GA4 path.

The prior issue was not missing tracking. The issue was destination mismatch:

- Current primary learning action: `fr_application_submit`.
- Prior helper inquiry action: `fr_inquiry_submit`, which was secondary and not included in conversions.

Implemented fix:

1. Preserved learning by mapping the new `franchise_inquiry_submit` helper event to existing primary `fr_application_submit` label `AW-11088792613/cys-CIHslY4YEKWYxqcp`.
2. Preserved Meta continuity by mapping the helper event to `Fr Application Submit` on shared dataset `918227085392601`.
3. Kept `real_estate_site_submit` secondary unless real-estate site submissions are later approved as a bidding event.
4. Kept Meta on the shared dataset during transition to avoid a learning reset.

Remaining confirmation:

1. Confirm `Fr Application Submit` receipt in Meta Events Manager after platform processing delay.
2. Confirm delayed processed rows in GA4 and Google Ads reporting.

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
| 1 | Franchise Canada delayed platform confirmation | Confirm Meta Events Manager receipt for `Fr Application Submit` and delayed processed GA4/Google Ads rows after the post-Version-54 browser QA. | No new strategy decision; platform reporting evidence needed |
| 2 | Franchise USA Google Ads | Add a final helper Ads tag for `cefa_franchise_us_inquiry_dispatch`, preferably to existing primary `Application Submit (USA)`. | Yes |
| 3 | Franchise USA duplicate source | Disable or prove audit-only the active Gravity Forms Google Analytics Form `1` feed. | Yes |
| 4 | USA reporting | Decide whether GA4 property `CEFA Franchise - USA.` should stay `CAD` or move to `USD`. | Yes |
| 5 | Parent | Start/continue ads using `Inquiry Submit_ollo`; monitor helper-filtered GA4 and BigQuery. | No blocker |
