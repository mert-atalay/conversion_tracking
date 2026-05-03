# Local Listing UTM Rules - GBP and Yelp

Last updated: 2026-05-03

## Purpose

Capture the CEFA parent-school local listing UTM convention for Google Business Profile and Yelp so it can be used consistently in GA4, BigQuery, Looker Studio, Sheets, and CRM exports.

This is a naming-convention workstream document. It does not define conversion events, GTM triggers, BigQuery marts, SEO page copy, or platform launch status.

## Scope

| Field | Value |
|---|---|
| Workstream | Naming convention |
| Property / platform | Parent school local listings, Google Business Profile, Yelp |
| Owner / agent | Naming convention agent |
| Live writes made | No |

## Current Verified Status

- `Verified`: This repo is the shared working surface for CEFA measurement/tracking docs on branch `codex/franchise-canada-tracking-plan`.
- `Verified`: Governance routes UTM naming and Meta naming to `docs/40-naming-convention/`.
- `Verified`: These rules are intentionally separate from Meta NC1 ad naming. Do not use Meta tokens such as `LSM`, `FRANCH`, `META`, `TOF`, `BOF`, `IMG`, `VID`, or `CAR` in GBP/Yelp UTMs.
- `Partial`: `{school_slug}` should use the canonical CEFA school page slug. This document gives the rule and examples, but it does not contain the full school slug crosswalk.
- `Pending`: Confirm which GBP and Yelp fields support direct inquiry-form links for every location before bulk updating live listings.

## Canonical Tokens

| Token | Value | Status |
|---|---|---|
| Local listing UTM version | `ll1` | Verified |
| GBP source | `google_business_profile` | Verified |
| Yelp source | `yelp` | Verified |
| GBP short token | `gbp` | Verified |
| Yelp short token | `yelp` | Verified |
| UTM medium | `local_listing` | Verified |
| Website campaign | `parents_school_location` | Verified |
| Inquiry campaign | `parents_school_inquiry` | Verified |
| School slug | `{school_slug}` | Partial |

Example school page:

```text
https://cefa.ca/cefa-find-a-school/burlington-south-service-road/
```

Example school slug:

```text
burlington-south-service-road
```

## Website Link Rule

Use this for the main GBP/Yelp website link for a school location.

```text
utm_source={platform}
utm_medium=local_listing
utm_campaign=parents_school_location
utm_content={school_slug}__website
utm_id=ll1__{platform_short}__{school_slug}
```

### Google Business Profile Website Link

```text
https://cefa.ca/cefa-find-a-school/{school_slug}/?utm_source=google_business_profile&utm_medium=local_listing&utm_campaign=parents_school_location&utm_content={school_slug}__website&utm_id=ll1__gbp__{school_slug}
```

Example:

```text
https://cefa.ca/cefa-find-a-school/burlington-south-service-road/?utm_source=google_business_profile&utm_medium=local_listing&utm_campaign=parents_school_location&utm_content=burlington-south-service-road__website&utm_id=ll1__gbp__burlington-south-service-road
```

### Yelp Website Link

```text
https://cefa.ca/cefa-find-a-school/{school_slug}/?utm_source=yelp&utm_medium=local_listing&utm_campaign=parents_school_location&utm_content={school_slug}__website&utm_id=ll1__yelp__{school_slug}
```

Example:

```text
https://cefa.ca/cefa-find-a-school/burlington-south-service-road/?utm_source=yelp&utm_medium=local_listing&utm_campaign=parents_school_location&utm_content=burlington-south-service-road__website&utm_id=ll1__yelp__burlington-south-service-road
```

## Inquiry Form Link Rule

Use this for local listing links intended to drive a parent inquiry form submission.

```text
utm_source={platform}
utm_medium=local_listing
utm_campaign=parents_school_inquiry
utm_content={school_slug}__inquiry_form
utm_id=ll1__{platform_short}__{school_slug}__inquiry
```

### Google Business Profile Inquiry Form Link

```text
https://cefa.ca/cefa-find-a-school/{school_slug}/?utm_source=google_business_profile&utm_medium=local_listing&utm_campaign=parents_school_inquiry&utm_content={school_slug}__inquiry_form&utm_id=ll1__gbp__{school_slug}__inquiry
```

Example:

```text
https://cefa.ca/cefa-find-a-school/burlington-south-service-road/?utm_source=google_business_profile&utm_medium=local_listing&utm_campaign=parents_school_inquiry&utm_content=burlington-south-service-road__inquiry_form&utm_id=ll1__gbp__burlington-south-service-road__inquiry
```

### Yelp Inquiry Form Link

```text
https://cefa.ca/cefa-find-a-school/{school_slug}/?utm_source=yelp&utm_medium=local_listing&utm_campaign=parents_school_inquiry&utm_content={school_slug}__inquiry_form&utm_id=ll1__yelp__{school_slug}__inquiry
```

Example:

```text
https://cefa.ca/cefa-find-a-school/burlington-south-service-road/?utm_source=yelp&utm_medium=local_listing&utm_campaign=parents_school_inquiry&utm_content=burlington-south-service-road__inquiry_form&utm_id=ll1__yelp__burlington-south-service-road__inquiry
```

## Optional Internal Form Label

If a hidden form field, GA4 event parameter, CRM handoff, or QA sheet needs a compact source label, use:

```text
parent_inquiry__{school_slug}__{platform_short}
```

Examples:

```text
parent_inquiry__burlington-south-service-road__gbp
parent_inquiry__burlington-south-service-road__yelp
```

## Rules

- Use lowercase UTM values.
- Use hyphens inside `{school_slug}`.
- Use double underscores only inside `utm_content`, `utm_id`, and optional internal labels.
- Keep `utm_campaign` stable across all schools.
- Put school-specific values in `utm_content` and `utm_id`, not in `utm_campaign`.
- Do not use paid-media funnel, audience, format, activation, or Meta platform tokens in local listing UTMs.
- Do not change `ll1` unless the local-listing UTM schema changes. If it changes, propose `ll2`.

## Reporting Interpretation

| Field | Meaning |
|---|---|
| `utm_source=google_business_profile` | Google Business Profile listing traffic |
| `utm_source=yelp` | Yelp listing traffic |
| `utm_medium=local_listing` | Unpaid local directory/listing traffic |
| `utm_campaign=parents_school_location` | General parent school-location link |
| `utm_campaign=parents_school_inquiry` | Parent inquiry-intent link |
| `utm_content` | School slug plus link type |
| `utm_id` | Stable machine key for joins and QA |

## Open Questions

- `Open question`: Should every school use the school page URL only, or should some listings use a direct form anchor once the live inquiry form URL pattern is confirmed?
- `Open question`: Which live GBP/Yelp fields are available and approved for inquiry-intent links per location?
- `Open question`: Should the canonical school slug source live in `docs/60-master-data/` or `data/reference/` for bulk updates?

## Next Actions

- Confirm the canonical school slug crosswalk before bulk applying these UTMs to all listings.
- Confirm GBP/Yelp field availability before changing live listing URLs.
- Link any future school slug source from this document rather than duplicating the full crosswalk here.

## Files Updated

- `docs/40-naming-convention/local-listing-utm-rules-gbp-yelp-2026-05-03.md`
- `docs/40-naming-convention/README.md`
