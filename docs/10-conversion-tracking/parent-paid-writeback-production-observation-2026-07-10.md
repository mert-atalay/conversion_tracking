# Parent Paid-Click Writeback Production Observation

Date opened: 2026-07-10  
Property: parent `cefa.ca`  
Form and CRM: Gravity Forms Form `4` -> CEFA School Manager -> KinderTales  
Status: live, production acceptance passed on 2026-07-13

## Live Configuration

| Control | Production value |
|---|---|
| CEFA Conversion Tracking | `0.6.2` |
| `CEFA_CT_PARENT_PAID_CLICK_WRITEBACK_ENABLED` | enabled |
| `CEFA_CT_ATTRIBUTION_V2_MODE` | `shadow` |
| `CEFA_CT_LEDGER_MODE` | `shadow` |
| Broad `CEFA_CT_CRM_IDENTITY_ENABLED` | disabled |

Only the parent paid-click adapter was enabled. Broad attribution writeback remains disabled, and franchise Canada/USA are outside this rollout.

## Test Status At Activation

Completed on 2026-07-10:

- PHP `7.4` and `8.2` CI passed.
- Attribution, payload, identity, ledger, parity, and browser regression tests passed.
- Production in-memory QA corrected stale `google_business_profile / local_listing` fields to canonical `google / cpc`.
- The same QA cleared stale campaign data and a competing click ID, preserved valid first-touch data, and returned `parent_paid_click`.
- The in-memory QA did not save a Gravity Forms entry and did not call KinderTales.
- Live-container no-send tests passed before and after activation for GA4 `generate_lead`, Google Ads `Inquiry Submit_ollo`, and Meta `Inquiry Submit` with `eventID`.
- Synthetic destination traffic was intercepted, so the tests did not create platform conversions.
- The immediate production monitor ran at `2026-07-10T21:43:43Z` and found no natural post-activation Form `4` entry to inspect.

Release checksum:

`898b132a177e440a19c98b818cc1bcb675d3755e58ead8b9a1e865b00b16f89c`

## Follow-Up Window

Run the first follow-up on 2026-07-13 or 2026-07-14. If no natural paid Form `4` inquiry exists, keep the feature enabled and repeat after the next paid inquiry arrives. Do not submit a synthetic production lead solely to satisfy this checkpoint.

Run the existing read-only, aggregate-only monitor on the parent WP Engine environment:

```bash
wp eval-file tools/wp-shadow-parity-report.php 4 '2026-07-10 21:35:00' 500
```

The report must not expose names, email addresses, phone numbers, raw click IDs, or raw attribution values.

## Acceptance Checklist

For the first natural paid inquiry after activation, confirm:

- `writeback_statuses.parent_paid_click` increases by at least one.
- The entry has a ledger capture reference and a successful ledger status.
- The saved source and medium match the canonical current paid touch.
- Exactly one applicable current click-ID family is retained; stale competing IDs are cleared.
- First landing page and first referrer remain valid.
- The server event ID exists and remains unique.
- The entry has a KinderTales `SUCCESS` note.
- The CEFA Brain webhook remains successful.
- The confirmation path still dispatches the existing neutral `school_inquiry_submit` event.
- Normal delayed reporting shows the lead in the expected GA4, Google Ads, and/or Meta destination according to its actual traffic source.

Safari/iOS is an important observation segment. Confirm that its entry receives a ledger capture reference through the opaque cookie or signed Form `4` fallback; do not require a particular browser to generate the first paid lead.

## Decision Rule

**Pass:** Keep the adapter enabled when paid attribution is corrected, KinderTales and webhook delivery succeed, event identity remains unique, and conversion dispatch is unchanged.

**Hold and investigate:** Keep the feature narrowly enabled while investigating if attribution is missing but business delivery and conversions remain healthy. Compare the canonical last non-direct touch, ledger recovery status, and browser type without modifying the entry.

**Rollback:** Remove or disable only `CEFA_CT_PARENT_PAID_CLICK_WRITEBACK_ENABLED` if the adapter writes a demonstrably incorrect paid touch, changes business fields, or correlates with a KinderTales/conversion regression. Do not disable the shadow ledger or alter GTM, GA4, Google Ads, Meta, School Manager, or KinderTales as part of this rollback.

## Follow-Up Record

Append the dated aggregate result here after each review:

| Review date | Natural paid entries | `parent_paid_click` | Ledger coverage | KinderTales success | Webhook success | Decision |
|---|---:|---:|---:|---:|---:|---|
| 2026-07-10 | 0 observed immediately after enablement | 0 observed | Not yet assessable | Not yet assessable | Not yet assessable | Await natural paid inquiry |
| 2026-07-13 | 44 paid-classified; 40 eligible paid clicks | 40 | 227/234 overall; 40/40 writebacks | 234/234 | 233/234 | Pass; keep adapter enabled |

## 2026-07-13 Production Review

The read-only follow-up covered 234 natural Form `4` submissions created after the `2026-07-10T21:35:00Z` activation boundary.

- All 234 submissions had server event IDs, and all 234 IDs were unique.
- 228 submissions had canonical attribution; five were expected direct submissions and one had legacy attribution without a canonical envelope.
- 40 entries received `parent_paid_click`; all 40 had ledger references.
- The corrected cohort included 32 iOS, six Android, one desktop Chrome, and one Safari submission.
- Policy-aware validation matched all 479 checked fields across the 40 writebacks, for `100%` writeback-policy parity.
- Four paid-classified entries correctly received no writeback: three had no current click-ID type and one had an `fbclid` without the governed paid context required by the Meta guardrail.
- KinderTales delivery succeeded for all 234 submissions.
- The CEFA Brain webhook succeeded for 233 submissions and failed for one. The failed webhook entry had a ledger reference and no paid-click writeback, so there is no evidence connecting that failure to the adapter.
- Public homepage and Form `4` paths continued to serve CEFA Conversion Tracking `0.6.2`.

The generic parity report showed `96.58%` core paid parity because its historical comparison expects retained click IDs that the approved adapter deliberately clears. The policy-aware check applies the actual production rule: retain only the current click family and clear competing stale IDs. That check passed at `100%`.

Overall ledger coverage was `227/234` (`97.01%`). The seven entries without a ledger reference comprised five iOS, one Safari, and one Chrome submission; six also lacked canonical attribution, while one retained canonical attribution through the existing browser path. This is a separate reliability follow-up, not a paid-writeback failure: all 40 paid writebacks, including the iOS/Safari cohort, had ledger references.

Decision: keep `CEFA_CT_PARENT_PAID_CLICK_WRITEBACK_ENABLED` enabled. Keep broad attribution and ledger modes in `shadow`. Investigate the isolated Brain webhook failure and continue improving Safari/iOS ledger recovery without changing School Manager, KinderTales, Form `4`, or conversion destinations.

Recommended next observation: rerun the aggregate report on or after 2026-07-16, or after another 100 Form `4` submissions, whichever comes first. Confirm that writeback-policy parity remains `100%`, KinderTales remains at `100%`, ledger coverage trends upward, and webhook failures do not repeat.

Architecture and ownership details remain canonical in [Parent Form 4, KinderTales, and attribution boundary](./parent-form4-kindertales-attribution-boundary-2026-07-10.md).
