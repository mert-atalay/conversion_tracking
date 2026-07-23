# Form 4 Event Collector

Lightweight Cloud Run service for the CEFA Form 4 first-party event foundation.

The collector accepts only HMAC-signed `school_inquiry_submit` payloads for Form 4 and writes a no-PII audit row to:

`marketing-api-488017.raw_website_forms.form4_event_audit`

The WordPress plugin send path is disabled by default and should be enabled first on staging.

## Endpoint

- `POST /collect/form4`
- `GET /`

Required headers:

- `X-CEFA-Timestamp`: Unix timestamp in seconds.
- `X-CEFA-Signature`: `sha256=<hex hmac>` over `timestamp + "." + raw_body`.

## No-PII Rules

The collector rejects unsupported payload fields and stores only approved tracking fields:

- `event_id`
- form metadata
- school/program metadata
- UTM values and click IDs
- cleaned URL host/path without query string or fragment
- collector metadata

Do not send parent names, child names, email, phone, address, DOB, notes, IP address, or raw user agent.

`test_mode: true` is supported for signed collector verification. Test rows remain in raw/staging audit tables and are excluded from the business daily mart.
