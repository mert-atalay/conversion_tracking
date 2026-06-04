# Codex Machine Migration Checklist - 2026-06-04

Status: `Verified` for local path inspection on 2026-06-04. Status is `Partial` for credential validity because secrets and OAuth tokens must be re-tested on the new Mac after restore.

## Purpose

This checklist records what must be carried to a new computer before formatting the current Mac so Codex can continue CEFA measurement, naming, conversion tracking, paid-media, SEO, BigQuery, Google Workspace, Meta, n8n, and MCP work without losing context.

Do not commit secrets, tokens, passcodes, private keys, OAuth files, keychains, `.env` files, or service-account JSON files into this repo. This file lists locations and verification steps only.

## Current Canonical GitHub Repo

Status: `Verified`

| Item | Value |
|---|---|
| GitHub repo | `mert-atalay/conversion_tracking` |
| URL | `https://github.com/mert-atalay/conversion_tracking` |
| Canonical branch | `main` |
| Local path on old Mac | `/Users/matthewbison/Desktop/cefa-nexus/conversion_tracking` |
| Snapshot tag | `cefa-measurement-docs-2026-06-03` |

On the new Mac, clone or pull this repo first:

```bash
git clone https://github.com/mert-atalay/conversion_tracking.git
cd conversion_tracking
git checkout main
```

## Existing Migration Copy

Status: `Verified`

The browsable migration copy is here:

```text
/Users/matthewbison/Desktop/codex-migration-browsable-copy-20260603-185115
```

Visible entry folder:

```text
/Users/matthewbison/Desktop/codex-migration-browsable-copy-20260603-185115/OPEN_ME_VISIBLE_LINKS
```

Important warning from the bundle: it is unencrypted and can contain API keys, OAuth state, SSH keys, keychains, passcodes, `.env` files, and other sensitive files. Treat it like a password vault. Do not upload it to normal cloud storage.

Included visible links:

| Visible link | Target | Use |
|---|---|---|
| `codex-config-memory` | `home/.codex` | Codex config, plugins, memory, MCP server config, auth state, skills, vendors |
| `agent-skills` | `home/.agents` | Shared agent skills |
| `developer-configs` | `home/.config` | gcloud, gws, GitHub CLI, Google Ads, Supermetrics and other developer auth/config |
| `ssh-keys` | `home/.ssh` | SSH keys and known hosts |
| `keychains` | `home/Library/Keychains` | macOS keychains |
| `desktop-workspaces` | `home/Desktop` | Desktop workspaces and project folders |
| `cefa-ops-sources` | `home/Desktop/CEFA Ops Sources` | CEFA source files and exports |
| `obsidian-vaults` | `home/Vaults` | Obsidian vaults |

Manifests already present in the bundle:

| Manifest | Use |
|---|---|
| `manifests/copied-paths.txt` | Exact copied path list |
| `manifests/include-paths.txt` | Intended include list |
| `manifests/codex-mcp-list-redacted.txt` | Redacted MCP list |
| `manifests/env-key-inventory-redacted.txt` | Redacted env key inventory |
| `manifests/all-env-files-included.txt` | Env files included in the copy |
| `manifests/size.txt` | Bundle size |

## Must Carry Before Formatting

Status: `Verified`

Carry these as a private transfer, not through public GitHub:

| Priority | Location | Why it matters |
|---|---|---|
| Critical | `/Users/matthewbison/.codex` | Codex config, auth state, plugins, memory, MCP config, vendors, skills, state DBs |
| Critical | `/Users/matthewbison/.codex/memories` | Codex long-term memory summaries and rollout summaries |
| Critical | `/Users/matthewbison/.codex/memory` | local memory JSONL and Memora database |
| Critical | `/Users/matthewbison/.codex/config.toml` | MCP servers, plugins, trusted projects |
| Critical | `/Users/matthewbison/.config/gcloud` | Google Cloud auth/configs including `cefa-bq-sticky` and `personal-gws` |
| Critical | `/Users/matthewbison/.config/gws` | Personal Google Workspace CLI auth and encrypted credentials |
| Critical | `/Users/matthewbison/.config/gh` | GitHub CLI auth |
| Critical | `/Users/matthewbison/.config/google-ads.yaml` | Google Ads API client config |
| Critical | `/Users/matthewbison/.config/codex/google-sheets-service-account.json` | Google Sheets/BigQuery service account used by local tools |
| Critical | `/Users/matthewbison/.ssh` | Git/SSH access |
| Critical | `/Users/matthewbison/Library/Keychains` | macOS-stored secrets/OAuth support |
| Critical | `/Users/matthewbison/Desktop/cefa-nexus` | CEFA NEXUS repo, `conversion_tracking`, agents, artifacts, Meta CLI, MCP helpers |
| Critical | `/Users/matthewbison/Desktop/agentic-brain` | Reporting/dashboard and Supermetrics/BQ workflow code |
| High | `/Users/matthewbison/Desktop/Nova` | WordPress/Nova tooling and MCP scripts |
| High | `/Users/matthewbison/Desktop/cefa-newwebsite-franchise` | Franchise-site local tooling/artifacts |
| High | `/Users/matthewbison/Desktop/chatbot` | Owly/chatbot work |
| High | `/Users/matthewbison/Desktop/CEFA Store` | Shopify store work |
| High | `/Users/matthewbison/Desktop/web design` | Agency/design project work |
| High | `/Users/matthewbison/Desktop/CEFA Ops Sources` | CEFA source exports, spreadsheets, screenshots, reference packs |
| High | `/Users/matthewbison/Vaults` | Obsidian vaults |

## Likely Gaps In Current Migration Copy

Status: `Partial`

The existing migration manifest does not clearly list these n8n/local-service paths. Copy them separately if you still need local n8n workflows and MCP integration:

| Location | Why it matters |
|---|---|
| `/Users/matthewbison/.n8n` | Local n8n user state, DB/config, credentials depending on setup |
| `/Users/matthewbison/.n8n-mcp` | n8n MCP state/config if used |
| `/Users/matthewbison/.codex/secrets/cefa-n8n.env` | Local n8n environment values |
| `/Users/matthewbison/.codex/secrets/cefa-n8n-mcp.env` | n8n MCP environment values |
| `/Users/matthewbison/.codex/state/cefa-n8n` | Local Codex/n8n state |
| `/Users/matthewbison/.codex/vendor/cefa-n8n-stack` | Local n8n stack/vendor files |
| `/Users/matthewbison/.codex/bin/start-cefa-n8n-local.sh` | Local startup script |
| `/Users/matthewbison/Library/LaunchAgents/com.cefa.n8n.local.plist` | macOS launch agent for local n8n |
| `/Users/matthewbison/Desktop/n8n-sharepoint-poc` | n8n/SharePoint proof-of-concept workspace |

Also verify cloud-synced files after signing in, especially:

| Cloud/synced item | Why |
|---|---|
| OneDrive/SharePoint CEFA budget workbook | Required for budget/reference workflows; local path may change after reinstall |
| Google Drive sheets/docs | Naming convention v21 sheet and other CEFA planning sheets live in Google Drive |
| Canva/Figma/Asana/SharePoint connectors | Plugin OAuth state may require reconnect even if config files are copied |

## Active MCP Servers To Recreate Or Verify

Status: `Verified` for configured names, `Partial` for post-migration auth.

Configured MCP servers found in `~/.codex/config.toml`:

```text
dataforseo
shadcn
shopify-dev-mcp
linear
google-sheets
ga4
gsc
gtm
playwright
chrome-devtools
meta_ads_official
composio_meta
marketing
bigquery_toolbox
memora
wordpress-studio
gcloud
gcloud_observability
gcloud_storage
supabase
supermetrics
composio
node_repl
```

Important bearer/OAuth/token-backed services to verify on the new Mac:

| Service | Config surface |
|---|---|
| DataForSEO | `~/.codex/config.toml` env values |
| Linear | `LINEAR_MCP_TOKEN` |
| Composio Meta | Composio URL/header config |
| Supabase MCP | `SUPABASE_MANAGEMENT_ACCESS_TOKEN` |
| Supermetrics MCP | `SUPERMETRICS_API_KEY` |
| BigQuery / Google Cloud | `~/.config/gcloud`, `~/.config/codex/google-sheets-service-account.json` |
| GA4/GSC MCP | CEFA `tools/mcp/.env.local` and Google OAuth files |
| Meta CLI | CEFA `tools/meta/.env.local` |
| GitHub CLI | `~/.config/gh` |
| Personal Google Workspace CLI | `~/.config/gws` and `personal-gws` gcloud config |

Do not paste the actual values into this repo.

## Active Plugins To Re-enable

Status: `Verified` for configured plugin names.

Configured Codex plugins include:

```text
canva
github
gmail
google-drive
hugging-face
vercel
game-studio
build-web-apps
superpowers
outlook-email
google-calendar
coderabbit
plugin-eval
remotion
jam
figma
documents
spreadsheets
presentations
ultimate-wordpress-developer
neon-postgres
supabase
openai-developers
codex-security
sharepoint
asana
latex
zoom
cefa-aeo-seo-toolkit
browser
chrome
```

Expect some OAuth plugins to require reconnect on the new Mac even if the local config was copied.

## CEFA-Specific Local Workspaces

Status: `Verified`

These are the main workspaces Codex has used for CEFA work:

| Workspace | Role |
|---|---|
| `/Users/matthewbison/Desktop/cefa-nexus/conversion_tracking` | Canonical GitHub repo for CEFA measurement/tracking docs and plugin |
| `/Users/matthewbison/Desktop/cefa-nexus/CEFA` | CEFA NEXUS agents, paid-media tools, Meta CLI, MCP helpers, artifacts |
| `/Users/matthewbison/Desktop/agentic-brain` | Reporting, dashboard, Supermetrics/BQ reconciliation work |
| `/Users/matthewbison/Desktop/Nova` | WordPress/Nova tooling |
| `/Users/matthewbison/Desktop/cefa-newwebsite-franchise` | Franchise website local tooling |
| `/Users/matthewbison/Desktop/chatbot` | Owly/chatbot work |
| `/Users/matthewbison/Desktop/CEFA Store` | Shopify work |
| `/Users/matthewbison/Desktop/web design` | Agency/design work |

For CEFA naming/conversion tracking specifically, the GitHub repo is now enough for the canonical docs, but the local CEFA NEXUS workspace still contains useful agents, skills, artifacts, and CLIs.

## New Mac Verification Commands

Status: `Recommended`

Run these after copying files and installing Codex/CLIs:

```bash
codex mcp list
gh auth status
gcloud config configurations list
CLOUDSDK_ACTIVE_CONFIG_NAME=personal-gws gcloud config get-value account
gws auth status
shopify version
```

Then verify CEFA repo and tools:

```bash
cd /Users/matthewbison/Desktop/cefa-nexus/conversion_tracking
git status -sb
git remote -v
git branch --show-current
```

```bash
cd /Users/matthewbison/Desktop/cefa-nexus/CEFA
tools/meta/cefa-meta doctor
tools/meta/cefa-meta accounts --live
tools/meta/cefa-meta campaigns --account parent --limit 5
```

For Google and BigQuery:

```bash
CLOUDSDK_ACTIVE_CONFIG_NAME=cefa-bq-sticky gcloud auth list
CLOUDSDK_ACTIVE_CONFIG_NAME=cefa-bq-sticky gcloud config get-value project
```

For n8n if carried:

```bash
ls -la ~/.n8n ~/.n8n-mcp ~/.codex/secrets/cefa-n8n.env ~/.codex/secrets/cefa-n8n-mcp.env
```

## Red Flags Before Formatting

Status: `Recommended`

Do not format until all are true:

- The migration bundle is copied to an external drive or other private encrypted storage.
- `~/.codex`, `~/.config/gcloud`, `~/.config/gws`, `~/.config/gh`, `~/.ssh`, and keychains are included.
- `~/.codex/memories`, `~/.codex/memory`, and Memora `memories.db` are included.
- CEFA local workspaces are either copied or pushed to GitHub where appropriate.
- n8n local state is copied separately if you want local workflows preserved.
- OneDrive/SharePoint and Google Drive files are confirmed accessible from cloud accounts.
- You know which secrets must be re-entered or reconnected if copied OAuth state fails.

## What Not To Put In GitHub

Status: `Verified`

Never commit these:

- `.env` files with real values;
- OAuth credential files;
- service-account JSON files;
- `~/.ssh`;
- macOS keychains;
- `.codex/auth.json`;
- `~/.config/gcloud/credentials.db`;
- `~/.config/gws/credentials.enc`;
- Meta access tokens;
- Supermetrics API keys;
- Supabase management tokens;
- Google Ads developer/client secrets;
- n8n credentials or encryption keys.

Keep GitHub for durable non-secret rules, indexes, docs, and code only.
