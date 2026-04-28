# GTM Containment And Container Blueprint

## Final recommendation

Use separate GTM web containers per site family where practical.

Recommended:

```text
Parent Canada container
Franchise Canada container
Franchise USA container
```

If the team must use a shared container temporarily, every major tag, trigger, variable, and lookup table must be hostname-contained.

## Why this matters

Franchise Canada production is expected to be:

```text
franchise.cefa.ca
```

Because it is under the `cefa.ca` root, broad all-pages triggers, shared cookies, linker settings, or shared Meta base pixels can bleed across parent and franchise if not controlled.

## Required hostname variables

Create:

```text
DLV / Built-in: Page Hostname
Lookup Table: Site Context From Hostname
```

Recommended hostname mapping:

| Hostname | site_context | market | business_unit |
|---|---|---|---|
| `cefa.ca` | `parent_ca` | `canada` | `parent` |
| `www.cefa.ca` | `parent_ca` | `canada` | `parent` |
| `cefamain.kinsta.cloud` | `parent_ca_staging` | `canada` | `parent` |
| `franchise.cefa.ca` | `franchise_ca` | `canada` | `franchise` |
| `cefafranchise.kinsta.cloud` | `franchise_ca_staging` | `canada` | `franchise` |
| `www.franchisecefa.com` | `franchise_us` | `usa` | `franchise` |
| `franchisecefa.com` | `franchise_us` | `usa` | `franchise` |
| `cefafranusdev.wpenginepowered.com` | `franchise_us_staging` | `usa` | `franchise` |

## Host-scoped triggers

Every destination tag should have one of these trigger guards:

```text
Parent Host Guard
Franchise CA Host Guard
Franchise US Host Guard
```

Examples:

```text
Parent GA4 base tag fires only on parent_ca hosts.
Franchise CA GA4 base tag fires only on franchise_ca hosts.
Franchise US GA4 base tag fires only on franchise_us hosts.
Parent Meta Pixel fires only on parent_ca hosts.
Franchise CA Meta Pixel fires only on franchise_ca hosts.
Franchise US Meta Pixel fires only on franchise_us hosts.
```

## Avoid

- one broad “All Pages” tag without hostname guard
- one shared Meta base pixel firing across all surfaces by accident
- parent micro-conversions firing on franchise
- franchise lead conversions firing on parent
- cross-domain linker changes without QA
- cookie domain assumptions copied from parent to franchise

## GTM naming convention

Recommended names:

```text
EV - parent - school_inquiry_submit
EV - franchise_ca - franchise_inquiry_submit
EV - franchise_us - franchise_inquiry_submit
TR - host - parent_ca
TR - host - franchise_ca
TR - host - franchise_us
TAG - GA4 - parent - generate_lead
TAG - GA4 - franchise_ca - generate_lead
TAG - META - franchise_ca - Lead
```
