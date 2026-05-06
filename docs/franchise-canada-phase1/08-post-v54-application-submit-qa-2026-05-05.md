# Franchise Canada Post-Version-54 Application Submit QA

Date: 2026-05-05

Property: `franchise.cefa.ca`

GTM container: `GTM-TPJGHFS`

Published GTM version tested: `54` / `CEFA Franchise Canada legacy thank-you duplicate guard - 2026-05-05`

## Purpose

This QA validates the 2026-05-05 continuity correction for Canada franchise Form `1`.

The website/dataLayer event remains the neutral helper event:

- `franchise_inquiry_submit`

The destination mapping now preserves the existing optimized platform paths:

- Google Ads primary action: `fr_application_submit`
- Google Ads label: `AW-11088792613/cys-CIHslY4YEKWYxqcp`
- Meta event: `Fr Application Submit`
- Meta dataset/pixel: `918227085392601`
- Meta custom conversion continuity path: `Fr Application Submit_CAD`
- GA4 event: `generate_lead`
- GA4 measurement ID: `G-6EMKPZD7RD`

## Controlled Submission

Test path:

`https://franchise.cefa.ca/available-opportunities/franchising-inquiry/?utm_source=qa_tracking&utm_medium=post_v54&utm_campaign=frca_application_submit_continuity&gclid=QA-FRCA-V54-20260505`

Final thank-you URL:

`https://franchise.cefa.ca/inquiry-thank-you/?location=brampton-on&inquiry=true&cefa_tracking=1&cefa_tracking_event_id=ad5901f8-0dbb-4281-97cc-88dd0c2d86d3`

Location selected:

- `Brampton, ON`

Event ID:

- `ad5901f8-0dbb-4281-97cc-88dd0c2d86d3`

## DataLayer Evidence

Verified in the browser:

- One raw `franchise_inquiry_submit` event was pushed.
- One dispatch `cefa_franchise_inquiry_dispatch` event was pushed.
- Both events used event ID `ad5901f8-0dbb-4281-97cc-88dd0c2d86d3`.
- The helper payload included:
  - `form_id: "1"`
  - `form_family: "franchise_inquiry"`
  - `site_context: "franchise_ca"`
  - `business_unit: "franchise"`
  - `market: "canada"`
  - `lead_type: "franchise_lead"`
  - `tracking_source: "helper_plugin"`
  - `location_interest: "565"`
  - `location_interest_name: "Brampton, ON"`
  - `gclid: "QA-FRCA-V54-20260505"`
  - `ga_client_id: "388062971.1778050811"`
  - `lc_source: "qa_tracking"`
  - `lc_medium: "post_v54"`
  - `lc_campaign: "frca_application_submit_continuity"`
  - `fc_source: "qa_tracking"`
  - `fc_medium: "post_v54"`
  - `fc_campaign: "frca_application_submit_continuity"`

## Destination Evidence

Browser/network proof:

- Google Ads final conversion request fired for conversion ID `11088792613` and label `cys-CIHslY4YEKWYxqcp`.
- GA4/Google measurement fired `generate_lead` to `G-6EMKPZD7RD`.
- No `MfYYCITslY4YEKWYxqcp` request was observed, so the secondary `fr_inquiry_submit` Ads label did not fire.
- The GTM-injected Meta helper script executed `fbq("trackCustom", "Fr Application Submit", { value: 550, currency: "CAD" }, { eventID: "ad5901f8-0dbb-4281-97cc-88dd0c2d86d3" })`.

Meta caveat:

- Browser execution of the Meta call is verified.
- Events Manager receipt for this exact post-v54 event still needs UI confirmation because the browser request log did not expose a clear `/tr` request in this test environment.

## Result

Status: partial pass.

Pass:

- Neutral helper event preserved.
- Final Form `1` submit maps to existing Google Ads primary `fr_application_submit`.
- Secondary Google Ads `fr_inquiry_submit` label did not fire.
- GA4 `generate_lead` fired.
- Meta `Fr Application Submit` browser call executed.

Remaining:

- Confirm Meta Events Manager receipt for `Fr Application Submit` after platform processing delay.
- Confirm processed GA4 and Google Ads reporting rows after standard processing delay.
