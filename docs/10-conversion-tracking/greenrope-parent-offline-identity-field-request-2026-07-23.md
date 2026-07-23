# GreenRope Parent Offline Identity Field Request

**Requested:** 2026-07-23
**Scope:** Parent-school opportunities only

Please create these two GreenRope **opportunity custom fields** as Short Text
fields:

1. `cefa_event_id`
2. `cefa_form_entry_id`

Requirements:

- Preserve the field names exactly, including lowercase letters and
  underscores.
- Make both fields available through GreenRope's opportunity API for read and
  write.
- Do not add workflow, assignment, stage, email, or automation behavior to
  either field.
- Do not make either field required for staff-created opportunities.
- Confirm when the fields are visible in the opportunity field dictionary/API.

Purpose:

- `cefa_event_id` stores the existing CEFA event ID from Gravity Forms Form 4
  field `32.4`.
- `cefa_form_entry_id` stores the corresponding Gravity Forms entry ID.
- These opaque identifiers let CEFA connect a later CRM stage to exactly one
  website inquiry without sending parent identity into marketing tables.

CEFA will perform one controlled API write/read-back after the fields are
created. No existing GreenRope field, workflow, assignment, or opportunity
stage needs to be changed.
