# Google Platform Access Status

Last updated: 2026-05-04

## Purpose

Document the current local access state for GA4, Google Tag Manager, and Google Ads across the CEFA parent and franchise tracking surfaces.

This file records access verification only. It does not approve live platform edits, bidding changes, conversion-action changes, or tag publication.

## Scope

| Field | Value |
|---|---|
| Workstream | Conversion tracking |
| Platforms | GA4 Admin API, GA4 Data API, Google Tag Manager API, Google Ads API |
| Google identity | `mert.atalay@cefa.ca` |
| Google Cloud project | `marketing-api-488017` |
| Live platform writes made by this update | No |

## Current Verified Access

| Platform | Status | Evidence |
|---|---|---|
| ADC credential shape | Verified | Local ADC is now `authorized_user`, not `impersonated_service_account`. |
| ADC scopes | Verified | Token includes Analytics read/edit, Tag Manager read/edit/publish, Cloud Platform, and Google Ads `adwords` scope. |
| GA4 Admin API | Verified | Account list and property reads work. |
| GA4 Data API | Verified | `runReport` works for all three active CEFA GA4 properties. |
| Google Tag Manager API | Verified | Account/container list works for CEFA parent, CEFA Franchise, and POC accounts. |
| Google Ads OAuth scope | Verified | OAuth token includes Google Ads `adwords` scope. |
| Google Ads API developer token | Verified locally | Developer token accepted by Google Ads API. Token is stored only in local protected config, not in git. |
| Google Ads customer read access | Verified | Customer and conversion-action reads work for parent and franchise accounts. |

## Local Config

| Config | Status | Notes |
|---|---|---|
| `~/.config/gcloud/application_default_credentials.json` | Verified | User ADC for `mert.atalay@cefa.ca`. Do not replace this with an impersonated-service-account ADC for GA4/GTM/Ads work. |
| `~/.config/google-ads.yaml` | Verified | Local protected Google Ads config, file mode `600`. Contains secrets and must not be committed. |
| Google Ads login customer | Verified | `6067148198` / `CEFA`, manager account. |

## Verified GA4 Properties

| Property ID | Name | Account | Currency | Time zone | Status |
|---|---|---|---|---|---|
| `267558140` | `Main Site - GA4` | `accounts/17532283` | `CAD` | `America/Vancouver` | GA4 Admin and Data API verified. |
| `259747921` | `CEFA Franchise` | `accounts/17532283` | `CAD` | `America/Vancouver` | GA4 Admin and Data API verified. |
| `519783092` | `CEFA Franchise - USA.` | `accounts/17532283` | `CAD` | `America/Los_Angeles` | GA4 Admin and Data API verified. Currency should be reviewed for USA reporting signoff. |

## Verified GTM Accounts And Containers

| GTM account | Account name | Container ID | Container name | Notes |
|---|---|---|---|---|
| `4591216764` | `CEFA` | `GTM-PPV9ZRZ` | `www.cefa.ca` | Old parent container, reference/legacy path. |
| `4591216764` | `CEFA` | `GTM-NZ6N7WNC` | `CEFA Staging POC - cefamain.kinsta.cloud` | Current parent production container despite staging-style name. |
| `6004334435` | `CEFA Franchise` | `GTM-TPJGHFS` | `franchise.cefa.ca` | Franchise Canada. |
| `6004334435` | `CEFA Franchise` | `GTM-5LZMHBZL` | `USA-CEFA` | Franchise USA. |
| `6351766032` | `jtacking poc -` | `GTM-T4BQFTRM` | `cefamain.kinsta.cloud` | POC/reference. |
| `6351766032` | `jtacking poc -` | `GTM-TF77KG4D` | `server poc - jtacking` | POC/reference. |

## Verified Google Ads Accounts

| Customer ID | Name | Manager | Currency | Time zone | Status |
|---|---|---:|---|---|---|
| `6067148198` | `CEFA` | `true` | `CAD` | `America/Vancouver` | Login/manager customer. |
| `4159217891` | `CEFA $3000` | `false` | `CAD` | `America/St_Johns` | Parent account read verified. |
| `3820636025` | `CEFA Franchisor` | `false` | `CAD` | `America/Vancouver` | Franchise account read verified. |

## Relevant Conversion-Action Findings

### Parent Account `4159217891`

| Conversion action | ID | Status | Primary for goal | Include in conversions | Notes |
|---|---:|---|---:|---:|---|
| `Inquiry Submit_ollo` | `789472714` | `ENABLED` | `true` | `true` | Current intended parent lead-form bidding action. Its Google Ads label is `cFt-CMrLufgCEIzSyv4C`. |
| `Contact Form Submit_ollo` | `788781971` | `ENABLED` | `true` | `false` | Previously matched the helper-event Ads label before GTM version `7`; no longer the parent helper-event Ads label. |
| `generate_lead (GA4)` | `6540439360` | `ENABLED` | `false` | `false` | GA4-imported action exists but is secondary/not included. |
| `Phone Click_ollo` | `789475090` | `ENABLED` | `true` | `false` | Enabled but not included in conversions metric. |
| `Email Click_ollo` | `789488589` | `ENABLED` | `true` | `false` | Enabled but not included in conversions metric. |
| `Application Submit_ollo` | `788776715` | `ENABLED` | `false` | `false` | Not a parent inquiry primary. |

### Franchise Account `3820636025`

| Conversion action | ID | Status | Primary for goal | Include in conversions | Notes |
|---|---:|---|---:|---:|---|
| `fr_application_submit` | `6472168961` | `ENABLED` | `true` | `true` | Existing franchise primary lead action. |
| `fr_inquiry_submit` | `6472168964` | `ENABLED` | `false` | `false` | Existing secondary/non-included action. |
| `fr_site_form_submit` | `6472168970` | `ENABLED` | `false` | `false` | Existing secondary/non-included action. |
| `generate_lead (GA4)` | `6480960234` | `ENABLED` | `false` | `false` | GA4-imported action exists but is secondary/not included. |
| `Application Submit (USA)` | `7482298930` | `ENABLED` | `true` | `true` | Existing USA primary lead action inside franchise account. |
| `CEFA Franchise - USA. (web) generate_lead` | `7499744287` | `HIDDEN` | `false` | `false` | USA GA4-imported action exists but is hidden/secondary. |

## Current Access Guardrails

- Do not commit `~/.config/google-ads.yaml`, ADC files, OAuth client files, refresh tokens, client secrets, or developer tokens.
- Do not make Google Ads primary/secondary changes without explicit approval and a before/after action list.
- Do not publish GTM container versions without explicit approval and a rollback note.
- Do not archive GA4 dimensions, key events, or Ads conversion actions until historical dependencies are reviewed.
- Keep parent and franchise account decisions separate even though the manager account can read both.

## Remaining Access Questions

| Item | Status | Notes |
|---|---|---|
| Meta Events Manager/API access | Pending | Not part of Google access; still needed for Meta custom conversion and optimization-event confirmation. |
| Long-lived production auth for automation | Pending | Local user ADC is fixed for Codex/operator work. Production automation should use workload identity, service accounts where API-supported, or approved secrets management. |
| USA GA4 currency | Open question | `CEFA Franchise - USA.` currently uses `CAD`; confirm whether this is intentional before final USA reporting signoff. |

## Next Actions

1. Use Google Ads API read access to produce a final parent conversion-action signoff table.
2. Verify the parent GTM helper-event Ads request uses `AW-802334988/cFt-CMrLufgCEIzSyv4C` after the version `7` label correction.
3. Do the same conversion-action decision for Franchise Canada and Franchise USA.
4. Resolve Meta access separately.
5. After approval, make platform changes in small batches with documented before/after values.
