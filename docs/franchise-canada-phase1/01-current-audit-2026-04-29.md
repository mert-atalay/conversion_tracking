# Franchise Canada Current Audit

Last updated: 2026-04-29

## Verified Access

WordPress staging MCP/API access is available for:

- `https://cefafranchise.kinsta.cloud`
- MCP server: `wordpress_franchise_http`
- MCP abilities discovered through the adapter include `cefa-franchise/gravity-forms-list`, `cefa-franchise/gravity-form-get`, `cefa-franchise/database-query`, `cefa-franchise/plugin-list`, content reads, and file reads/writes.

GTM access is available for:

- GTM account `6004334435`
- Canada franchise container `48104535`
- Public ID `GTM-TPJGHFS`
- Workspace `48` / `Default Workspace`

GA4 Admin MCP access is available for:

- Property `259747921` / `CEFA Franchise`
- Google Ads link customer `3820636025`

## Current GTM State

Current/live Canada franchise container:

- Account: `6004334435`
- Container: `48104535`
- Public ID: `GTM-TPJGHFS`
- Name: `franchise.cefa.ca`
- Workspace: `48`
- Live version in prior authenticated audit: `47`

Live-version object counts from the existing authenticated audit:

- Tags: `54`
- Triggers: `20`
- Variables: `44`
- Folders: `11`
- Built-in variables: `39`
- Custom templates: `2`

Published container string check from `gtm.js`:

- GA4 measurement ID present: `G-6EMKPZD7RD`
- Google Ads IDs present: `AW-11088792613`, `AW-802334988`
- Meta pixel candidate present: `918227085392601`
- Strings present: `generate_lead`, `form_submit`, `Lead`, `franchise`, `thank`, `hostname`, `page_hostname`

Important: new Canada staging currently also loads `GTM-TPJGHFS`. That means any new GTM work in this container must be hostname-scoped until production cutover is controlled.

## Old Canada GTM Logic Found

The prior authenticated audit shows old Canada triggers such as:

- `Fr Application Submit_ollo`
  - Type: pageview
  - Filter: Page URL contains `franchise.cefa.ca/thank-you`
- `Franchisor_FB_Site Form Submit_ollo`
  - Type: pageview
  - Filter: Page URL contains `submit-site-thank-you`
- `Fr Inquiry Submit (own a cefa)_ollo`
  - Type: form submission
  - Filters include old path `own-a-cefa` and Elementor form classes.
- `Fr Submit a Site_ollo`
  - Type: form submission
  - Filters include old path `submit-a-site` and Elementor form classes.
- `Fr Inquiry Click_ollo`
  - Type: link click
  - Filter: Click URL matches `submit-a-site|own-a-cefa`
- `Fr Phone Click_ollo`
  - Type: link click
  - Filter: Click URL contains `tel:`
- `Fr Email Click_ollo`
  - Type: link click
  - Filter: Click URL contains `mailto`

Interpretation:

- The old container is useful for IDs and legacy intent examples.
- It should not be copied as-is into the new staging build.
- Old Elementor form-submit triggers do not match the new Gravity Forms runtime.
- Old thank-you path triggers are not sufficient for the final confirmed-success contract.

## New Staging Site Structure

Staging homepage:

- URL: `https://cefafranchise.kinsta.cloud/`
- GTM installed: `GTM-TPJGHFS`
- Public page source does not show form markup on the homepage.
- Public page source did not contain direct `dataLayer.push` tracking events.

Staging sitemap page inventory includes:

- `/`
- `/available-opportunities/`
- `/available-opportunities/franchising-inquiry/`
- `/available-opportunities/submit-an-inquiry-not-available/`
- `/partner-with-cefa/`
- `/partner-with-cefa/franchise-partners/`
- `/partner-with-cefa/our-process/`
- `/partner-with-cefa/real-estate-partners/`
- `/partner-with-cefa/real-estate-partners/submit-a-site/`
- `/about-cefa/`
- `/about-cefa/why-cefa/`
- `/resource-hub/`
- `/resource-hub/faqs/`
- `/contact-us/`
- `/privacy-policy/`
- `/terms-of-use/`
- `/cookie-settings/`

Additional published pages found through WordPress:

- `Submit an Inquiry - Thank You` / page ID `633`
- `Submit a Site - Thank You` / page ID `636`

## New Staging Form Runtime

Form pages checked publicly:

- `/available-opportunities/franchising-inquiry/`
  - Contains Gravity Forms Form `1`
  - Submit button ID: `gform_submit_button_1`
  - Form ID: `gform_1`
- `/partner-with-cefa/real-estate-partners/submit-a-site/`
  - Contains Gravity Forms Form `2`
  - Submit button ID: `gform_submit_button_2`
  - Form ID: `gform_2`
- `/partner-with-cefa/real-estate-partners/`
  - Also contains Gravity Forms Form `2`
- `/contact-us/`
  - No Gravity Form detected in public source.

No public-source `dataLayer.push` final events were detected on the checked staging pages.

## Gravity Forms Inventory

Active forms on Canada staging:

- Form `1`: `Franchise Inquiry`
- Form `2`: `Site Inquiry`
- Form `3`: `Newsletter`

### Form 1: Franchise Inquiry

Primary fields:

- `1`: First Name
- `3`: Last Name
- `4`: Phone
- `5`: Email
- `6`: Address
- `7`: Liquid cash / investment range
- `32`: custom `cefa_location_select` field, label `Where are you interested in opening a CEFA school?`
- `10`: opening timeline, conditionally shown when selected location is available
- `11`: eventual school count, conditionally shown when selected location is available
- `12`: sole shareholder vs partners/investors, conditionally shown when selected location is available
- `37`: consent, required and conditionally shown when selected location is available

Hidden attribution fields already present:

- `14`: `lc_source`
- `15`: `lc_medium`
- `16`: `lc_campaign`
- `17`: `lc_content`
- `18`: `lc_term`
- `19`: `lc_channel`
- `20`: `lc_landing`
- `21`: `lc_referrer`
- `22`: `fc_source`
- `23`: `fc_medium`
- `24`: `fc_campaign`
- `25`: `fc_content`
- `26`: `fc_term`
- `27`: `fc_channel`
- `28`: `fc_referrer`
- `29`: `gclid`
- `30`: `GA_Client_ID`

Confirmation:

- Type: page redirect
- Page ID: `633`
- Page title: `Submit an Inquiry - Thank You`

### Form 2: Site Inquiry

Primary fields:

- `1`: First Name
- `3`: Last Name
- `32`: Company Name
- `4`: Phone
- `5`: Email
- `39`: Site Offered By
- `34`: Property Square Footage
- `35`: Outdoor Space
- `6`: Site Address
- `36`: Availability
- `37`: Availability Details, conditionally shown
- `38`: Consent

Hidden attribution fields:

- `14` through `30` match Form 1 attribution field pattern.

Confirmation:

- Type: page redirect
- Page ID: `636`
- Page title: `Submit a Site - Thank You`

### Form 3: Newsletter

Fields:

- `1`: First Name
- `3`: Last Name
- `4`: Email

Confirmation:

- Type: message

## Current Gap

The new Canada staging site can be tracked with GTM clicks and thank-you pageviews, but that would not meet the final event identity plan. For final lead tracking, we still need one confirmed-success browser event per successful form submission, with a submission-scoped `event_id`, clean metadata, attribution fields, and duplicate/false-positive guards.

