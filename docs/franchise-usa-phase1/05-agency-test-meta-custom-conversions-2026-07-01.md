# Franchise USA Agency Test Meta Custom Conversions

Last updated: 2026-07-09

Status: `In-house custom conversion proven; GTM Version 25 published; partner remains on broad USA inquiry conversion`

## Current Operating Decision

The current comparison does not require a partner marker.

- Keep the in-house campaign on `CEFA | Franchise USA | In-House Lead`. Its `cefa_agency_test=fr_us_in_house` parameter remains mandatory because that custom conversion explicitly filters on the parameter.
- Keep the partner/Reshift campaign on the existing broad `USA Franchise Lead` custom conversion. Meta attributes the result to the partner campaign/ad set, so campaign-level reporting does not require `cefa_agency_test=fr_us_partner`.
- Keep `CEFA | Franchise USA | Partner Lead` available but unused. Do not switch the partner ad set to it unless CEFA later requires a partner-only custom-conversion row independent of campaign attribution.
- GTM Version `25` implements the clearing-only rule: a fresh landing from exact partner campaign `120244631021580488`, ad set `120244631021560488`, or governed slug `reshift_meta` expires stale `fr_us_in_house` without storing `fr_us_partner`.
- Compare the agencies by campaign/ad-set ID, spend, attributed inquiry conversions, cost per inquiry, qualified leads, and downstream outcomes. Use Meta Experiments or mutually exclusive audiences when practical.

This is intentionally asymmetric but simpler: in-house has a protected custom conversion; partner uses the established broad USA inquiry conversion. The two campaigns still remain distinguishable in Ads Manager and reporting by their campaign/ad-set IDs.

The in-house marker lifetime now matches the active seven-day Meta click-through attribution window. Candidate and live-browser tests proved in-house persistence, partner clearing, direct-return preservation, and partner precedence over stale in-house landing evidence.

## Summary

This note records the Franchise USA Meta agency-test conversion structure for the planned in-house vs partner campaign comparison.

Do not create duplicate lead events such as `Agency A Lead` or `Agency B Lead`. Keep the underlying destination event as Meta standard `Lead` on the USA franchise dataset, then separate the test buckets with one non-PII event parameter:

`cefa_agency_test`

## Meta Objects Created

Ad account:

- `act_505300888223754` / CEFA Franchisor

Dataset:

- `1531247935333023` / `CEFA Franchise USA`

Custom conversions:

| Name | ID | Rule |
| --- | --- | --- |
| `CEFA | Franchise USA | In-House Lead` | `36521415357505819` | Meta `Lead` + URL contains `inquiry-thank-you` + `cefa_agency_test = fr_us_in_house` |
| `CEFA | Franchise USA | Partner Lead` | `1352507926817889` | Meta `Lead` + URL contains `inquiry-thank-you` + `cefa_agency_test = fr_us_partner` |

The existing broader custom conversion remains active:

| Name | ID | Rule |
| --- | --- | --- |
| `USA Franchise Lead` | `1915200622465036` | Meta `Lead` + URL contains `inquiry-thank-you` |

## Agency-Specific URL Tags

Only the in-house marker is required for the current operating setup. The partner example below is retained for a possible future partner-only custom conversion, not as a current implementation requirement.

Use these final URL parameters for the two test campaigns:

In-house:

```text
utm_source=meta&utm_medium=paid_social&utm_campaign=franchise_us_agency_test&utm_content=in_house&cefa_agency_test=fr_us_in_house
```

Optional future partner-only setup:

```text
utm_source=meta&utm_medium=paid_social&utm_campaign=franchise_us_agency_test&utm_content=partner&cefa_agency_test=fr_us_partner
```

Example in-house homepage URL:

```text
https://franchisecefa.com/?utm_source=meta&utm_medium=paid_social&utm_campaign=franchise_us_agency_test&utm_content=in_house&cefa_agency_test=fr_us_in_house
```

The live GTM implementation also accepts a shorter URL alias and normalizes it into the canonical Meta event parameter:

```text
cefa_agency=in_house -> cefa_agency_test=fr_us_in_house
cefa_agency=partner -> cefa_agency_test=fr_us_partner
```

## Event Parameter Publication

The URL parameter alone is not enough. Meta can only match the new custom conversions after the final Meta `Lead` event receives:

```json
{"cefa_agency_test":"fr_us_in_house"}
```

or:

```json
{"cefa_agency_test":"fr_us_partner"}
```

Published live implementation:

1. Persist `cefa_agency_test` from the landing URL into a first-party cookie or session storage on `franchisecefa.com`.
2. Read that value on the inquiry thank-you page.
3. Add it to the existing GTM Meta `Lead` tags for Franchise USA inquiry leads.
4. Keep the existing event name, dataset, `eventID`, and thank-you-path rule unchanged.

Relevant GTM tags:

- `267` / `CEFA - Franchise USA - Meta Lead - Franchise Inquiry`
- `268` / `CEFA - Franchise USA - Meta Lead - Site Submit`
- `270` / `CEFA - Franchise USA - GAConnector Hidden Field Writer`

For this agency test, the primary reporting conversion should be the inquiry form path. Do not count site-submit leads into the agency test unless paid media explicitly approves that as part of the test design.

## 2026-07-01 GTM Publish Evidence

On 2026-07-01, GTM publish access was completed through service-account impersonation for:

`marketing-cefa-795@marketing-api-488017.iam.gserviceaccount.com`

Published container:

- Account: `6004334435` / `CEFA Franchise`
- Container: `204988779` / `GTM-5LZMHBZL` / `USA-CEFA`
- Version: `20`
- Version name: `2026-07-01 - Franchise USA agency test Meta parameter`

Changed live GTM tags:

- `267` / added `cefa_agency_test` to the Meta standard `Lead` custom data for Form `1`.
- `268` / added `cefa_agency_test` to the Meta standard `Lead` custom data for Form `2`.
- `270` / persists the allowed agency-test URL value into a first-party `cefa_agency_test` cookie on the two live USA form pages.

Public runtime check on 2026-07-01:

- `https://www.googletagmanager.com/gtm.js?id=GTM-5LZMHBZL` still contains the USA dataset `1531247935333023`.
- The published GTM runtime now contains `cefa_agency_test`, `fr_us_in_house`, and `fr_us_partner`.
- Live GTM Version `20` read-back confirms tags `267`, `268`, and `270` contain all three agency-test markers.

The in-house custom conversion can fire once Meta receives a live `Lead` event with the matching in-house parameter. The partner custom conversion remains intentionally unused under the current operating decision.

## 2026-07-09 Homepage-First Persistence Publish

Reason:

- Paid traffic should land on the Franchise USA homepage first, not directly on the inquiry form.
- GTM Version `20` already added `cefa_agency_test` to the Franchise USA Meta `Lead` tags, but its first-party cookie persistence ran only on the two form pages.
- Homepage-first traffic with `cefa_agency_test=fr_us_in_house` needed the same value persisted before the visitor later reached the inquiry thank-you page.

Published container:

- Account: `6004334435` / `CEFA Franchise`
- Container: `204988779` / `GTM-5LZMHBZL` / `USA-CEFA`
- Version: `21`
- Version name: `2026-07-09 - Franchise USA homepage agency persistence`

Added GTM objects:

- Trigger `271` / `CEFA - Franchise USA - DOM Ready - franchisecefa.com`
- Tag `272` / `CEFA - Franchise USA - Agency Test Cookie Writer`

Behavior:

- Runs on `franchisecefa.com` DOM Ready.
- Writes first-party cookie `cefa_agency_test` only when the URL or GAConnector landing URL contains an allowed value.
- Allowed values normalize to:
  - `fr_us_in_house`
  - `fr_us_partner`
- Does not fire Meta, GA4, Google Ads, or any conversion event.
- Does not change the existing Meta `Lead` tags, event names, event IDs, datasets, or custom-conversion rules.

Homepage browser QA on 2026-07-09:

- Loaded:
  `https://franchisecefa.com/?cefa_agency_test=fr_us_in_house&utm_source=meta&utm_medium=paid_social&utm_campaign=homepage_agency_test_probe&utm_content=in_house`
- Observed homepage cookie:
  `cefa_agency_test=fr_us_in_house`, domain `.franchisecefa.com`, path `/`
- Navigated in the same browser context to:
  `https://franchisecefa.com/available-opportunities/franchising-inquiry/`
- Observed the same cookie still available on the form page.

This confirms homepage-first Meta traffic can carry the agency marker forward to the existing inquiry thank-you `Lead` event.

## 2026-07-09 In-House Campaign Fallback Publish

Live Meta audit finding:

- Campaign `120247607795440488` had `12` active ads.
- `3` active ads already carried the canonical `cefa_agency_test=fr_us_in_house` parameter.
- The other `9` active ads carried the exact static in-house `utm_campaign` slug and/or dynamic `utm_id={{campaign.id}}`, but no explicit agency marker.
- Editing those existing post/video creatives would have risked review and learning disruption.

Published container:

- Version: `22`
- Version name: `2026-07-09 - Franchise USA in-house campaign fallback`
- Workspace used: `25`
- Only changed GTM object: tag `272` / `CEFA - Franchise USA - Agency Test Cookie Writer`

Exact fallback mapping:

```text
utm_id=120247607795440488 -> cefa_agency_test=fr_us_in_house
utm_campaign=cefa_franchise_us_nc_charlotte_franchise_inquiry_conversion_inhouse_202607 -> cefa_agency_test=fr_us_in_house
```

Safety behavior:

- Explicit `cefa_agency_test` or `cefa_agency` values take precedence.
- Only the exact campaign ID and exact campaign slug are allowlisted; no broad `inhouse` substring inference is used.
- Unknown campaign IDs/slugs remain unclassified.
- No Meta campaign, ad set, ad, creative, budget, targeting, status, custom-conversion rule, dataset, event name, or conversion tag was changed.
- Version comparison confirmed all other `63` tags, `28` triggers, and `73` variables were unchanged.

QA evidence:

- Six local cases passed: canonical in-house, explicit partner precedence, campaign ID, campaign slug, unknown campaign, and GAConnector landing-cookie fallback.
- Public homepage QA confirmed both the campaign ID and campaign slug create `cefa_agency_test=fr_us_in_house` on `.franchisecefa.com`.
- The cookie persisted from the homepage to live Form `1`.
- A no-send inquiry-dispatch test on `/inquiry-thank-you/` produced the standard Meta `Lead` payload for dataset `1531247935333023` with `cefa_agency_test=fr_us_in_house` and an `eventID`.
- The QA replaced `fbq` temporarily and observed zero outbound Meta `Lead` requests, so it created neither a CRM lead nor a Meta conversion.

The explicit `cefa_agency_test` parameter remains the canonical implementation. Version `22` is a controlled safety fallback for the current in-house campaign, not a general naming-based classifier.

## 2026-07-09 Live End-to-End In-House Lead Test

Approved production test path:

- Active campaign: `120247607795440488`
- Active ad set: `120247612154860488`
- Active ad: `120247612154890488`
- Market: `Charlotte, NC`
- Test record label: `CEFA Meta` / `InHouse QA 20260709`
- The first attempt used the reserved `example.com` domain, was rejected by form validation, and did not create a successful lead.

The successful submission preserved:

- `cefa_agency_test=fr_us_in_house`
- `utm_source=facebook`
- `utm_medium=paid_social`
- `utm_campaign=cefa_franchise_us_nc_charlotte_franchise_inquiry_202607`
- `utm_term=120247612154860488`
- `utm_content=120247612154890488`

Successful result:

- Production Form `1` reached `/inquiry-thank-you/` for `Charlotte, NC`.
- Event ID: `d7b6b67f-b4f8-4aa1-8f35-144453174aa3`
- The browser Pixel sent `Lead` with `cefa_agency_test=fr_us_in_house`.
- The server transport sent `Lead` with the same event ID and agency marker, preserving deduplication.
- Meta updated `CEFA | Franchise USA | In-House Lead` from `2026-07-01T09:36:38-07:00` to `2026-07-09T11:48:46-07:00`.
- Meta updated `USA Franchise Lead` to `2026-07-09T11:48:45-07:00`.
- `CEFA | Franchise USA | Partner Lead` remained unfired, confirming rule isolation.

Attribution boundary:

- The test started from an ad preview and then reproduced the ad's destination parameters; it did not contain a genuine served-ad `fbclid`.
- Therefore it validates the website, Pixel, server transport, event parameter, and custom-conversion rule, but it is not expected to appear as a campaign-attributed result.
- Both active ad sets correctly remained on `0 (CEFA | Franchise USA | In-House Lead)` immediately after the test.
- A genuine lead following a delivered in-house ad click is the remaining campaign-attribution proof.

## 2026-07-09 Active In-House Ad URL Audit

Fresh Meta MCP and Graph API read-back after the live lead test:

- Campaign `120247607795440488` contained `12` active/effectively active ads across `2` active ad sets.
- All `12/12` ads pointed to `https://franchisecefa.com/`.
- All `12/12` used `utm_medium=paid_social`, dynamic ad-set attribution in `utm_term`, and dynamic ad attribution in `utm_content`.
- `3/12` video ads carried the canonical `cefa_agency_test=fr_us_in_house` marker directly.
- `9/12` ads carried both exact fallback inputs: `utm_id={{campaign.id}}` and `utm_campaign=cefa_franchise_us_nc_charlotte_franchise_inquiry_conversion_inhouse_202607`.
- `0/12` ads carried `fr_us_partner` or any conflicting partner marker.
- A public browser check confirmed a representative fallback URL writes `cefa_agency_test=fr_us_in_house`.
- A precedence check confirmed an explicit `cefa_agency_test=fr_us_partner` remains partner even when in-house fallback parameters are present.

Both active ad sets use:

- Dataset/pixel `1531247935333023` / `CEFA Franchise USA`
- Custom conversion `36521415357505819` / `CEFA | Franchise USA | In-House Lead`
- Rule: `Lead` + URL contains `inquiry-thank-you` + `cefa_agency_test=fr_us_in_house`

The partner custom conversion remains a mutually exclusive rule requiring `cefa_agency_test=fr_us_partner`; it was not selected by either active in-house ad set and did not fire during the approved in-house test.

## 2026-07-01 In-House Browser QA

Safe test method:

- Loaded `https://franchisecefa.com/inquiry-thank-you/?codex_test=1&cefa_agency_test=fr_us_in_house`.
- Did not submit the production Gravity Form, so no CRM/Synuma lead was intentionally created by this QA pass.
- Simulated the GTM helper dispatch event `cefa_franchise_us_inquiry_dispatch` in the browser with `site_context=franchise_us` and `form_family=franchise_inquiry`.

Observed browser result:

- First-party cookie `cefa_agency_test=fr_us_in_house` was set.
- GTM called Meta `fbq('track', 'Lead', ...)` once.
- The Meta `Lead` custom data included `cefa_agency_test: fr_us_in_house`.
- The Meta `Lead` event URL was the `/inquiry-thank-you/` path required by the custom-conversion rule.
- The event used the USA Meta dataset/pixel `1531247935333023`.

Meta API note:

- Dataset `1531247935333023` was active and showed recent `last_fired_time` / `server_last_fired_time`.
- The Meta dataset stats endpoint did not expose a fresh URL-level row during the immediate QA window, so final platform UI confirmation should be checked in Events Manager after processing delay or with one approved live test lead.

## 2026-07-01 In-House Real Lead QA

Real test method:

- Submitted the production Franchise USA Form `1` through the in-house tagged URL:
  `utm_source=meta&utm_medium=paid_social&utm_campaign=franchise_us_agency_test&utm_content=in_house&cefa_agency_test=fr_us_in_house`
- Used an obvious CEFA plus-address test alias and test name beginning with `Codex TEST IGNORE`.
- The first attempt using a reserved `example.com` test email was rejected by the form email validator and did not create a successful lead.

Successful result:

- Thank-you URL reached:
  `https://franchisecefa.com/inquiry-thank-you/?location=atlanta&inquiry=true&cefa_tracking=1&cefa_tracking_event_id=0cd029ef-04c5-46e5-b553-8d768bbd41cd`
- Event ID:
  `0cd029ef-04c5-46e5-b553-8d768bbd41cd`
- Website helper event:
  `franchise_inquiry_submit`
- GTM dispatch event:
  `cefa_franchise_us_inquiry_dispatch`
- Attribution payload included:
  `lc_source=meta`, `lc_medium=paid_social`, `lc_campaign=franchise_us_agency_test`, `lc_content=in_house`
- Meta call observed:
  `fbq('track', 'Lead', ...)`
- Meta `Lead` custom data included:
  `cefa_agency_test: fr_us_in_house`
- Meta dataset/pixel:
  `1531247935333023`

This proves the real Form `1` success path can satisfy the in-house custom-conversion rule:

`Lead` + `/inquiry-thank-you/` URL + `cefa_agency_test = fr_us_in_house`.

## Recommended Reporting And Optimization Design

- Keep the current in-house ad sets optimizing to `36521415357505819` / `CEFA | Franchise USA | In-House Lead` while agency-specific proof is the primary requirement.
- Keep the partner/Reshift campaign optimizing to `1915200622465036` / `USA Franchise Lead`.
- Keep `1352507926817889` / `CEFA | Franchise USA | Partner Lead` available but unused.
- Compare agencies by campaign/ad-set ID. Use the in-house custom conversion for in-house rows and the broad USA inquiry conversion filtered to the partner campaign for partner rows.
- Keep `cefa_agency_test` as the first-party in-house label carried into the final `Lead` event and attribution fields.
- The in-house path needs a click-carried identifier because its custom conversion explicitly filters on that value. The current partner path does not need one because Meta campaign attribution separates its broad inquiry conversions.
- If in-house volume is too low for stable learning, moving it to the broad `USA Franchise Lead` optimization event remains a separate paid-media decision.

## Guardrails

- Do not replace the standard Meta `Lead` event.
- Do not create fake separate base events for each agency.
- Do not use landing-page PageView or URL-only rules as lead conversions.
- Do not send PII in `cefa_agency_test` or any Meta event parameter.
- Keep USA on dataset `1531247935333023`; do not move the test back to the Canada/parent shared dataset.
- Use exact allowlisted campaign IDs/slugs only for fallback classification; never infer agency ownership from a loose naming substring.
- Do not add a partner marker or switch the partner ad set to the unused partner-only custom conversion unless CEFA later requires partner-only reporting independent of campaign attribution.
- If weekly in-house lead volume is low, consider the broader `USA Franchise Lead` optimization event while keeping campaign IDs as the agency reporting boundary.
