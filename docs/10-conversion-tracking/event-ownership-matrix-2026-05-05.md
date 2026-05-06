# CEFA Event Ownership Matrix

Last updated: 2026-05-05
Audience: CEFA stakeholders, agency, paid media, analytics, and implementation agents
Scope: Parent `cefa.ca`, Franchise Canada `franchise.cefa.ca`, and Franchise USA `www.franchisecefa.com`

Google Sheet working copy: [CEFA Event Taxonomy - Clean v1 - 2026-05-05](https://docs.google.com/spreadsheets/d/1ztfakcO0oDbO2WVeKCAGOa7c9ks9EHuflfLvVOEiadU/edit)

Sheet structure: parent and franchise are split into separate detailed tabs. Future/planned events are included inside the relevant parent/franchise tabs as gray rows, and detailed parameter contracts are kept in `Parent Parameters` and `Franchise Parameters`. The older mixed taxonomy sheets should be ignored.

## Purpose

This matrix shows who owns each conversion event layer, what each event is used for, and which items are safe for bidding versus reporting only. It is intentionally written as a stakeholder handoff, not as a full GTM implementation export.

## How To Read This

| Term | Meaning |
|---|---|
| Website event | Neutral event pushed by the website or helper bridge into `dataLayer`. |
| Destination event | Platform-specific event configured in GTM, GA4, Google Ads, or Meta. |
| Business truth | The submitted form and CRM/routing record. This is the source of truth for whether a real lead exists. |
| Primary bidding event | Event that paid media can optimize toward. These should be limited to confirmed lead submissions. |
| Micro-conversion | Intent or diagnostic event such as CTA click, form start, submit click, or validation error. These should be used for reporting, not primary bidding. |

## Cross-Property Ownership

| Layer | Primary owner | Applies to | Notes |
|---|---|---|---|
| Website templates, CTAs, page URLs, form placement | Website/theme owner and agency | All properties | Changes to CTA paths, form IDs, or thank-you flows can break tracking context and should be coordinated. |
| Gravity Forms entry and CRM delivery | WordPress/form owner and CRM routing owner | All properties | This is the business truth layer. Tracking must not change lead delivery behavior. |
| Parent tracking bridge | CEFA Conversion Tracking plugin owner | `cefa.ca` | Owns the neutral `school_inquiry_submit` browser event and attribution persistence for parent tracking. |
| Franchise tracking bridge | CEFA tracking owner with franchise site owner | `franchise.cefa.ca`, `www.franchisecefa.com` | Owns neutral franchise helper events and GAConnector cleanup/compatibility where applicable. |
| GTM containers | CEFA tracking/analytics owner | All properties | Maps neutral website events to GA4, Google Ads, Meta, and future server-side destinations. |
| GA4 properties and custom dimensions | CEFA analytics owner | All properties | GA4 receives normalized events and metadata. GA4 should not be treated as CRM truth. |
| Google Ads conversion actions | CEFA paid media/tracking owner | All properties | Primary versus secondary conversion status is a paid-media decision and should be documented before launch changes. |
| Meta dataset and custom conversions | CEFA paid media/tracking owner | All properties | Parent and Canada franchise currently preserve the shared dataset path; USA uses a separate dataset. |
| CAPI, server-side GTM, collector, Measurement Protocol | Future CEFA data/tracking owner | Phase 1B/Phase 2 | Additive server-side validation only until browser parity and duplicate prevention are signed off. |
| Warehouse/reporting truth | CEFA data/BigQuery owner | Future reporting | BigQuery can reconcile events after export, but it does not replace form/CRM truth. |

## Parent Site: `cefa.ca`

| Event | When it fires | Website/source owner | Destination ownership | Business truth | Current status | Stakeholder action |
|---|---|---|---|---|---|---|
| `school_inquiry_submit` | Confirmed successful parent Form 4 inquiry submission. | CEFA Conversion Tracking plugin. | GTM `GTM-NZ6N7WNC` maps to GA4 `generate_lead` on `G-T65G018LYB`, Google Ads `Inquiry Submit_ollo` using `AW-802334988/cFt-CMrLufgCEIzSyv4C`, and Meta `Inquiry Submit` on dataset `918227085392601`. | Gravity Forms Form 4 and KinderTales lead delivery. | Verified as the parent final conversion path. | Keep as the only parent final browser conversion source. Do not re-enable Gravity Forms GA add-on as a competing final source. |
| `validation_error` | Parent Form 4 validation fails. | CEFA Conversion Tracking plugin. | GA4/reporting only. | No lead created. | Active as diagnostic/reporting event. | Do not use for Ads or Meta bidding. |
| `form_start` / `form_submit_click` | Parent starts or attempts the Form 4 flow. | CEFA Conversion Tracking plugin. | GA4/reporting only unless explicitly approved otherwise. | No confirmed lead until Form 4 is saved and routed. | Supporting micro-conversion. | Use for funnel diagnosis, not primary optimization. |
| `parent_inquiry_cta_click` | User clicks an inquiry CTA before reaching the form. | Website template/content plus CEFA tracking plugin. | GA4/reporting only. | No lead created. | Supporting micro-conversion. | Keep CTA URLs stable and school-aware where needed, especially school-page inquiry CTAs that should carry `?location=<slug>`. |
| `phone_click`, `email_click`, `find_a_school_click` | User clicks secondary contact or navigation actions. | Website template/content plus CEFA tracking plugin. | GA4/reporting only. | No form lead by itself. | Supporting micro-conversions. | Use for journey analysis only unless a separate stakeholder decision makes them secondary conversions. |
| Future server-side audit/CAPI event | Server-side confirmation after browser parity is stable. | Future CEFA tracking/data owner. | Future CAPI, collector, sGTM, or Measurement Protocol path. | Gravity Forms/KinderTales plus event identity. | Pending Phase 1B/Phase 2. | Do not activate as a second final source until dedupe and ownership are signed off. |

### Parent Notes

| Item | Owner | Status |
|---|---|---|
| Final parent event name | CEFA tracking owner | `school_inquiry_submit` remains the neutral website event. |
| Final GA4 event | CEFA analytics owner | Mapped to GA4 `generate_lead`. |
| Final Google Ads action | CEFA paid media owner | Existing primary action `Inquiry Submit_ollo` is preserved to avoid unnecessary learning reset. |
| Final Meta event | CEFA paid media owner | Uses `Inquiry Submit` on shared dataset `918227085392601`; custom conversion naming may differ from raw event naming. |
| CTA school context | Website/template owner with CEFA tracking review | Needs coordination when school-page CTAs do not preserve location context in the URL. |

## Franchise Canada: `franchise.cefa.ca`

| Event | When it fires | Website/source owner | Destination ownership | Business truth | Current status | Stakeholder action |
|---|---|---|---|---|---|---|
| `franchise_inquiry_submit` | Confirmed successful Franchise Canada inquiry form submission. | Franchise tracking bridge/WPCode helper and franchise form owner. | GTM `GTM-TPJGHFS` live Version `54` keeps the neutral website event but maps the final submit to GA4 `generate_lead` on `G-6EMKPZD7RD`, Meta `Fr Application Submit` on shared dataset `918227085392601` / custom conversion `Fr Application Submit_CAD` ID `1146840919855743`, and Google Ads primary `fr_application_submit` using `AW-11088792613/cys-CIHslY4YEKWYxqcp`. Secondary Ads tag `fr_inquiry_submit` is paused. | Franchise Gravity Forms entry and franchise routing/Synuma lead delivery. | Partial pass: post-Version-54 browser QA confirmed one helper event, Google Ads primary `fr_application_submit`, GA4 `generate_lead`, no secondary Ads `fr_inquiry_submit`, and Meta `Fr Application Submit` script execution. Meta Events Manager receipt and delayed platform reporting still need confirmation. | Confirm the post-v54 `Fr Application Submit` in Meta Events Manager and delayed GA4/Google Ads processed reports. |
| `real_estate_site_submit` | Confirmed successful Canada real estate/site form submission. | Franchise tracking bridge/WPCode helper and franchise form owner. | GTM `GTM-TPJGHFS` maps to GA4 and Meta `Fr Site Form Submit`; Google Ads currently uses secondary `fr_site_form_submit` with `AW-11088792613/vq7GCIrslY4YEKWYxqcp`. | Franchise Gravity Forms site/real estate form and routing/Synuma delivery. | Active as reporting or secondary conversion path. | Keep secondary unless paid media explicitly decides site forms should be a primary bidding signal. |
| Franchise form start / submit attempt / validation events | User starts, attempts, or fails franchise form validation. | Franchise tracking bridge and form owner. | GA4/reporting only. | No confirmed lead until form is saved and routed. | Supporting diagnostic events where implemented. | Do not use as primary Ads or Meta conversions. |
| GAConnector attribution fields | GAConnector captures and writes campaign/source metadata into hidden fields. | GAConnector/vendor setup plus CEFA tracking owner. | Can be forwarded to GA4/GTM/reporting when clean. | Attribution metadata attached to form entry, not a conversion by itself. | Keep current logic for now. | Preserve current GAConnector behavior until a CEFA-owned replacement is explicitly planned. |
| Future CAPI/server-side audit | Server-side confirmation after browser path is stable. | Future CEFA tracking/data owner. | Future CAPI, collector, sGTM, or Measurement Protocol path. | Form/CRM delivery plus event identity. | Pending Phase 1B/Phase 2. | Keep additive and deduped; do not replace browser path without signoff. |

### Franchise Canada Notes

| Item | Owner | Status |
|---|---|---|
| Final Canada franchise event name | CEFA tracking owner | `franchise_inquiry_submit` remains the neutral inquiry event. |
| Canada Meta dataset strategy | CEFA paid media owner | Keep shared dataset `918227085392601` during transition to avoid abrupt learning reset. |
| Canada Google Ads primary action | CEFA paid media/tracking owner | Resolved for continuity: preserve existing primary `fr_application_submit` and map the helper submit to `AW-11088792613/cys-CIHslY4YEKWYxqcp`. |
| Canada real estate/site forms | CEFA paid media/tracking owner | Should remain secondary unless explicitly approved for bidding. |
| GAConnector | CEFA tracking owner and vendor | Keep for now; future replacement can be planned after launch stability. |

## Franchise USA: `www.franchisecefa.com`

| Event | When it fires | Website/source owner | Destination ownership | Business truth | Current status | Stakeholder action |
|---|---|---|---|---|---|---|
| `franchise_inquiry_submit` | Confirmed successful USA franchise inquiry form submission. | Franchise tracking bridge/WPCode helper and franchise form owner. | GTM `GTM-5LZMHBZL` maps to GA4 `generate_lead` on `G-YL1KQPWV0M` and Meta standard `Lead` on USA dataset `1531247935333023`. Google Ads final helper-submit mapping is still pending. | USA franchise Gravity Forms entry and franchise routing/Synuma lead delivery. | Partial: GA4 and Meta path active; Google Ads final-submit mapping pending. | Map the helper event to the existing primary `Application Submit (USA)` action unless a different paid-media decision is approved. |
| `real_estate_site_submit` | Confirmed successful USA real estate/site form submission. | Franchise tracking bridge/WPCode helper and franchise form owner. | GTM `GTM-5LZMHBZL` maps to GA4; Meta can use USA dataset reporting/custom conversion if approved; Google Ads mapping pending or secondary. | USA real estate/site form entry and routing/Synuma delivery. | Partial/reporting path. | Decide whether this stays reporting-only or becomes a secondary conversion. |
| USA Meta `Lead` | Destination event fired from helper submit mapping. | CEFA GTM/paid media owner. | USA dataset `1531247935333023`; custom conversion `USA Franchise Lead` exists for standard `Lead` plus `/inquiry-thank-you/`. | Depends on underlying helper event and form submission. | Active Meta path. | Keep separate from parent/Canada shared dataset to avoid cross-market contamination. |
| Gravity Forms GA add-on feed for USA Form 1 | Gravity Forms add-on event path if still active. | WordPress/form owner with CEFA tracking review. | Could send GA4/Google tags outside the helper contract. | Form submission, but less controlled than helper event path. | Duplicate-source risk/open item. | Disable or prove audit-only before final signoff. Do not let it become a second final conversion source. |
| Franchise form start / submit attempt / validation events | User starts, attempts, or fails USA form validation. | Franchise tracking bridge and form owner. | GA4/reporting only. | No confirmed lead until form is saved and routed. | Supporting diagnostic events where implemented. | Do not use as primary Ads or Meta conversions. |
| Future CAPI/server-side audit | Server-side confirmation after browser path is stable. | Future CEFA tracking/data owner. | Future CAPI, collector, sGTM, or Measurement Protocol path. | Form/CRM delivery plus event identity. | Pending Phase 1B/Phase 2. | Add only after browser event, event ID, and dedupe rules are stable. |

### Franchise USA Notes

| Item | Owner | Status |
|---|---|---|
| Final USA franchise event name | CEFA tracking owner | `franchise_inquiry_submit` remains the neutral inquiry event. |
| USA Meta dataset strategy | CEFA paid media owner | Uses separate USA dataset `1531247935333023`. |
| USA Google Ads primary action | CEFA paid media/tracking owner | Open item: map helper event to existing primary `Application Submit (USA)` if preserving action history is the chosen path. |
| USA GA4 currency | CEFA analytics owner | Review whether the current currency should remain CAD or move to USD for USA reporting. |
| USA Gravity Forms GA add-on | WordPress/form owner with CEFA tracking review | Should not be a final conversion source unless intentionally approved and deduped. |

## Decision Queue

| Priority | Property | Decision | Recommended owner |
|---|---|---|---|
| High | Parent `cefa.ca` | Keep `school_inquiry_submit` as the only final browser conversion source and avoid reintroducing competing Gravity Forms GA add-on final events. | CEFA tracking owner |
| High | Parent `cefa.ca` | Confirm school-page inquiry CTA links preserve school context, for example `?location=<slug>`, where the form expects location context. | Website/template owner and CEFA tracking owner |
| High | Franchise Canada | Complete delayed platform confirmation after post-Version-54 browser QA: Meta Events Manager receipt for `Fr Application Submit`, GA4 processed `generate_lead`, and Google Ads processed `fr_application_submit`. | CEFA paid media/tracking owner |
| High | Franchise USA | Complete Google Ads helper-submit mapping to the chosen primary action, likely existing `Application Submit (USA)`. | CEFA paid media/tracking owner |
| High | Franchise USA | Disable or prove audit-only the active Gravity Forms GA add-on feed so it does not become a duplicate final source. | WordPress/form owner and CEFA tracking owner |
| Medium | Franchise USA | Review GA4 currency setting for USA reporting. | CEFA analytics owner |
| Medium | All | Keep Measurement Protocol, CAPI, and sGTM as additive Phase 1B/Phase 2 layers until dedupe and ownership are signed off. | CEFA tracking/data owner |

## Do Not Change Without Coordination

| Item | Why coordination is required |
|---|---|
| Form IDs and key hidden fields | GTM, plugin logic, CRM routing, and reporting depend on stable form metadata. |
| Thank-you URLs and confirmation flows | Success events and false-positive guards depend on the confirmation path. |
| GTM container IDs or published versions | Changing containers can silently remove Ads, GA4, or Meta mappings. |
| Google Ads conversion labels | Labels are the live destination for bidding and historical action continuity. |
| Meta pixel/dataset IDs | Dataset changes can affect learning, attribution, and campaign continuity. |
| Gravity Forms GA add-on feeds | These can create duplicate or competing conversion sources if enabled as final events. |
| Helper plugin or WPCode bridge snippets | These are the controlled neutral website event sources. |
| CTA URL patterns | Location and page context can be lost if CTA URLs are changed without tracking review. |

## Summary For Stakeholders

| Property | Final lead event | Current stakeholder-level status |
|---|---|---|
| Parent `cefa.ca` | `school_inquiry_submit` | Final parent path is in place. Keep monitoring and protect the current event/source ownership. |
| Franchise Canada `franchise.cefa.ca` | `franchise_inquiry_submit` | GTM Version `54` preserves existing `Fr Application Submit` / `fr_application_submit` learning paths. Browser QA passed; Meta Events Manager and delayed platform reporting confirmation remain. |
| Franchise USA `www.franchisecefa.com` | `franchise_inquiry_submit` | GA4/Meta path is active; Google Ads final-submit mapping and duplicate-source cleanup remain open. |
