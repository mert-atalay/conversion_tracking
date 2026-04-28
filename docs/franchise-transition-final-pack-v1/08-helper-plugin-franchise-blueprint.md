# Helper Plugin Franchise Blueprint

## Final recommendation

Use the same plugin codebase if practical, but make it configuration-driven.

Do not hardcode parent Form 4 logic into franchise.

Recommended package:

```text
CEFA Conversion Tracking
```

Recommended architecture:

```text
shared core modules
parent module
franchise module
site configuration
```

## Why configurable shared plugin is better

Pros:

- one codebase
- consistent event_id lifecycle
- consistent duplicate guards
- consistent attribution capture
- easier Phase 1B CAPI handoff
- easier sGTM handoff later

Cons:

- requires careful configuration to avoid parent/franchise coupling
- franchise forms may not use Gravity Forms
- each WP backend needs its own config and QA

## Recommended config model

Example config:

```json
{
  "site_context": "franchise_ca",
  "business_unit": "franchise",
  "market": "canada",
  "country": "CA",
  "forms": [
    {
      "form_family": "franchise_inquiry",
      "canonical_event": "franchise_inquiry_submit",
      "success_event": "franchise_inquiry_submit",
      "form_selector": "<verify>",
      "success_url_pattern": "<verify>"
    },
    {
      "form_family": "site_submission",
      "canonical_event": "real_estate_site_submit",
      "form_selector": "<verify>",
      "success_url_pattern": "<verify>"
    }
  ]
}
```

## Franchise plugin modules

### 1. Site context module

Outputs:

```text
site_context
business_unit
market
country
environment
```

### 2. Event ID module

Generates one event ID per successful lead submission.

### 3. Form detection module

Detects known franchise form surfaces and success states.

### 4. DataLayer payload module

Pushes clean neutral website events.

### 5. Duplicate guard module

Prevents reload/direct-thank-you duplicates.

### 6. Attribution module

Captures:

```text
utm_source
utm_medium
utm_campaign
utm_term
utm_content
gclid
gbraid
wbraid
fbclid
msclkid
first_landing_page
first_referrer
```

### 7. Future collector module

Disabled in Phase 1. Used for Phase 1B.

## If franchise does not use Gravity Forms

Use the same event contract, but adapt form hooks to the actual form stack.

The contract matters more than the form technology.
