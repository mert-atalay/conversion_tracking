# Meta Bulk Import Success Pattern - 2026-05-05

## Scope

| Field | Value |
| --- | --- |
| Workstream | `docs/40-naming-convention/` |
| Platform | Meta Ads |
| Applies to | CEFA Franchisor / Franchise Canada video ads |
| Related local artifact | `/Users/matthewbison/Desktop/cefa-nexus/CEFA/.agency/artifacts/meta-bulk-import/2026-05-05-franchise-canada-video-refresh/` |
| Drive file | [live-status-safe CSV](https://drive.google.com/file/d/1jzghoeo_v97f7774zNEBIH0aRbDNAt91/view?usp=drivesdk) |
| Live Meta writes made in this documentation update | No |

## Status

`Verified`

- User confirmed the final Ads Manager bulk import was successful.
- The import used the `live_status_safe` file:
  `meta_bulk_import_add_only_new_ads_paused_live_status_safe_2026-05-05.csv`.
- The uploaded Drive copy was downloaded back and checksum-validated before import.
- The final file contained 12 intended create-ad rows: four ad copy angles across three target ad sets.
- `Ad ID` was blank for every row, making the file add-only at the ad level.
- `Ad Status` was `PAUSED` for every new ad row.
- Campaign and ad set status fields were adjusted to match live Meta API status before upload.
- Destination was kept in `Link`; tracking was kept in `URL Tags`.

`Partial`

- User reported that Meta added browser/add-on items such as WhatsApp during the import flow.
- The exact controlling Meta UI setting or import-template column is not verified.
- The prepared file's checked headers did not expose a confirmed WhatsApp/add-on-specific column. Relevant nearby fields included `Publisher Platforms`, `Messenger Positions`, `Destination Type`, `Degrees of Freedom Type`, `Text Transformations`, and `Add End Card`.

`Pending`

- The account appears eligible for ad-level tags, but the current checked export templates do not show a confirmed dedicated ad-level tag/label column beyond `URL Tags` and `Additional Custom Tracking Specs`.
- Verify whether Ads Manager export/import or the Meta Marketing API `adlabels` path can write/read ad-level tags before adding them to the workbook, control center, or n8n automation.

## Reusable Pattern

For future CEFA Meta bulk imports:

1. Start from a fresh Ads Manager export/import schema for the relevant account.
2. Keep the generated import file UTF-16 tab-delimited, even if the extension is `.csv`.
3. For create-ad rows under existing objects, populate Campaign ID and Ad Set ID, but leave Ad ID blank.
4. Set all new ad rows to `PAUSED`.
5. Check live campaign/ad set status immediately before upload and mirror those status values in the file.
6. Preserve existing campaign/ad set names in the upload file unless the batch is explicitly approved as a rename batch.
7. Put destination URLs in `Link` and final UTMs in `URL Tags`.
8. Put the Meta video asset ID in `Video ID`; this successful batch used `v:27350182134612138`.
9. Use Ads Manager bulk import preview and accept only if the preview shows the intended new paused ad rows.
10. After import, export the created ads and reconcile IDs, add-ons, statuses, tags, and URL tags.

## Guardrails

- Do not treat this successful import as approval to activate campaigns, ad sets, or ads.
- Do not treat this as approval to change budgets, optimization events, datasets, pixels, or attribution settings.
- Do not add ad-level tags to NC1/NC2 or automation until their read/write path is verified.
- Before the next import, inspect Ads Manager preview for unwanted Meta add-ons, especially WhatsApp/browser add-on behavior.

## Related Docs

- [Meta creative build import manifest contract](./meta-creative-build-import-manifest-2026-05-04.md)
- [Naming convention workstream README](./README.md)
