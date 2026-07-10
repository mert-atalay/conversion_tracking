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
- CEFA Conversion Tracking `0.6.1` is active.
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

## Safe Next Step

Do not enable canonical CRM compatibility writeback yet. The current primary adapter can replace all approved fields, including intentional blanks.

Before any promotion:

1. Define the exact last-non-direct rule for `gclid`, `gbraid`, `wbraid`, `fbclid`, and explicit UTMs.
2. Decide whether canonical values should fill only missing fields or replace stale existing values.
3. Add regression tests for `gclid`-only visits after an older organic/local touch.
4. Confirm the resulting fields still appear correctly in the KinderTales inquiry record.
5. Add `event_id` and `capture_id` to KinderTales metadata only after the KinderTales API contract is confirmed to accept those keys.
6. Keep one final conversion event and preserve the existing event ID for future browser/server deduplication.

## Operational Guardrail

For parent work, use the terms `KinderTales delivery`, `School Manager`, `Form 4`, and `fields 35–46`. Reserve `Synuma/SiteZeus` for franchise Canada and franchise USA work.
