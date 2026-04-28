# Phase 1A Reference

This folder preserves the implementation decision behind the plugin.

The current accepted boundary is hybrid:

- Agency / CEFA School Manager owns the live form UI and business behavior.
- CEFA helper plugin owns the final tracking contract.
- GTM maps the neutral website event to destination events.
- Gravity Forms Google Analytics Add-On remains optional only if it outputs clean separate values without duplicate risk.

The plugin must remain a tracking bridge only.

## Files

- `../parent-production-cutover-checklist.md`
- `../cross-property-measurement-boundaries.md`
- `plugin-vs-theme-decision.md`
- `gravity-forms-add-on-decision.md`
- `event-flow-and-lifecycle.md`
- `datalayer-contract.md`
- `guardrails.md`
- `acceptance-tests.md`
- `architecture-v7.yaml`
