# Conversion Tracking Remediation Execution Log

Last updated: 2026-07-09

Blueprint: [CEFA conversion tracking remediation blueprint](./cefa-conversion-tracking-remediation-blueprint-2026-07-09.md)

## Current Situation

| Area | Current state |
|---|---|
| Parent regional PMax | Existing BC, Ontario, and Alberta inquiry-only campaign goals remain unchanged. |
| Parent Search goals | Branded and Oakville Eighth Line now use only `SUBMIT_LEAD_FORM / WEBSITE` as biddable campaign goals. |
| Google URL parameter pilot | Live on branded Search campaign `14995905347` only. The campaign overrides the legacy account template with `{lpurl}` and uses the canonical final URL suffix. |
| Parent GA4 key events | `generate_lead` remains; inquiry/email/phone/school-finder clicks are ordinary events. GA4's non-deletable `purchase` key event remains. |
| Franchise Canada GA4 key events | `generate_lead` remains; application/email/phone clicks are ordinary events. GA4's non-deletable `purchase` key event remains. |
| Franchise USA GA4 key events | Unchanged pending lifecycle dependency review. |
| Franchise USA Google Ads | Repaired. Existing `Application Submit (USA)` action now fires from confirmed Form `1` only. |
| Franchise USA Meta in-house | Working. Both active ad sets still optimize to the marker-filtered in-house custom conversion. |
| Franchise USA Meta partner | Unchanged. Reshift still optimizes to broad `USA Franchise Lead`; no partner marker was added. |
| Agency carryover | Repaired. Exact Reshift traffic clears stale in-house state without creating a partner marker. |
| Franchise USA GA4/Meta form events | Existing active tags and triggers remain unchanged. |
| Meta raw browser Lead anomaly | Resolved as an API aggregation/query-semantics artifact. Correct event-filtered stats show normal browser/server pairs. |
| Consent/CMP | Deferred by owner decision and outside this execution scope. |
| Attribution Bridge V1 | Parent signed-envelope and entry-meta shadow foundation implemented and tested in the PR. Production remains `off`; CRM propagation and shadow rollout are not yet implemented. |
| Server event identity | Guarded dual-mode registry implemented in the PR. Shadow keeps the current platform ID and reserves a separate server UUID; primary promotes only a reserved UUID. Not deployed. |
| Franchise replacement adapter | Existing fields `14-30` can be populated from canonical CEFA attribution only when both primary mode and the CRM identity flag are enabled. Default is disabled. |
| Confirmation payload V2 | Signed, 30-minute, replay-safe payload retrieval implemented behind a separate disabled flag. |
| Shadow parity evidence | No-PII per-entry match/missing/mismatch summaries implemented for parent and franchise field maps. |
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

### Parent Google Ads Search goal isolation

Validated through Google Ads API `validateOnly=true`, then applied and read back:

- campaign `14995905347` / branded Search;
- campaign `23854771600` / Oakville Eighth Line Search.

For both campaigns:

- `SUBMIT_LEAD_FORM / WEBSITE` remains biddable;
- `PURCHASE / WEBSITE` is not biddable;
- `DOWNLOAD / APP` is not biddable;
- `GET_DIRECTIONS / WEBSITE` is not biddable;
- `ENGAGEMENT / YOUTUBE_HOSTED` is not biddable;
- `YOUTUBE_FOLLOW_ON_VIEWS / YOUTUBE_HOSTED` is not biddable.

Read-back confirmed campaign status, budgets, bidding strategies, ads, keywords, and targeting were not changed.

### GA4 key-event cleanup

Removed key-event status only from confirmed micro actions:

Parent property `267558140`:

- `inquiry_click`;
- `email_click`;
- `phone_click`;
- `find_a_school_click`.

Franchise Canada property `259747921`:

- `fr_application_click`;
- `fr_phone_click`;
- `fr_email_click`.

Read-back state:

- Parent key events: `purchase`, `generate_lead`.
- Franchise Canada key events: `purchase`, `generate_lead`.
- Franchise USA key events were not changed.

### Google Ads URL parameter pilot

Validated through Google Ads API `validateOnly=true`, then applied and read back on one campaign only:

- account: `4159217891`;
- campaign: `14995905347` / `corp | search | branded | cefa | always on`;
- campaign tracking template: `{lpurl}`;
- campaign final URL suffix:

```text
utm_source=google&utm_medium=cpc&utm_campaign={campaignid}&utm_id={campaignid}&utm_content={creative}&utm_term={keyword}&google_adgroup_id={adgroupid}&google_network={network}&google_device={device}&google_matchtype={matchtype}
```

Reason for the campaign-level pilot:

- the account still has the legacy tracking template `{lpurl}?utm_source=google&utm_medium=cpc&utm_campaign={campaignid}&utm_content={creative}&utm_term={keyword}`;
- many active school Search ads have ad-level final URL suffixes, so an account-wide suffix would create an unsafe mixed hierarchy until those overrides are mapped and removed;
- the branded campaign has one enabled ad, no ad-level URL options, and a single homepage final URL.

Read-back confirmed that status, `20 CAD/day` budget, target impression share bidding, ad group, ad status, and `https://cefa.ca/` final URL did not change. Auto-tagging remains enabled at the account level. No PMax or school campaign URL option changed.

### Attribution Bridge signed-envelope foundation

Implemented in source control only; not deployed to WordPress:

- hostname-scoped `CEFA_CT_ATTRIBUTION_V2_MODE` with fail-closed `off`, `shadow`, and `primary` values;
- production default remains `off`;
- server-only `CEFA_CT_ATTRIBUTION_SECRET` requirement;
- host-only cookie namespaces for parent, Franchise Canada, and Franchise USA;
- allowlisted query capture with bounded values and no arbitrary form/query data;
- exact CEFA internal-referrer exclusions;
- first-touch and last-non-direct behavior that ignores direct/internal navigation;
- canonical click-ID and platform-ID objects;
- newest Google click-ID family replacement;
- approved in-house experiment marker normalization without a partner marker;
- HMAC signing, tamper rejection, site-context rejection, expiry rejection, eight-touch cap, and cookie-size budget;
- `Secure`, `HttpOnly`, `SameSite=Lax`, path `/`, host-only cookie settings when eventually enabled.

Live WordPress remains on plugin `0.4.5`. Source control now contains a guarded `0.5.0` release candidate; no WordPress deployment has been made.

### Parent CEFA-owned attribution entry metadata

Implemented in source control only; not deployed to WordPress:

- verified signed attribution is saved to `cefa_conversion_tracking_attribution_v1` entry meta in `shadow` or `primary` mode;
- schema, delivery status, and provenance are saved in separate bounded meta keys;
- repeated after-submission and confirmation hooks are idempotent;
- `shadow` mode does not write or overwrite Gravity Forms fields;
- parent fields `35-46`, School Manager field `32`, event names, confirmation destinations, and CRM feed inputs remain unchanged;
- `_ga`, GA4 session, `_fbp`, and `_fbc` cookies are parsed server-side into an allowlisted `browser_ids` object;
- arbitrary cookies and query parameters are not retained;
- the parent browser script now uses exact approved CEFA hosts and no longer classifies internal CEFA navigation as referral traffic.

Automated tests cover metadata persistence, off-mode no-write behavior, idempotency, legacy-field preservation, GA client/session parsing, Meta browser-ID parsing, exact-host exclusions, internal-navigation behavior, and Google organic classification.

### CEFA-owned script versus current GAConnector contract

| Capability | Live parent `0.4.5` | `0.5.0` release candidate | Current franchise GAConnector fields `14-30` |
|---|---|---|---|
| Source/medium/campaign/content/term | Saved as parent last-touch fields | Signed first and last non-direct entry meta | Saved as first/last-click fields |
| Landing/referrer | First landing/referrer saved | Normalized host/path for first, current, last, and history | First/last landing and referrer fields |
| Google click IDs | `gclid`, `gbraid`, `wbraid` fields | Same plus signed canonical storage | Current mapped field exposes `gclid` |
| Meta/Microsoft click IDs | `fbclid`, `msclkid` fields | Same plus signed canonical storage | Not present in the current mapped fields |
| GA client ID | Not saved on parent Form 4 | Parsed server-side into entry meta | Saved in field `30` |
| GA session ID | Not saved | Parsed server-side into entry meta | Not present in the current mapped fields |
| `_fbp` / `_fbc` | Not saved | Parsed server-side into entry meta | Not present in the current mapped fields |
| Multi-touch history | Browser-only, up to eight touches | Signed and saved with the entry | First/last-click fields, not an eight-touch saved history |
| Direct/internal protection | Internal-referrer defect in live script | Exact-host defect fixed and tested | Dependent on GAConnector classification |
| Tamper protection | Browser cookies/local storage | HMAC-signed, host-scoped envelope | No CEFA-controlled signature contract |
| CRM availability | Legacy parent fields are available | Canonical entry meta is not yet mapped into CRM | Existing hidden fields are available to current form/feed paths |
| Final server event identity | Existing event ID flow is only partially server-enforced | Still pending unique reservation/cutover | Not supplied by GAConnector |

Decision:

- The remediation branch now captures a richer attribution dataset than the current GAConnector field map.
- It does **not** yet match GAConnector operationally because the canonical entry metadata is not mapped into CRM and the final server event-ID contract is incomplete.
- Do not remove GAConnector or retire parent fields `35-46` until a production shadow comparison reaches the documented parity gates.

### Server identity and replacement adapters

Implemented in source control only; not deployed:

- plugin-owned event-ID registry with a unique primary key;
- 10,000 generated/reserved UUID contract test with zero duplicates;
- `shadow` mode preserves the current platform event ID and stores a separate reserved server UUID plus browser submission-attempt ID;
- `primary` mode replaces the operational event ID only after atomic reservation;
- repeated confirmation handling reuses the saved server identity;
- existing parent fields `35-46` and franchise fields `14-30` have canonical compatibility adapters;
- compatibility writing requires both `CEFA_CT_ATTRIBUTION_V2_MODE=primary` and `CEFA_CT_CRM_IDENTITY_ENABLED=true`;
- shadow and disabled modes cannot overwrite the existing fields;
- current CRM routing, destination feeds, and GAConnector remain unchanged.

### Signed replay-safe confirmation payload

Implemented behind `CEFA_CT_PAYLOAD_V2_ENABLED` and a separate server-only signing secret:

- signed token contains only event ID, site context, expiry, and random nonce;
- payload remains readable more than once for 30 minutes;
- tampered, expired, or wrong-context tokens are rejected;
- legacy one-time behavior remains the default until V2 is enabled;
- REST responses remain `Cache-Control: no-store`.

### Shadow parity evidence

For each supported saved entry in shadow mode, the plugin can now store:

- checked and matched field counts;
- parity rate;
- mismatch semantic keys;
- legacy-missing semantic keys;
- canonical-missing semantic keys.

The parity record stores no raw attribution values, URLs, click IDs, browser IDs, or PII. It supports both parent fields `35-46` and franchise fields `14-30`.

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

### Google URL parameter pilot QA

Synthetic ValueTrack rendering was tested against the live homepage for desktop/mobile-compatible query behavior:

- `gclid`, `gbraid`, and `wbraid` were tested separately;
- every request returned HTTP `200` with zero redirects;
- every click ID remained unchanged in the effective URL;
- a URL with an existing query parameter returned HTTP `200` with zero redirects and correct `&` separators;
- each canonical UTM key appeared once.

This proves the landing URL and parameter syntax. It does not claim a served-ad click or Google Ads attribution receipt.

## Explicitly Unchanged

- Meta campaign, ad-set, ad, creative, budget, targeting, status, and promoted objects;
- Google Ads campaign budget, bidding strategy, targeting, status, final URLs, and conversion actions; only the branded Search campaign URL options changed as documented above;
- all three parent regional PMax campaigns, including current budgets: BC `80 CAD/day`, Ontario `60 CAD/day`, Alberta `60 CAD/day`;
- Franchise USA GA4 and Meta final-submit tags;
- Form `2` destination behavior;
- WordPress form fields and CRM routing;
- legacy Google Ads tag `218`, which remains paused;
- consent/CMP configuration.

## Remaining Priority Order

1. Confirm delayed Google Ads action receipt/status without expecting campaign attribution from the QA test.
2. Merge reviewed GitHub PR `#3`; the `0.5.0` release candidate and CI are ready.
3. Export live Gravity Forms and destination feed maps before changing WordPress.
4. Deploy parent shadow mode with server secrets and compare it beside fields `35-46`.
5. Observe at least 98% paid-entry parity and 100% reserved server-ID uniqueness without routing regressions.
6. Deploy franchise shadow mode beside GAConnector fields `14-30`, one property at a time.
7. Enable signed confirmation payload V2 only after browser prefetch/replay QA.
8. Create approved CRM destination fields and map event/form identity without changing routing.
9. Complete the Google URL-option cleanup, warehouse reconciliation, and lifecycle propagation.

## Rollback

- Google Ads tag repair rollback: publish GTM Version `22` or pause tag `275` in a one-change version.
- Value-only rollback: publish Version `23` only if the action value contract is intentionally changed away from `600 CAD`.
- Agency clearing rollback: publish Version `24` to restore the prior writer.
- Google URL pilot rollback: clear `tracking_url_template` and `final_url_suffix` on campaign `14995905347` in a validated two-field campaign mutate. The unchanged account tracking template will resume inheritance.

Do not roll back to Version `22` merely to undo agency clearing, because that would also remove the repaired Google Ads Form `1` conversion tag.
