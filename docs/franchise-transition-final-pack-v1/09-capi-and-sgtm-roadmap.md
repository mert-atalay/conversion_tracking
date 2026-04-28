# CAPI And sGTM Roadmap

## Current recommendation

Do not make CAPI or sGTM a blocker for franchise Phase 1 browser tracking.

Use this order:

```text
Phase 1 = browser parity and clean event contracts
Phase 1B = Meta CAPI / collector
Phase 2 = custom-domain sGTM
```

## Why CAPI comes before sGTM

Meta CAPI can provide practical recovery from browser loss and ad blockers once the browser event identity is stable.

But CAPI must use:

```text
same event_name
same event_id
same dataset as the campaign being optimized
```

during transition.

## CAPI by surface

### Parent

CAPI should use parent dataset once parent Meta strategy is finalized.

### Franchise Canada

If active campaigns rely on the shared dataset, first CAPI events should go to the current shared dataset for continuity.

Do not send the same event to both old and new datasets for the same campaign unless clearly in testing mode.

### Franchise USA

Use the USA dataset.

## sGTM timing

sGTM remains Phase 2.

Franchise separation does not make sGTM urgent by itself. The urgent Phase 1 needs are:

- hostname containment
- clean event contracts
- Meta dataset transition plan
- no parent/franchise tag bleed
- no duplicate lead events

sGTM becomes important later for:

- custom-domain first-party routing
- server-side enrichment
- stronger privacy controls
- BigQuery handoff
- offline/lifecycle conversion uploads

## Custom-domain sGTM future structure

Recommended future server domains:

```text
metrics.cefa.ca                 parent
metrics.franchise.cefa.ca       franchise Canada, if feasible
metrics.franchisecefa.com       franchise USA
```

Alternative:

```text
collect.cefa.ca
collect.franchise.cefa.ca
collect.franchisecefa.com
```

Each should be evaluated with DNS, hosting, consent, and cookie-domain implications.
