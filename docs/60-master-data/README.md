# Master Data Workstream

This folder is for canonical and partial reference data across schools, programs, locations, CRM systems, and marketing platforms.

## Current Files

- [Final known school/program tracking reference](../known-school-program-reference-table-2026-05-03.md)
- [Canonical school/program taxonomy status](../canonical-school-program-taxonomy-2026-05-03.md)
- [Master data, taxonomy, conversion, and metrics reference](./cefa-master-data-taxonomy-and-measurement-reference-2026-05-03.md)
- [School dimension warehouse coverage, 2026-05-03](./school-dimension-warehouse-coverage-2026-05-03.md)

## Current Rules

- Parent school tracking join key: `school_uuid`.
- Program tracking join key: `program_id` where available.
- `canonical_location_id` is present for all checked school rows but mixed-format; do not treat it as the final normalized school key yet.
- School labels, slugs, campaign names, and ad names are aliases only.
- Keep missing external IDs as `pending`; do not fill guesses.

## Current Known Gaps

- WordPress School Manager ID missing for South Surrey - Morgan Crossing East and Surrey - Panorama North.
- Gravity routing missing for South Surrey - Morgan Crossing East, Surrey - Cloverdale, Surrey - Panorama North, and Surrey - Sullivan Ridge.
- School code missing for Calgary - South, North Vancouver - Capilano Mall, and Surrey - Sunnyside.
- CRM/KinderTales journey-code mapping for programs is still pending.

## Suggested Next Files

- `school-crosswalk.csv` in `data/reference/`
- `program-crosswalk.csv` in `data/reference/`
- `crm-system-crosswalk.md`
- `gbp-location-crosswalk.md`
