# Parent Analytics Tracking Skill Review - 2026-05-05

Status: review complete; no live GTM, GA4, Ads, Meta, or WordPress changes made by this review.

Property: parent `cefa.ca`

## Purpose

This review checks the current CEFA parent conversion-tracking plan against the external analytics-tracking skill from:

- `https://github.com/coreyhaines31/marketingskills/tree/main/skills/analytics-tracking`
- Local review clone commit: `1bcff9fc79c64fd7886c3c7aa583f4bd63916ff2`

The external skill was used as an additional implementation-quality checklist only. CEFA conversion tracking remains canonical for event names, property boundaries, plugin ownership, and business-truth rules.

## External Skill Principles Applied

The external analytics-tracking skill emphasizes:

- Track for decisions, not volume.
- Use consistent lower-snake-case event names.
- Put context in properties, not event names.
- Validate that events fire on the correct trigger.
- Validate that parameter values populate correctly.
- Avoid duplicate events.
- Test across browser and mobile.
- Verify conversion recording, not just tag execution.
- Avoid PII in analytics properties.
- Use GTM Preview, GA4 DebugView, Tag Assistant, and browser/network checks before publish.
- Use descriptive GTM version names and notes.

These principles support the existing CEFA plan. They do not require changing the canonical parent event or replacing the helper-plugin approach.

## Current CEFA Parent State Reviewed

Current intended parent path:

```text
Gravity Forms Form 4 confirmed submission
-> CEFA Conversion Tracking plugin
-> one-time thank-you token
-> dataLayer event: school_inquiry_submit
-> GTM-NZ6N7WNC
-> GA4 generate_lead
-> Google Ads existing Inquiry Submit_ollo action
-> Meta Inquiry Submit after Meta-only restore publish
```

Current reviewed facts from repo documentation and Tag Assistant export:

- Parent canonical website event is `school_inquiry_submit`.
- Helper-plugin dataLayer event is the final browser conversion source.
- Gravity Forms Google Analytics Add-On is not the final conversion source.
- Live parent plugin version is documented as `cefa-conversion-tracking` `0.4.3`.
- Active parent GTM container is `GTM-NZ6N7WNC`.
- Old parent GTM `GTM-PPV9ZRZ` is archived/reference-only.
- Tag Assistant preview showed `school_inquiry_submit` with clean values for school, program, days, `event_id`, and `tracking_source=helper_plugin`.
- Google-side final tags remain active in public live GTM version `9`.
- Meta Tags `39` and `40` worked in preview but remain paused in public live GTM version `9` until a narrow restore publish.
- Unsafe GA4 Custom HTML micro-event tags `66`, `67`, and `68` must stay paused.

## Review Decision

No strategic change is needed.

The external analytics-tracking guidance strengthens the current plan rather than changing it:

- Keep `school_inquiry_submit` as the website-side source event.
- Keep GTM as the destination mapping layer.
- Keep GA4 destination event as `generate_lead`.
- Keep Google Ads mapped to the existing `Inquiry Submit_ollo` action to preserve continuity.
- Keep Meta mapped to the existing parent dataset/pixel/event continuity path once Tags `39` and `40` are safely restored.
- Keep Measurement Protocol server-side work audit-only until browser parity and duplicate controls are proven.

## Event Naming Assessment

The external skill recommends generic names such as `form_submitted`, but CEFA should not switch to that generic website event.

Reason:

- `school_inquiry_submit` is lower-snake-case.
- It is specific enough to identify the business event.
- It keeps context such as school, program, days, lead type, and lead intent in properties.
- It maps cleanly to GA4 `generate_lead`, Meta `Inquiry Submit` or `Lead`, and Google Ads conversion actions.

Destination naming exceptions are acceptable:

- Google Ads action `Inquiry Submit_ollo` should remain for continuity unless CEFA deliberately migrates bidding later.
- Meta `Inquiry Submit` may remain as the continuity event/custom conversion if that is what current campaigns and reporting use.
- These destination names do not need to match the neutral website event exactly.

## GTM Implementation Assessment

The external GTM reference allows Custom HTML for pixels, but the CEFA incident shows an important boundary:

- Custom HTML is acceptable for Meta Pixel calls if it is narrowly triggered and does not push recursive dataLayer events.
- Custom HTML is not acceptable for GA4 micro-events when it calls `gtag()` using the same event name as the GTM trigger.
- GA4 event delivery should use native GA4 Event tags or another non-looping implementation pattern.

Therefore:

- Keep Tags `66`, `67`, and `68` paused.
- Do not recreate GA4 `form_start`, `form_submit_click`, or `validation_error` through Custom HTML `gtag()` snippets.
- If micro-events are restored later, use native GA4 Event tags triggered by the helper-plugin dataLayer events.
- Publish only narrowly scoped changes with descriptive GTM version names and rollback notes.

## Data Quality Assessment

The current CEFA contract aligns with the external skill's data-quality rules:

- One valid Form 4 submission should create one final conversion event.
- `event_id` is single-event scoped and must not be school UUID, slug, program ID, or location ID.
- School, program, and days are separate metadata fields.
- Direct thank-you visits should not fire a final conversion.
- Failed validation should not fire `generate_lead`; it can emit `validation_error` as a diagnostic event.
- No PII should be sent to GA4, Ads, Meta, or GTM parameters.

Additional guardrail from this review:

- Do not register high-cardinality values such as `event_id`, full URLs, raw referrers, click IDs, parent names, emails, phone numbers, notes, or child details as GA4 custom dimensions.

## Micro-Conversion Assessment

The external event library includes CTA and form-interaction events. CEFA can use those, but not as primary launch conversions.

Recommended boundary:

- Final parent conversion: `school_inquiry_submit`.
- Diagnostic or remarketing events: `parent_inquiry_cta_click`, `find_a_school_click`, `phone_click`, `email_click`, `form_start`, `form_submit_click`, `validation_error`.
- Google Ads bidding at launch: final submit only.
- Micro-conversions should remain GA4/Meta/remarketing/reporting-only unless CEFA explicitly approves a bidding strategy change.

Micro-events may carry their own event identifiers for QA if needed, but they should not be treated as the same final-conversion deduplication identity as the Form 4 submit event.

## Consent And Privacy Assessment

The Tag Assistant preview showed consent granted for:

- `ad_storage`
- `analytics_storage`
- `ad_user_data`
- `ad_personalization`

That is useful but not a complete production consent audit.

Before final cleanup or Phase 1B, confirm:

- Consent defaults before user choice.
- Consent update behavior after choice.
- Whether Meta and Google Ads tags respect consent.
- Whether any destination receives PII or prohibited form values.
- Whether internal/test traffic is filtered or marked.

This is especially important before server-side/CAPI expansion.

## Server-Side And Measurement Protocol Assessment

The external GA4 guidance says Measurement Protocol can supplement tracking. That matches the current CEFA Phase 1B position.

Do not use Gravity Forms Measurement Protocol to send a second primary GA4 `generate_lead` while the browser/GTM path is active.

Approved exploration path:

```text
school_inquiry_submit_server_audit
```

Rules:

- Not a GA4 key event.
- Not imported to Google Ads.
- Shares the same Form 4 `event_id`.
- Sends only non-PII metadata and approved attribution fields.
- Used for parity testing before any future server-side primary conversion migration.

## Franchise Implications

This parent review reinforces the cross-property plan:

- Parent, Franchise Canada, and Franchise USA should not share broad unscoped GTM triggers.
- Franchise events should remain neutral website events such as `franchise_inquiry_submit` and `real_estate_site_submit`.
- Franchise Canada can temporarily use the currently optimized shared Meta dataset only if campaign continuity requires it.
- Franchise USA should use the separate USA dataset/pixel path before serious optimization.
- Hostname scoping is mandatory wherever a shared domain/subdomain or shared container risk exists.

## Updated Parent Action Plan

1. Publish only Meta Tags `39` and `40`.
2. Keep Tags `66`, `67`, and `68` paused.
3. Name the GTM version explicitly, for example: `Restore parent Meta tags only - keep GA4 Custom HTML micro tags paused - 2026-05-05`.
4. Run one desktop Form 4 controlled submission.
5. Run one mobile Form 4 controlled submission.
6. Confirm exactly one `school_inquiry_submit`.
7. Confirm GA4 `generate_lead`.
8. Confirm Google Ads request uses `AW-802334988/cFt-CMrLufgCEIzSyv4C`.
9. Confirm Meta PageView and Meta `Inquiry Submit` use the same final `event_id`.
10. Confirm Contact Us and inquiry dropdowns do not freeze.
11. Confirm no repeated inline `G-T65G018LYB` scripts are injected.
12. Reconcile GTM, GA4, Google Ads, Meta, BigQuery, and Gravity Forms/KinderTales/business truth after the next traffic window.

## Signoff Checklist Added From External Review

- [ ] Every tracked event has an owner and decision purpose.
- [ ] Website event names use lower-snake-case.
- [ ] Destination event/action names are documented when they differ for continuity.
- [ ] Event parameters are populated and low-cardinality where registered in GA4.
- [ ] No PII is sent to analytics/ad platforms.
- [ ] No duplicate final conversion sources are active.
- [ ] GTM Preview is clean before publish.
- [ ] Public live container is tested after publish.
- [ ] Browser/network proof exists.
- [ ] Platform proof exists.
- [ ] Mobile proof exists.
- [ ] Business-truth reconciliation path exists.

## Final Judgment

The external analytics-tracking skill does not invalidate the CEFA plan. It confirms the right direction:

- Use a clean dataLayer contract.
- Keep context in parameters.
- Avoid duplicate conversion sources.
- Validate before and after GTM publish.
- Keep no-PII and consent controls explicit.
- Keep server-side work additive/audit-only until the browser path is stable.

The immediate risk is not the helper plugin. The immediate risk is reintroducing broad or recursive GTM Custom HTML tags. The next live action should remain the narrow Meta-only restore publish, followed by controlled QA.
