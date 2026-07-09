# Conversion Tracking Remediation Execution Log

Last updated: 2026-07-09

Blueprint: [CEFA conversion tracking remediation blueprint](./cefa-conversion-tracking-remediation-blueprint-2026-07-09.md)

## Current Situation

| Area | Current state |
|---|---|
| Parent regional PMax | Existing BC, Ontario, and Alberta inquiry-only campaign goals remain unchanged. |
| Franchise USA Google Ads | Repaired. Existing `Application Submit (USA)` action now fires from confirmed Form `1` only. |
| Franchise USA Meta in-house | Working. Both active ad sets still optimize to the marker-filtered in-house custom conversion. |
| Franchise USA Meta partner | Unchanged. Reshift still optimizes to broad `USA Franchise Lead`; no partner marker was added. |
| Agency carryover | Repaired. Exact Reshift traffic clears stale in-house state without creating a partner marker. |
| Franchise USA GA4/Meta form events | Existing active tags and triggers remain unchanged. |
| Meta raw browser Lead anomaly | Resolved as an API aggregation/query-semantics artifact. Correct event-filtered stats show normal browser/server pairs. |
| Consent/CMP | Deferred by owner decision and outside this execution scope. |
| Attribution Bridge V1 | Blueprint complete; runtime build and shadow rollout not started. |
| CRM event-ID lineage | Not yet implemented. |
| Warehouse reconciliation repairs | Not yet implemented. |

## Implemented Live Changes

### GTM Version 23

Name: `2026-07-09 - Franchise USA Google Ads confirmed inquiry repair`

Change:

- added tag `275` / `CEFA - Google Ads - Franchise USA - Application Submit - Confirmed Form 1`;
- existing conversion ID/label `AW-11088792613/fnFOCLKk6-8bEKWYxqcp`;
- existing trigger `260` / `cefa_franchise_us_inquiry_dispatch` only;
- `{{DLV - cefa - event_id}}` as Google transaction ID;
- enhanced conversions disabled;
- legacy tag `218` left paused;
- zero existing tags, triggers, or variables changed.

### GTM Version 24

Name: `2026-07-09 - Franchise USA Google Ads value continuity`

Reason:

- no-send browser QA showed that an omitted GTM conversion value transmitted `value=0`;
- the existing Google Ads action is configured for `600 CAD`.

Change:

- updated tag `275` only;
- added explicit `conversionValue=600` and `currencyCode=CAD`;
- no trigger, variable, destination, or legacy tag changes.

### GTM Version 25

Name: `2026-07-09 - Franchise USA stale in-house marker clearing`

Change:

- updated tag `272` only;
- in-house marker lifetime changed from 90 days to 7 days;
- exact partner campaign `120244631021580488`, ad set `120244631021560488`, and slug `reshift_meta` clear stale in-house state;
- clearing stores no `fr_us_partner` value;
- unknown/direct traffic does not erase valid in-house state.

## QA Evidence

### Google Ads no-send QA

The platform endpoints were successfully stubbed so no conversion was transmitted.

- Form `1` inquiry dispatch produced one Google conversion tag invocation.
- Label: `fnFOCLKk6-8bEKWYxqcp`.
- Transaction ID matched the QA event ID.
- Value/currency: `600 CAD` after Version `24`.
- Form `2` site dispatch produced zero requests to this action.

### Controlled real Form 1 QA

- success path: `/inquiry-thank-you/`;
- event ID: `c1a582b5-642e-4db3-bf95-0a5e925db784`;
- exact Google action label observed;
- transaction ID matched the server event ID;
- value/currency: `600 CAD`;
- the test used explicit QA UTMs and no served-ad click ID;
- campaign attribution is not expected and is not claimed.

Google emitted its normal conversion, consent-mode, view-through, and first-party transport requests around the single tag invocation. The primary conversion request carried the transaction ID.

### Agency clearing QA

Candidate tests passed:

- explicit in-house marker;
- in-house campaign ID fallback;
- in-house campaign slug fallback;
- partner campaign ID clearing;
- partner ad-set ID clearing;
- partner slug clearing;
- explicit partner clearing;
- direct-return preservation;
- unknown-campaign preservation;
- partner precedence over stale in-house landing evidence.

Live browser checks after Version `25` confirmed:

- in-house campaign evidence writes `fr_us_in_house` with a seven-day expiry;
- `utm_campaign=reshift_meta` clears stale in-house state;
- partner ad-set ID `120244631021560488` clears stale in-house state;
- a direct return preserves valid in-house state.

### Meta Lead stats investigation

The original audit used the Pixel stats endpoint with unfiltered `aggregation=event`. That response reported `1,086` apparent Lead counts from 2026-07-01 through 2026-07-09, including bursts of `200`, `199`, `78`, `199`, and `400`.

The correct event-specific query is:

```text
aggregation=event_source&event=Lead
```

With full pagination, the same period contains:

- browser Lead events: `7`;
- server Lead events: `6`;
- six normal browser/server pairs;
- one browser-only event on 2026-07-01.

Decision:

- do not disable the USA Meta browser tag or CAPI path;
- do not use unfiltered `aggregation=event` counts as Lead truth;
- monitor Meta Lead transport with an explicit `event=Lead` filter and full pagination;
- retain form/CRM truth as the business lead count.

## Explicitly Unchanged

- Meta campaign, ad-set, ad, creative, budget, targeting, status, and promoted objects;
- Google Ads campaign, budget, bidding strategy, targeting, status, URLs, and conversion action;
- all three parent regional PMax campaigns;
- Franchise USA GA4 and Meta final-submit tags;
- Form `2` destination behavior;
- WordPress form fields and CRM routing;
- legacy Google Ads tag `218`, which remains paused;
- consent/CMP configuration.

## Remaining Priority Order

1. Confirm delayed Google Ads action receipt/status without expecting campaign attribution from the QA test.
2. Establish a clean reviewed production-state source commit and redacted GTM/form manifests.
3. Clean GA4 key-event definitions and isolate the two parent Search campaign goals in separate change windows.
4. Standardize Google Ads URL suffixes through a limited pilot.
5. Build and test Attribution Bridge V1 behind feature flags.
6. Shadow the bridge beside GAConnector.
7. Carry event IDs into CRM and repair warehouse reconciliation.

## Rollback

- Google Ads tag repair rollback: publish GTM Version `22` or pause tag `275` in a one-change version.
- Value-only rollback: publish Version `23` only if the action value contract is intentionally changed away from `600 CAD`.
- Agency clearing rollback: publish Version `24` to restore the prior writer.

Do not roll back to Version `22` merely to undo agency clearing, because that would also remove the repaired Google Ads Form `1` conversion tag.
