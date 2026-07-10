# Parent Form 4, KinderTales, And Attribution Boundary

Date: 2026-07-10  
Scope: production parent property `cefa.ca` only

## Non-Negotiable System Boundary

The parent and franchise delivery paths are different systems.

| Property | Business form | Business destination | Delivery owner |
|---|---|---|---|
| Parent `cefa.ca` | Gravity Forms Form `4` | KinderTales CRM | `CEFA School Manager` custom plugin |
| Franchise Canada | Gravity Forms Forms `1` and `2` | Synuma/SiteZeus | Franchise control/API integration |
| Franchise USA | Gravity Forms Forms `1` and `2` | Synuma/SiteZeus | Franchise control/API integration |

Never describe Synuma as the parent Form `4` destination. Never apply a franchise CRM assumption to `cefa.ca`.

## Verified Parent Runtime

Production evidence on 2026-07-10:

- Gravity Forms `2.10.5` is active.
- CEFA School Manager `1.0.21` is active.
- CEFA Conversion Tracking `0.6.2` is active.
- Form `4` has active Mailchimp and CEFA Brain webhook feeds.
- The generic Gravity Forms Zoho CRM add-on is active globally but has no Form `4` feed.
- KinderTales delivery is not a generic Gravity Forms feed. It is the custom `gform_after_submission` handler in CEFA School Manager.

## Authoritative Parent Flow

1. CEFA School Manager renders and resolves the custom School Inquiry field.
2. Form `4` submits the parent/child details and School Inquiry field `32`.
3. School Manager enriches the submission before Gravity Forms saves it.
4. Gravity Forms creates the Form `4` entry.
5. School Manager builds the KinderTales payload and posts it to `https://crm-api.kindertales.com/public/crm/inquiries` using its configured client ID.
6. School Manager records a `cefa-sm` success, failure, or skipped note on the entry.
7. CEFA Conversion Tracking builds the confirmed-success tracking payload and exposes `school_inquiry_submit` on the confirmation path.
8. Parent GTM `GTM-NZ6N7WNC` maps that neutral event to GA4, Google Ads, and Meta.
9. The CEFA Brain webhook is an additional data/reconciliation path. It is not the KinderTales delivery owner.

## School And Program Ownership

School Manager owns the business meaning of field `32`:

| Field | Meaning | Owner |
|---|---|---|
| `32.1` | KinderTales school/location UUID | School Manager / KinderTales |
| `32.2` | Selected program ID | School Manager |
| `32.3` | Selected days | School Manager / KinderTales |
| `32.4` | Submission event ID | Shared operational identity; tracking plugin must preserve business behavior |
| `32.5` | School slug | School Manager enrichment |
| `32.6` | School name | School Manager enrichment |
| `32.7` | Program name | School Manager enrichment |

CEFA Conversion Tracking may read these values for measurement. It must not replace school selection, program availability, journey-code resolution, or KinderTales routing.

## Attribution Fields Sent To KinderTales

The live School Manager Form `4` mapping is verified as:

| KinderTales metadata key | Gravity Forms field |
|---|---|
| `utm_source` | `35` |
| `utm_medium` | `36` |
| `utm_campaign` | `37` |
| `utm_term` | `38` |
| `utm_content` | `39` |
| `gclid` | `40` |
| `gbraid` | `41` |
| `wbraid` | `42` |
| `fbclid` | `43` |
| `msclkid` | `44` |
| `first_landing_page` | `45` |
| `first_referrer` | `46` |

School Manager fills missing mapped fields from `cefa_*` cookies before submission. It then reads the saved fields and includes them in KinderTales `metaData`. Therefore, parent attribution is already sent to KinderTales through fields `35–46`.

## What The New Ledger Does

The ledger is an attribution reliability and audit layer. In current `shadow` mode it:

- stores canonical first-touch and last-non-direct evidence in `wp_cefa_ct_attribution_ledger`;
- stores the canonical envelope and opaque capture reference beside the Gravity Forms entry;
- recovers the same capture through an HttpOnly cookie or signed Form `4` fallback;
- compares canonical attribution with the existing fields `35–46`;
- does not change fields `35–46`;
- does not change the KinderTales payload;
- does not change School Manager or the confirmation destination;
- does not create a second GA4, Google Ads, or Meta conversion.

The complete ledger record is not currently sent to KinderTales. KinderTales continues to receive the existing mapped Form `4` fields.

## Current Parity Finding

Four production Form `4` entries created after ledger activation were reviewed:

- `4/4` had canonical attribution;
- `4/4` had unique reserved server event IDs;
- `4/4` had ledger capture references using `shadow_opaque_cookie`;
- `4/4` had successful KinderTales notes;
- `4/4` had successful CEFA Brain webhook notes.

One paid entry showed an intentional diagnostic disagreement:

- existing Form fields: `google_business_profile / local_listing`;
- canonical ledger: `google / cpc`;
- the canonical record contained paid-click evidence while the existing source/medium cookies retained an older UTM classification.

This is evidence that the ledger can improve attribution, but it also means primary writeback must remain disabled until the replacement rule is approved and tested.

## Conversion Integrity

The conversion path remains:

`confirmed Form 4 entry -> school_inquiry_submit -> GTM-NZ6N7WNC -> GA4 generate_lead + Google Ads Inquiry Submit_ollo + Meta Inquiry Submit`

The current public GTM container still contains:

- `school_inquiry_submit`;
- GA4 `generate_lead`;
- Google Ads `AW-802334988/cFt-CMrLufgCEIzSyv4C`;
- Meta dataset `918227085392601`.

No GTM, GA4, Google Ads, Meta, Form `4`, School Manager, KinderTales, or webhook setting was changed by the ledger rollout.

The four post-ledger entries all had server event IDs and no pending one-time confirmation alias when checked. The newest entries were still inside the 30-minute payload lifetime, which confirms that their confirmation browsers retrieved the tracking payload instead of leaving it unconsumed. This verifies the website event handoff layer. Fresh processed GA4/Ads/Meta receipt remains subject to platform reporting delay and authenticated reporting access.

A live-container no-send test then pushed a synthetic `school_inquiry_submit` while intercepting destination transport:

- GA4 generated `generate_lead`;
- Google Ads generated conversion requests for `AW-802334988` with label `cFt-CMrLufgCEIzSyv4C`;
- Meta called `trackCustom` for `Inquiry Submit` on dataset `918227085392601`;
- the Meta call included the shared event ID through its `eventID` deduplication option;
- Google destination requests were aborted, and the Meta function was replaced before invocation, so no synthetic conversion was transmitted.

This proves current website-side tag triggering after the ledger rollout. It does not replace delayed platform reporting confirmation.

## Parent Paid-Click Writeback Policy

Plugin `0.6.2` separates paid-click correction from broad primary mode through `CEFA_CT_PARENT_PAID_CLICK_WRITEBACK_ENABLED`.

When enabled, the adapter:

1. Requires parent context, Form `4`, canonical attribution, and a click type attached to the current last non-direct touch.
2. Supports `gclid`, `gbraid`, `wbraid`, and `msclkid` directly; `fbclid` also requires CEFA campaign metadata or governed Meta platform IDs because it can occur on organic links.
3. Replaces stale source, medium, campaign, term, content, and click-ID fields `35-44`.
4. Clears competing click-ID fields so the saved entry represents one proven paid touch.
5. Writes first landing and first referrer fields `45-46` only when canonical first-touch values exist.
6. Records `cefa_conversion_tracking_writeback_status=parent_paid_click` for audit and rollback verification.
7. Does not change field `32`, event identity, School Manager code, KinderTales routing, or conversion destinations.

Regression coverage includes a `gclid`-only visit after an older local-listing touch, stale campaign clearing, first-touch preservation, historical-click/newer-organic protection, and franchise isolation.

### Live rollout

The parent-only flag is enabled in production while both broad attribution and ledger modes remain `shadow`:

- `CEFA_CT_PARENT_PAID_CLICK_WRITEBACK_ENABLED=1`;
- `CEFA_CT_ATTRIBUTION_V2_MODE=shadow`;
- `CEFA_CT_LEDGER_MODE=shadow`;
- broad `CEFA_CT_CRM_IDENTITY_ENABLED` remains disabled.

Production in-memory QA corrected `google_business_profile / local_listing` to `google / cpc`, cleared the stale campaign and competing `fbclid`, preserved a valid first landing value when canonical first touch was unavailable, and returned writeback status `parent_paid_click`. The QA did not save a Gravity Forms entry or call KinderTales.

Live GTM no-send tests passed both before and after flag enablement for GA4 `generate_lead`, Google Ads `Inquiry Submit_ollo`, and Meta `Inquiry Submit` with `eventID`. Synthetic destination transport was blocked.

No natural Form `4` entry arrived between flag enablement and the immediate post-enable monitor at `2026-07-10T21:43:43Z`. The first natural paid inquiry should therefore be reviewed for `parent_paid_click`, corrected fields `35-44`, KinderTales `SUCCESS`, webhook success, and unchanged event identity.

Immediate rollback is to remove or set `CEFA_CT_PARENT_PAID_CLICK_WRITEBACK_ENABLED` false. This does not require changing attribution mode, ledger mode, School Manager, KinderTales, GTM, GA4, Google Ads, or Meta.

Future work may add `event_id` and `capture_id` to KinderTales metadata only after the KinderTales API contract is confirmed to accept those keys.

## Operational Guardrail

For parent work, use the terms `KinderTales delivery`, `School Manager`, `Form 4`, and `fields 35–46`. Reserve `Synuma/SiteZeus` for franchise Canada and franchise USA work.
