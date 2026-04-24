# Plugin vs Theme Decision

Use a CEFA-owned helper plugin as the preferred final Phase 1A event source.

## Reason

Theme-only tracking would couple conversion logic to block/template changes. The Gravity Forms Google Analytics Add-On can be useful, but the observed staging issue is that custom compound Field 32 values can collapse into one combined string.

The helper plugin can use the saved Gravity Forms entry as truth and emit clean values.

## Ownership

| Area | Owner |
|---|---|
| Form 4 UI | Agency / CEFA School Manager |
| Field 32 behavior | Agency / CEFA School Manager |
| School/program/day rendering | Agency / CEFA School Manager |
| School locking | Agency / CEFA School Manager |
| KinderTales/business delivery | Existing runtime / agency |
| Event ID contract | CEFA helper plugin |
| Final `school_inquiry_submit` payload | CEFA helper plugin |
| GA4/Ads/Meta mapping | CEFA / GTM |
| Meta CAPI / collector | Future CEFA Phase 1B |
| sGTM | Future CEFA Phase 2 |
