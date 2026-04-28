# Franchise QA And Launch Gates

## Before changing any live franchise campaigns

Do not change campaign optimization until all of these are known:

1. Current Meta dataset/pixel ID.
2. Current Meta event name used for optimization.
3. Current custom conversion rules.
4. Current active campaign/ad set optimization event.
5. Current GTM container and all tags/triggers/variables.
6. Current GA4 property and key events.
7. Current Google Ads conversion actions.
8. Current form stack.
9. Current thank-you/success behavior.
10. Current CRM or lead delivery path.

## Browser QA

For each site:

- submit real test lead
- confirm exactly one final website submit event
- confirm event_id exists
- confirm no duplicate on reload
- confirm no conversion on direct thank-you visit
- confirm form validation failure does not fire lead conversion
- confirm micro-conversions are reporting-only

## GTM QA

- parent tags fire only on parent hostnames
- franchise Canada tags fire only on franchise Canada hostnames
- franchise USA tags fire only on franchise USA hostnames
- base pixels are host-contained
- GA4 config tags are host-contained
- conversion tags are host-contained
- test/staging tags do not fire on production
- production tags do not fire on staging unless intended

## GA4 QA

- correct GA4 property receives events
- event names are correct
- parameters are present
- custom dimensions exist where needed
- DebugView confirms events
- no cross-property event bleed

## Meta Events Manager QA

- correct dataset receives events
- event name is correct
- `event_id` exists
- `event_source_url` matches correct host
- franchise parameters are present
- custom conversions segment correctly
- test events show browser events before campaign changes

## Campaign-level QA

Before moving live optimization:

- export current campaign/ad set settings
- document current optimization event
- document current dataset/pixel
- document current custom conversion
- duplicate/test first if possible
- compare event volume, CPL, lead quality, and attribution
- avoid mass switching all active ad sets at once

## Production launch gate

Do not publish if any of these fail:

- tag fires on wrong host
- wrong Meta dataset receives lead
- shared dataset event cannot separate parent vs franchise
- duplicate lead events fire
- event_id missing
- event_source_url missing or wrong
- direct thank-you visit counts as conversion
