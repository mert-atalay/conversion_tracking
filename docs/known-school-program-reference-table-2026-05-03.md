# Final Known School And Program Tracking Reference

Last updated: 2026-05-03

## Purpose

This file is the concrete known-values reference for CEFA parent conversion tracking joins. It documents what is currently verified and leaves unresolved cross-system IDs as `pending` instead of guessing.

Use `school_uuid` as the final parent-tracking school join key. Use `program_id` as the final parent-tracking program join key once emitted with Form 4/GA4 events.

Do not treat the current warehouse `canonical_location_id` column as the final normalized school key yet. It is present for every checked school row, but it is mixed-format: some rows are UUID-like and some rows are slug-like. That makes it useful as current warehouse metadata, not the safest cross-system tracking key.

## Source Coverage

| Requested field | Current status | Current source | Notes |
|---|---|---|---|
| Stable school ID | known | `school_uuid` | Used by Form 4 `32.1`, helper payload `school_selected_id`, CEFA Ops school map, and `mart_marketing.dim_school`. |
| WordPress School Manager ID | pending | WordPress backend / School Manager export | Not present in the verified warehouse table used for this file. |
| Canonical location ID | known but not normalized | `mart_marketing.dim_school.canonical_location_id` | Present for all 53 rows; 40 UUID-like values and 13 slug-like values. Use `school_uuid` as tracking join key until normalized. |
| GreenRope group/location ID | pending | CRM or upstream warehouse source | `greenrope_primary_location_id` exists in an assertion schema, but no populated values were available in the checked table. |
| KinderTales ID | known as `school_uuid` unless disproven | CEFA Ops School Identity Map | Ops note defines `school_uuid` as current KinderTales school unique ID. Keep a separate column later only if downstream proves another ID. |
| Gravity Forms school label | partially known | Form 4 `32.6` / GA4 `school_selected_name` | Available in events/entries, but not yet normalized as a complete source table. |
| GA4/location label | partially known | GA4 event params | `school_selected_id`, `school_selected_slug`, and `school_selected_name` are sent with helper-plugin lead events. |
| GBP location | pending | GBP or upstream warehouse source | `gbp_location_id` exists in an assertion schema, but no populated values were available in the checked table. |
| Ad account naming | pending | CEFA naming convention / platform exports | Only account-level classification is verified; school-level ad naming key is not complete. |

## Known School Location Table

Source: `marketing-api-488017.mart_marketing.dim_school` joined by `school_uuid` to the CEFA Ops School Identity Map for `region` and `school_code`.

Important caveat: `canonical_location_id` is present for all 53 checked rows, but the current warehouse values are mixed-format. BigQuery verification on 2026-05-03 showed 40 UUID-like values and 13 slug-like values. Treat slug-like values as current known warehouse values, not as blanks, but do not assume the column has been normalized to one ID format yet.

Final tracking rule: use `school_uuid` for parent tracking joins and deduped school reporting until `canonical_location_id` is normalized into one agreed format.

| school_uuid | kindertales_school_id | canonical_location_id | location_code | location_name | region | school_code | school_slug | landing_page_path |
|---|---|---|---|---|---|---|---|---|
| 81236954-bcad-11ef-8bcb-028d36469a89 | 81236954-bcad-11ef-8bcb-028d36469a89 | 4abfc0c0-c672-43f6-899d-b3730f143db9 | abbotsford-highstreet | Abbotsford - Highstreet | British Columbia | ABB2M9 | abbotsford-highstreet | /cefa-find-a-school/abbotsford-highstreet |
| 812376b1-bcad-11ef-8bcb-028d36469a89 | 812376b1-bcad-11ef-8bcb-028d36469a89 | 5eca862e-d01f-4db9-965d-d91c956db45a | burlington-south-service-road | Burlington - South Service Road | Ontario | BUR4X5 | burlington-south-service-road | /cefa-find-a-school/burlington-south-service-road |
| 81236ff4-bcad-11ef-8bcb-028d36469a89 | 81236ff4-bcad-11ef-8bcb-028d36469a89 | burnaby-brentwood | burnaby-brentwood | Burnaby - Brentwood | British Columbia | BUR3Z5 | burnaby-brentwood | /cefa-find-a-school/burnaby-brentwood |
| 81237055-bcad-11ef-8bcb-028d36469a89 | 81237055-bcad-11ef-8bcb-028d36469a89 | burnaby-canada-way | burnaby-canada-way | Burnaby - Canada Way | British Columbia | BUR1M4 | burnaby-canada-way | /cefa-find-a-school/burnaby-canada-way |
| 812370b7-bcad-11ef-8bcb-028d36469a89 | 812370b7-bcad-11ef-8bcb-028d36469a89 | 97938001-2850-4646-a0a7-bfb0bd12668d | burnaby-kingsway | Burnaby - Kingsway | British Columbia | BUR1Y9 | burnaby-kingsway | /cefa-find-a-school/burnaby-kingsway |
| 8123764f-bcad-11ef-8bcb-028d36469a89 | 8123764f-bcad-11ef-8bcb-028d36469a89 | calgary-beacon-hill | calgary-beacon-hill | Calgary - Beacon Hill | Alberta | CAL0A1 | calgary-beacon-hill | /cefa-find-a-school/calgary-beacon-hill |
| d39b7b92-5af3-41fe-bdea-700d9578b955 | d39b7b92-5af3-41fe-bdea-700d9578b955 | 3bb8b0ce-0f92-43a9-a8f9-d224bc60988b | calgary-beltline | Calgary - Beltline | Alberta | CAL3Y6 | calgary-beltline | /cefa-find-a-school/calgary-beltline |
| 81237836-bcad-11ef-8bcb-028d36469a89 | 81237836-bcad-11ef-8bcb-028d36469a89 | f0cc460e-9eb6-4870-8cf5-0e574ff67f03 | calgary-cornerstone | Calgary - Cornerstone | Alberta | CAL1K1 | calgary-cornerstone | /cefa-find-a-school/calgary-cornerstone |
| 6217b777-8b97-484a-8699-c7f8c248b78a | 6217b777-8b97-484a-8699-c7f8c248b78a | 6c6f1b55-c8ca-4969-b0aa-41c448ded4f2 | calgary-northland | Calgary - Northland | Alberta | CAL2J8 | calgary-northland | /cefa-find-a-school/calgary-northland |
| 812368e9-bcad-11ef-8bcb-028d36469a89 | 812368e9-bcad-11ef-8bcb-028d36469a89 | calgary-south | calgary-south | Calgary - South | Alberta | pending | calgary-south | /cefa-find-a-school/calgary-south |
| 812377d6-bcad-11ef-8bcb-028d36469a89 | 812377d6-bcad-11ef-8bcb-028d36469a89 | ab431137-854d-43dc-b5ec-874e86d7f29d | calgary-south-trail-crossing | Calgary - South Trail Crossing | Alberta | CAL3V8 | calgary-south-trail-crossing | /cefa-find-a-school/calgary-south-trail-crossing |
| 81237b65-bcad-11ef-8bcb-028d36469a89 | 81237b65-bcad-11ef-8bcb-028d36469a89 | 52648827-5803-4f22-9e6f-6af53b604663 | chilliwack-cottonwood | Chilliwack - Cottonwood | British Columbia | CHI4E7 | chilliwack-cottonwood | /cefa-find-a-school/chilliwack-cottonwood |
| 81236dfb-bcad-11ef-8bcb-028d36469a89 | 81236dfb-bcad-11ef-8bcb-028d36469a89 | def3b657-8d7e-45ba-8493-d88d55226d57 | coquitlam | Coquitlam | British Columbia | COQ0J5 | coquitlam | /cefa-find-a-school/coquitlam |
| 81237582-bcad-11ef-8bcb-028d36469a89 | 81237582-bcad-11ef-8bcb-028d36469a89 | delta-captain-s-cove | delta-captain-s-cove | Delta - Captains Cove | British Columbia | DEL0E6 | delta-captains-cove | /cefa-find-a-school/delta-captains-cove |
| 81236cdd-bcad-11ef-8bcb-028d36469a89 | 81236cdd-bcad-11ef-8bcb-028d36469a89 | 2aa4b3fd-fcf1-4afd-b849-46dc211f703d | kelowna-mckay | Kelowna - McKay | British Columbia | KEL5A8 | kelowna-mckay | /cefa-find-a-school/kelowna-mckay |
| 81236d3d-bcad-11ef-8bcb-028d36469a89 | 81236d3d-bcad-11ef-8bcb-028d36469a89 | 98773e91-5ddb-4322-be07-a7eb23b32d2c | kelowna-spall | Kelowna - Spall | British Columbia | KEL4P7 | kelowna-spall | /cefa-find-a-school/kelowna-spall |
| 81236f94-bcad-11ef-8bcb-028d36469a89 | 81236f94-bcad-11ef-8bcb-028d36469a89 | 807f3a84-6f47-489f-bbd6-5311b09f3697 | langley-city-centre | Langley - City Center | British Columbia | LAN5E6 | langley-city-center | /cefa-find-a-school/langley-city-center |
| 81237114-bcad-11ef-8bcb-028d36469a89 | 81237114-bcad-11ef-8bcb-028d36469a89 | a3c178e9-d292-4f5a-9c85-a14feff74185 | langley-walnut-grove | Langley - Walnut Grove | British Columbia | LAN0A5 | langley-walnut-grove | /cefa-find-a-school/langley-walnut-grove |
| 81236d9e-bcad-11ef-8bcb-028d36469a89 | 81236d9e-bcad-11ef-8bcb-028d36469a89 | a19e9947-1dfd-44a8-97f7-7b6053df0610 | langley-willowbrook | Langley - Willowbrook | British Columbia | LAN6K8 | langley-willowbrook | /cefa-find-a-school/langley-willowbrook |
| 812379b4-bcad-11ef-8bcb-028d36469a89 | 812379b4-bcad-11ef-8bcb-028d36469a89 | 9a3964c0-afae-4601-a997-48d7bc44fdd4 | markham-esna-park | Markham - Esna Park | Ontario | MAR1E1 | markham-esna-park | /cefa-find-a-school/markham-esna-park |
| 81236c7d-bcad-11ef-8bcb-028d36469a89 | 81236c7d-bcad-11ef-8bcb-028d36469a89 | bbca6924-f9a1-4598-bc36-2aa4ca74b41b | meadowtown | Meadowtown | British Columbia | PIT2W1 | meadowtown | /cefa-find-a-school/meadowtown |
| 81237b00-bcad-11ef-8bcb-028d36469a89 | 81237b00-bcad-11ef-8bcb-028d36469a89 | 25f1b58b-24e5-444a-ac71-41b6e1ebaf91 | mississauga-meadowvale | Mississauga - Meadowvale | Ontario | MIS7K2 | mississauga-meadowvale | /cefa-find-a-school/mississauga-meadowvale |
| 812369ba-bcad-11ef-8bcb-028d36469a89 | 812369ba-bcad-11ef-8bcb-028d36469a89 | b091070e-cdd9-4c2a-a7e8-d81a81502d7a | nanaimo | Nanaimo | British Columbia | NAN1H1 | nanaimo | /cefa-find-a-school/nanaimo |
| 8123677c-bcad-11ef-8bcb-028d36469a89 | 8123677c-bcad-11ef-8bcb-028d36469a89 | new-westminster-downtown | new-westminster-downtown | New Westminster Downtown | British Columbia | NEW1E6 | new-westminster-downtown | /cefa-find-a-school/new-westminster-downtown |
| 8123680a-bcad-11ef-8bcb-028d36469a89 | 8123680a-bcad-11ef-8bcb-028d36469a89 | 688ce197-963f-4279-855d-894164f907d9 | new-westminster-uptown | New Westminster Uptown | British Columbia | NEW3C2 | new-westminster-uptown | /cefa-find-a-school/new-westminster-uptown |
| 81236e59-bcad-11ef-8bcb-028d36469a89 | 81236e59-bcad-11ef-8bcb-028d36469a89 | 1df3a9bf-56a8-4daa-ba8b-5c878bc6381b | north-vancouver-capilano-mall | North Vancouver - Capilano Mall | British Columbia | pending | north-vancouver-capilano-mall | /cefa-find-a-school/north-vancouver-capilano-mall |
| 81236f34-bcad-11ef-8bcb-028d36469a89 | 81236f34-bcad-11ef-8bcb-028d36469a89 | f232fc62-9ef3-4b56-b90a-99a9f8e3063b | north-vancouver-lions-gate | North Vancouver - Lions Gate | British Columbia | NOR3B5 | north-vancouver-lions-gate | /cefa-find-a-school/north-vancouver-lions-gate |
| 81237525-bcad-11ef-8bcb-028d36469a89 | 81237525-bcad-11ef-8bcb-028d36469a89 | ac405242-b53b-4ee3-900d-688fa7b17e93 | oakville-eighth-line | Oakville - Eighth Line | Ontario | OAK2H1 | oakville-eighth-line | /cefa-find-a-school/oakville-eighth-line |
| 81237a11-bcad-11ef-8bcb-028d36469a89 | 81237a11-bcad-11ef-8bcb-028d36469a89 | a81ad611-c02a-488b-a953-c9c71654bf74 | okotoks | Okotoks - Darcy Crossing | Alberta | OKO7E4 | okotoks-darcy-crossing | /cefa-find-a-school/okotoks-darcy-crossing |
| 81237350-bcad-11ef-8bcb-028d36469a89 | 81237350-bcad-11ef-8bcb-028d36469a89 | richmond---crestwood | richmond-crestwood | Richmond - Crestwood | British Columbia | RIC2X8 | richmond-crestwood | /cefa-find-a-school/richmond-crestwood |
| 812373ae-bcad-11ef-8bcb-028d36469a89 | 812373ae-bcad-11ef-8bcb-028d36469a89 | c0be0646-6f88-4fb5-8e42-8d174e1edbcb | richmond-jacombs | Richmond - Jacombs | British Columbia | RIC1Z6 | richmond-jacombs | /cefa-find-a-school/richmond-jacombs |
| 812371ce-bcad-11ef-8bcb-028d36469a89 | 812371ce-bcad-11ef-8bcb-028d36469a89 | 48b6c89a-a899-4090-a50c-2f7a9c023b1b | richmond-south | Richmond - South | British Columbia | RIC2Z5 | richmond-south | /cefa-find-a-school/richmond-south |
| 81236c1d-bcad-11ef-8bcb-028d36469a89 | 81236c1d-bcad-11ef-8bcb-028d36469a89 | 88dd6ce1-2b52-4ea1-a8dd-a8bf85a83351 | south-delta | South Delta | British Columbia | DEL0B1 | south-delta | /cefa-find-a-school/south-delta |
| 8123687f-bcad-11ef-8bcb-028d36469a89 | 8123687f-bcad-11ef-8bcb-028d36469a89 | morgan-crossing | morgan-crossing | South Surrey - Morgan Crossing | British Columbia | SOU1H4 | south-surrey-morgan-crossing | /cefa-find-a-school/south-surrey-morgan-crossing |
| 81237712-bcad-11ef-8bcb-028d36469a89 | 81237712-bcad-11ef-8bcb-028d36469a89 | 13b83ca2-6170-4974-b2b9-c6be048bca24 | morgan-crossing-east-campus | South Surrey - Morgan Crossing East | British Columbia | SOU0R7 | south-surrey-morgan-crossing-east | /cefa-find-a-school/south-surrey-morgan-crossing-east |
| 81237895-bcad-11ef-8bcb-028d36469a89 | 81237895-bcad-11ef-8bcb-028d36469a89 | f28d673f-b2a2-4ea9-be5d-c9f40449a53f | surrey-campbell-heights | Surrey - Campbell Heights | British Columbia | SUR9V2 | surrey-campbell-heights | /cefa-find-a-school/surrey-campbell-heights |
| 81237777-bcad-11ef-8bcb-028d36469a89 | 81237777-bcad-11ef-8bcb-028d36469a89 | surrey-cloverdale | surrey-cloverdale | Surrey - Cloverdale | British Columbia | SUR2X6 | surrey-cloverdale | /cefa-find-a-school/surrey-cloverdale |
| 81236bbe-bcad-11ef-8bcb-028d36469a89 | 81236bbe-bcad-11ef-8bcb-028d36469a89 | 2836e555-33cb-4fe8-9b7f-e3deee1721d0 | surrey-fleetwood | Surrey - Fleetwood | British Columbia | SUR0G3 | surrey-fleetwood | /cefa-find-a-school/surrey-fleetwood |
| 8123722e-bcad-11ef-8bcb-028d36469a89 | 8123722e-bcad-11ef-8bcb-028d36469a89 | bb573368-3b35-43a6-84d2-0708944d6894 | guildford | Surrey - Guildford | British Columbia | SUR1J7 | surrey-guildford | /cefa-find-a-school/surrey-guildford |
| 81236a20-bcad-11ef-8bcb-028d36469a89 | 81236a20-bcad-11ef-8bcb-028d36469a89 | 09537acf-19b4-4d0e-8645-b51aaa009ba8 | surrey-nordel | Surrey - Nordel | British Columbia | SUR0C9 | surrey-nordel | /cefa-find-a-school/surrey-nordel |
| 81236a85-bcad-11ef-8bcb-028d36469a89 | 81236a85-bcad-11ef-8bcb-028d36469a89 | 9fa97dba-6ef6-4ccf-b84e-d3a716db3591 | south-surrey-panorama | Surrey - Panorama | British Columbia | SOU5J9 | surrey-panorama | /cefa-find-a-school/surrey-panorama |
| c77db124-f089-4d39-932a-343c1508fd75 | c77db124-f089-4d39-932a-343c1508fd75 | surrey---panorama-north | surrey-panorama-north | Surrey - Panorama North | British Columbia | SUR0Y6 | surrey-panorama-north | /cefa-find-a-school/surrey-panorama-north |
| 81237465-bcad-11ef-8bcb-028d36469a89 | 81237465-bcad-11ef-8bcb-028d36469a89 | sullivan-ridge | sullivan-ridge | Surrey - Sullivan Ridge | British Columbia | SUR1G8 | surrey-sullivan-ridge | /cefa-find-a-school/surrey-sullivan-ridge |
| 59258c9a-c5eb-42b7-9059-aea9a326f479 | 59258c9a-c5eb-42b7-9059-aea9a326f479 | 85667235-fa90-4145-a8c5-112840606654 | surrey-sunnyside | Surrey - Sunnyside | British Columbia | pending | surrey-sunnyside | /cefa-find-a-school/surrey-sunnyside |
| 81237956-bcad-11ef-8bcb-028d36469a89 | 81237956-bcad-11ef-8bcb-028d36469a89 | d6b79883-f1d9-41a0-bfa2-3e44ee0b8560 | vancouver-ubc | UBC | British Columbia | VAN2C5 | ubc | /cefa-find-a-school/ubc |
| 81237290-bcad-11ef-8bcb-028d36469a89 | 81237290-bcad-11ef-8bcb-028d36469a89 | 7a40e5a2-19e1-482b-a294-da63bb1ba7dd | vancouver-cambie | Vancouver - Cambie | British Columbia | VAN4V1 | vancouver-cambie | /cefa-find-a-school/vancouver-cambie |
| 812372f3-bcad-11ef-8bcb-028d36469a89 | 812372f3-bcad-11ef-8bcb-028d36469a89 | vancouver-commercial-drive | vancouver-commercial-drive | Vancouver - Commercial Drive | British Columbia | VAN4C9 | vancouver-commercial-drive | /cefa-find-a-school/vancouver-commercial-drive |
| 81237172-bcad-11ef-8bcb-028d36469a89 | 81237172-bcad-11ef-8bcb-028d36469a89 | 616c94b9-5cb2-489e-9b2f-79dbea3989a6 | vancouver-kitsilano | Vancouver - Kitsilano | British Columbia | VAN1Z6 | vancouver-kitsilano | /cefa-find-a-school/vancouver-kitsilano |
| 812374c6-bcad-11ef-8bcb-028d36469a89 | 812374c6-bcad-11ef-8bcb-028d36469a89 | victoria---douglas | victoria-douglas | Victoria - Douglas | British Columbia | VIC3K8 | victoria-douglas | /cefa-find-a-school/victoria-douglas |
| e5a64523-1163-4b24-9b00-4cd79eabdc7e | e5a64523-1163-4b24-9b00-4cd79eabdc7e | 3c78a5fc-e4a5-41d8-bd19-b1e446eff2b8 | victoria-university-heights | Victoria - University Heights | British Columbia | VIC6J1 | victoria-university-heights | /cefa-find-a-school/victoria-university-heights |
| 81236b5e-bcad-11ef-8bcb-028d36469a89 | 81236b5e-bcad-11ef-8bcb-028d36469a89 | 0e449353-5881-4e20-9286-04f2c66e9dd3 | victoria-westshore | Victoria - Westshore | British Columbia | VIC0X1 | victoria-westshore | /cefa-find-a-school/victoria-westshore |
| 812375f3-bcad-11ef-8bcb-028d36469a89 | 812375f3-bcad-11ef-8bcb-028d36469a89 | c786d4fe-070f-4429-92a1-32a9be32b442 | west-vancouver-park-royal | West Vancouver - Park Royal | British Columbia | WES2W4 | west-vancouver-park-royal | /cefa-find-a-school/west-vancouver-park-royal |
| 812378f2-bcad-11ef-8bcb-028d36469a89 | 812378f2-bcad-11ef-8bcb-028d36469a89 | 65c043e4-5b3b-4a54-a8b3-124af56be561 | white-rock | White Rock | British Columbia | WHI0C6 | white-rock | /cefa-find-a-school/white-rock |

## Known Program Table

Source: recent live GA4 BigQuery `generate_lead` rows where `tracking_source=helper_plugin`, backed by the Form 4 contract where `32.2=program_id` and `32.7=program_name`.

| program_id | program_name | program_key | aliases | recent_helper_events |
|---|---|---|---|---:|
| 2030 | Waitlist | waitlist | Waitlist | 6 |
| 411 | CEFA Baby | baby | Baby; CEFA Baby | 60 |
| 475 | Junior Kindergarten 1 | jk1 | JK1; Junior Kindergarten 1 | 18 |
| 478 | Junior Kindergarten 2 | jk2 | JK2; Junior Kindergarten 2 | 7 |
| 482 | Junior Kindergarten 3 | jk3 | JK3; Junior Kindergarten 3 | 5 |
| 486 | CEFA Weekend Care Program | weekend_care | Weekend Care; CEFA Weekend Care; CEFA Weekend Care Program | 1 |

## Canonical Location ID Normalization Worklist

These rows have a current `canonical_location_id`, but it is slug-like rather than UUID-like. They are not missing IDs. They are rows that should be normalized or explicitly approved as slug-key rows before `canonical_location_id` becomes the main cross-system join key.

| school_uuid | location_name | current_canonical_location_id | location_code | school_slug | recommended_status |
|---|---|---|---|---|---|
| 81236ff4-bcad-11ef-8bcb-028d36469a89 | Burnaby - Brentwood | burnaby-brentwood | burnaby-brentwood | burnaby-brentwood | needs normalization decision |
| 81237055-bcad-11ef-8bcb-028d36469a89 | Burnaby - Canada Way | burnaby-canada-way | burnaby-canada-way | burnaby-canada-way | needs normalization decision |
| 8123764f-bcad-11ef-8bcb-028d36469a89 | Calgary - Beacon Hill | calgary-beacon-hill | calgary-beacon-hill | calgary-beacon-hill | needs normalization decision |
| 812368e9-bcad-11ef-8bcb-028d36469a89 | Calgary - South | calgary-south | calgary-south | calgary-south | needs normalization decision |
| 81237582-bcad-11ef-8bcb-028d36469a89 | Delta - Captains Cove | delta-captain-s-cove | delta-captain-s-cove | delta-captains-cove | needs normalization decision |
| 8123677c-bcad-11ef-8bcb-028d36469a89 | New Westminster Downtown | new-westminster-downtown | new-westminster-downtown | new-westminster-downtown | needs normalization decision |
| 81237350-bcad-11ef-8bcb-028d36469a89 | Richmond - Crestwood | richmond---crestwood | richmond-crestwood | richmond-crestwood | needs normalization decision |
| 8123687f-bcad-11ef-8bcb-028d36469a89 | South Surrey - Morgan Crossing | morgan-crossing | morgan-crossing | south-surrey-morgan-crossing | needs normalization decision |
| 81237777-bcad-11ef-8bcb-028d36469a89 | Surrey - Cloverdale | surrey-cloverdale | surrey-cloverdale | surrey-cloverdale | needs normalization decision |
| c77db124-f089-4d39-932a-343c1508fd75 | Surrey - Panorama North | surrey---panorama-north | surrey-panorama-north | surrey-panorama-north | needs normalization decision |
| 81237465-bcad-11ef-8bcb-028d36469a89 | Surrey - Sullivan Ridge | sullivan-ridge | sullivan-ridge | surrey-sullivan-ridge | needs normalization decision |
| 812372f3-bcad-11ef-8bcb-028d36469a89 | Vancouver - Commercial Drive | vancouver-commercial-drive | vancouver-commercial-drive | vancouver-commercial-drive | needs normalization decision |
| 812374c6-bcad-11ef-8bcb-028d36469a89 | Victoria - Douglas | victoria---douglas | victoria-douglas | victoria-douglas | needs normalization decision |

## Known Gaps

- WordPress School Manager internal IDs are not yet mapped into this table.
- `canonical_location_id` is complete but mixed-format: 40 UUID-like rows and 13 slug-like rows in the checked warehouse table.
- GreenRope, GBP, Gravity location ID, and PiinPoint values were not available as populated rows in the checked BigQuery surfaces.
- School-level ad naming tokens are not complete. Do not infer them from labels without naming-convention confirmation.
- CRM/KinderTales program journey codes are not mapped yet.
- Some school labels differ slightly across systems, so `school_uuid` should remain the join key.

## School Code Gaps From CEFA Ops Map

These schools are present in the warehouse table but have no `school_code` value in the checked CEFA Ops School Identity Map:

- Calgary - South
- North Vancouver - Capilano Mall
- Surrey - Sunnyside

## Maintenance Rule

When a missing external ID is confirmed, update this file and the taxonomy status note in the same commit. Do not overwrite known IDs from labels or campaign names alone.
