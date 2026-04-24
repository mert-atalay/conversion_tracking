# Gravity Forms Google Analytics Add-On Decision

The Gravity Forms Google Analytics Add-On with Tag Manager connection type is allowed as a test path, but it is not accepted as the final source unless it outputs clean values.

## Add-On Can Do

- Create a feed for a specific form submission.
- Use a Tag Manager trigger name.
- Map event parameters from form fields.
- Fire/log a custom event such as `school_inquiry_submit`.

## Current Concern

The staging test showed the add-on can collapse custom compound field `32.*` values into one combined string.

Unacceptable output:

```text
school UUID | program ID | days | Event ID | school slug | school name | program name
```

This is unsafe for GTM because it requires parsing and can break event ID matching.

## Accept Add-On Only If

- One `school_inquiry_submit` fires after a real successful Form 4 submission.
- `event_id` equals `32.4`.
- `school_selected_id` equals `32.1`.
- `program_id` equals `32.2`.
- `days_per_week` equals `32.3`.
- `school_selected_slug` equals `32.5`.
- `school_selected_name` equals `32.6`.
- `program_name` equals `32.7`.
- Direct thank-you visits do not fire conversions.
- Reloads do not duplicate conversions.
- Failed validation does not fire conversions.
- No duplicate POC/helper event is mapped to platforms.

## Final Decision

The add-on is a convenience layer, not the truth layer.

Final signoff is based on observed browser `dataLayer` output and saved Gravity Forms entry matching.
