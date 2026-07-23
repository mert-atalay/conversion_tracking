# Governance

This folder defines how the CEFA marketing measurement repo is organized.

Start here when adding a new document, routing work to another agent, or deciding where a new source-of-truth update belongs.

## Files

- [measurement-and-activation-program-register-2026-07-23.md](./measurement-and-activation-program-register-2026-07-23.md): cross-workstream status, approved tooling, blockers, build sequence, and production gates for conversion tracking, Stape sGTM, BigQuery/Dataform, and offline activation.
- [repo-map.md](./repo-map.md): folder map, workstream boundaries, and where each agent should write.
- [source-of-truth-rules.md](./source-of-truth-rules.md): authority order and verification rules.
- [data-taxonomy.md](./data-taxonomy.md): cross-workstream map of CEFA data sources, stable IDs, naming keys, conversion events, warehouse surfaces, and owning docs.
- [repository-structure-audit-2026-06-03.md](./repository-structure-audit-2026-06-03.md): current repo/branch structure audit, collision risks, and branch consolidation recommendation.
- [codex-machine-migration-checklist-2026-06-04.md](./codex-machine-migration-checklist-2026-06-04.md): non-secret checklist for carrying Codex config, memory, MCPs, plugins, local workspaces, and auth surfaces to a new Mac.
- [agent-responsibilities.md](./agent-responsibilities.md): agent/workstream ownership boundaries.
- [contribution-workflow.md](./contribution-workflow.md): how to add docs without mixing workstreams.

## Core Rule

Use this repo as the shared reference layer, but keep facts in the narrowest correct location. Runtime plugin code, tracking plans, BigQuery contracts, SEO notes, naming rules, and paid-media execution notes should not be mixed into one file.
