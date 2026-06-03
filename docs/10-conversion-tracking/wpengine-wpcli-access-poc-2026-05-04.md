# WP Engine WP-CLI Access POC

Last updated: 2026-05-04

## Purpose

Verify that each live CEFA website has its own WP Engine SSH/WP-CLI access path and that the access is sufficient for future controlled plugin operations.

This POC did not update, install, activate, deactivate, or delete any WordPress plugin. It only ran read checks plus reversible transient and temporary plugin-directory file write/delete checks.

## Access Boundary

Each website must use its own SSH target, install path, and WP-CLI user. Do not reuse the parent access target for franchise sites.

| Website | SSH target | WP path | WP-CLI user | Verified siteurl |
|---|---|---|---:|---|
| Parent `cefa.ca` | `cefaweb@cefaweb.ssh.wpengine.net` | `/home/wpe-user/sites/cefaweb` | `8` | `https://cefa.ca` |
| Franchise Canada `franchise.cefa.ca` | `cefafranchise2@cefafranchise2.ssh.wpengine.net` | `/home/wpe-user/sites/cefafranchise2` | `7` | `https://franchise.cefa.ca` |
| Franchise USA `franchisecefa.com` | `franchisecefa1@franchisecefa1.ssh.wpengine.net` | `/home/wpe-user/sites/franchisecefa1` | `7` | `https://franchisecefa.com` |

Shared local key:

```bash
~/.ssh/wpengine_cefastaging_ed25519
```

Recommended SSH options:

```bash
-i ~/.ssh/wpengine_cefastaging_ed25519 -o IdentitiesOnly=yes -o BatchMode=yes -o StrictHostKeyChecking=accept-new
```

## Verified Capability Matrix

| Capability | Parent | Franchise Canada | Franchise USA |
|---|---|---|---|
| SSH login | Pass | Pass | Pass |
| Correct WP path reachable | Pass | Pass | Pass |
| WP-CLI available | Pass, `WP-CLI 2.12.0` | Pass, `WP-CLI 2.12.0` | Pass, `WP-CLI 2.12.0` |
| PHP CLI available | Pass, `PHP 8.4.19` | Pass, `PHP 8.4.19` | Pass, `PHP 8.4.19` |
| `wp option get siteurl` | Pass | Pass | Pass |
| `wp plugin list` | Pass | Pass | Pass with `--skip-update-check` recommended |
| `WP_PLUGIN_DIR` writable by WP-CLI context | Pass | Pass | Pass |
| Reversible transient write/read/delete | Pass | Pass | Pass |
| Reversible temp file write/delete in `wp-content/plugins` | Pass | Pass | Pass |

## Plugin Inventory Snapshot

### Parent `cefa.ca`

Relevant active plugins:

| Plugin | Status | Version |
|---|---|---:|
| `cefa-conversion-tracking` | active | Initially `0.4.1`; later updated to `0.4.3` on 2026-05-04 |
| `cefa-mcp-abilities` | active | `1.3.0` |
| `cefa-owly-chatbot` | active | `3.2.60` |
| `cefa-school-manager` | active | `1.0.18` |
| `gravityforms` | active | `2.10.1` |
| `mcp-adapter` | active | `0.5.0` |

Interpretation:

- Parent can be updated through WP Engine SSH/WP-CLI.
- The live parent conversion plugin was successfully updated to `0.4.3` later on 2026-05-04 using the parent target and `--user=8`.
- Future controlled parent plugin deployments can use the same parent target and `--user=8`.

### Franchise Canada `franchise.cefa.ca`

Relevant active plugins:

| Plugin | Status | Version |
|---|---|---:|
| `cefa-franchise-mcp-control` | active | `0.1.12` |
| `gravityforms` | active | `2.10.1` |
| `mcp-adapter` | active | `0.5.0` |

Interpretation:

- Franchise Canada can be managed through its own WP Engine SSH/WP-CLI target.
- Do not use the parent `cefaweb` target for Franchise Canada.
- Use `--user=7`.

### Franchise USA `franchisecefa.com`

Relevant active plugins:

| Plugin | Status | Version |
|---|---|---:|
| `cefa-franchise-mcp-control` | active | `0.1.13` |
| `gravityforms` | active | `2.10.1` |
| `gravityformsgoogleanalytics` | active | `2.4.1` |
| `mcp-adapter` | active | `0.5.0` |

Interpretation:

- Franchise USA can be managed through its own WP Engine SSH/WP-CLI target.
- Do not use the parent `cefaweb` or Canada `cefafranchise2` target for Franchise USA.
- Use `--user=7`.
- `wp plugin list --skip-update-check` is recommended for USA because the normal update-check path was slow.

## POC Commands Used

### Parent

```bash
ssh -i ~/.ssh/wpengine_cefastaging_ed25519 -o IdentitiesOnly=yes -o BatchMode=yes -o StrictHostKeyChecking=accept-new cefaweb@cefaweb.ssh.wpengine.net
cd /home/wpe-user/sites/cefaweb
wp --user=8 option get siteurl
wp --user=8 plugin list --fields=name,status,version,update --format=csv
wp --user=8 transient set cefa_wpcli_poc_20260504_parent ok 60
wp --user=8 transient get cefa_wpcli_poc_20260504_parent
wp --user=8 transient delete cefa_wpcli_poc_20260504_parent
```

### Franchise Canada

```bash
ssh -i ~/.ssh/wpengine_cefastaging_ed25519 -o IdentitiesOnly=yes -o BatchMode=yes -o StrictHostKeyChecking=accept-new cefafranchise2@cefafranchise2.ssh.wpengine.net
cd /home/wpe-user/sites/cefafranchise2
wp --user=7 option get siteurl
wp --user=7 plugin list --fields=name,status,version,update --format=csv
wp --user=7 transient set cefa_wpcli_poc_20260504_franchise_canada ok 60
wp --user=7 transient get cefa_wpcli_poc_20260504_franchise_canada
wp --user=7 transient delete cefa_wpcli_poc_20260504_franchise_canada
```

### Franchise USA

```bash
ssh -i ~/.ssh/wpengine_cefastaging_ed25519 -o IdentitiesOnly=yes -o BatchMode=yes -o StrictHostKeyChecking=accept-new franchisecefa1@franchisecefa1.ssh.wpengine.net
cd /home/wpe-user/sites/franchisecefa1
wp --user=7 option get siteurl
wp --user=7 plugin list --skip-update-check --fields=name,status,version --format=csv
wp --user=7 transient set cefa_wpcli_poc_20260504_franchise_usa_retry ok 60
wp --user=7 transient get cefa_wpcli_poc_20260504_franchise_usa_retry
wp --user=7 transient delete cefa_wpcli_poc_20260504_franchise_usa_retry
```

### Plugin Directory Write POC

This reversible file write/delete was run on each site:

```bash
printf 'ok' > wp-content/plugins/.cefa-wpcli-plugin-write-poc-20260504-<site>
cat wp-content/plugins/.cefa-wpcli-plugin-write-poc-20260504-<site>
rm wp-content/plugins/.cefa-wpcli-plugin-write-poc-20260504-<site>
test ! -e wp-content/plugins/.cefa-wpcli-plugin-write-poc-20260504-<site>
```

All three sites returned:

```text
PLUGIN_WRITE_POC_READ=ok
PLUGIN_WRITE_POC_DELETE=ok
```

## Future Plugin Deployment Pattern

Use this pattern only after explicit approval for the specific site.

### Parent Conversion Plugin Example

Local package currently prepared:

```bash
/Users/matthewbison/Desktop/cefa-conversion-tracking-0.4.3.zip
```

Controlled deployment pattern:

```bash
scp -i ~/.ssh/wpengine_cefastaging_ed25519 -o IdentitiesOnly=yes /Users/matthewbison/Desktop/cefa-conversion-tracking-0.4.3.zip cefaweb@cefaweb.ssh.wpengine.net:/tmp/cefa-conversion-tracking-0.4.3.zip

ssh -i ~/.ssh/wpengine_cefastaging_ed25519 -o IdentitiesOnly=yes cefaweb@cefaweb.ssh.wpengine.net
cd /home/wpe-user/sites/cefaweb
wp --user=8 plugin list --fields=name,status,version --format=csv | grep cefa-conversion-tracking
wp --user=8 plugin install /tmp/cefa-conversion-tracking-0.4.3.zip --force --activate
wp --user=8 plugin list --fields=name,status,version --format=csv | grep cefa-conversion-tracking
wp cache flush
```

Post-deploy parent validation must include:

- Confirm public HTML or asset URL shows `cefa-conversion-tracking.js?ver=0.4.3`.
- Submit one controlled Form 4 test.
- Confirm one `school_inquiry_submit` dataLayer event.
- Confirm Google Ads request uses `AW-802334988/cFt-CMrLufgCEIzSyv4C`.
- Confirm Form 4 `32.4` event ID does not equal the school UUID in `32.1`.

## Guardrails

- Do not run plugin deployment commands against the wrong SSH target.
- Do not update all three sites with one command; each site has its own target and WP-CLI user.
- Do not use `wp plugin update` for CEFA custom plugins unless the plugin is intentionally wired to an update source. For repo-built ZIPs, use `wp plugin install <zip> --force --activate`.
- Do not update franchise plugins while doing parent plugin work.
- Do not treat this SSH/WP-CLI path as a replacement for browser/GA4/GTM/Ads QA after deployment.
- Keep the Google Ads learning path unchanged: parent still maps to existing `Inquiry Submit_ollo`.
