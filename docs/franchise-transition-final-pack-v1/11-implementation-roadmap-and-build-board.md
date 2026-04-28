# Implementation Roadmap And Build Board

## Workstream 1 — Parent production cutover

Owner: CEFA/GTM + agency for site deployment support

Tasks:

- export staging GTM
- export production GTM before changes
- deploy helper plugin to production
- verify routes
- verify Form 4 field stability
- verify `school_inquiry_submit`
- verify GA4 `generate_lead`
- verify Google Ads label
- verify parent Meta strategy
- freeze cleanup until post-cutover

## Workstream 2 — Franchise Canada audit

Owner: CEFA/GTM + agency

Tasks:

- inspect `cefafranchise.kinsta.cloud`
- identify form stack
- identify thank-you/success pages
- identify GTM container
- identify Meta dataset/pixel
- identify current active campaign optimization event
- map CTA/forms
- build franchise event contract
- set hostname containment

## Workstream 3 — Franchise Canada shared-dataset stabilization

Tasks:

- keep shared dataset for active campaigns
- add franchise parameters
- create `Franchise Canada Lead` custom conversion
- test events in shared dataset
- verify custom conversion segmentation
- do not change active campaign optimization yet

## Workstream 4 — Franchise Canada parallel dataset

Tasks:

- create/identify new franchise Canada dataset
- test events
- verify event quality
- launch new/duplicated campaign test
- compare performance
- plan phased migration

## Workstream 5 — Franchise USA clean setup

Tasks:

- audit staging site
- create/confirm separate USA GA4 property
- create/confirm separate USA Meta dataset
- build USA GTM container
- build event contract
- run test events before serious optimization

## Workstream 6 — Phase 1B / Phase 2

Tasks:

- collector design
- Meta CAPI
- event dedup
- custom-domain sGTM
- BigQuery
- lifecycle uploads
