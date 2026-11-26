---
name: flow-sync
description: >-
  Manual maintenance skill: audit the live Google Flow web app (https://flow.google.com)
  via Antigravity's built-in browser to detect new features, updated UI labels, model
  launches, credit changes, and deprecated/removed capabilities, then patch and prune
  this plugin's rules, skills, and references. Invoke only when explicitly triggered
  by the user (e.g., /flow-sync); never auto-invoke during normal creative workflows.
disable-model-invocation: true
---

# Flow Sync (Live UI Audit, Feature Calibration & Deprecation Pruning)

Keep the `antigravity-flow` plugin synchronized with the live **Google Flow** web application (`https://flow.google.com/?hl=en`) through a repeatable, zero-credit, strictly read-only inspection and patching loop.

## Core Principles

1. **Zero Credit Spend & Zero Mutations**: Every browser audit step is strictly read-only — never click `Start generation`, `Delete`, `Move to trash`, or paid `4K Upscaled` exports during a sync.
2. **Observe Before Editing**: Never guess Flow UI changes from memory or old blog posts. Ground every addition, rename, or deletion in live screenshots and DOM/accessibility observations from `https://flow.google.com/?hl=en`.
3. **Add New, Fix Drifted, Prune Obsolete**:
   - **Add** newly launched models, modes, tools, or workflows (creating a new skill if a major standalone capability emerges).
   - **Fix** renamed buttons, changed navigation paths, updated credit costs, and altered settings popovers.
   - **Prune** features, models (e.g., retired `Leaving <Date>` models), and controls that no longer exist in the live UI so agents never waste steps hunting for dead elements.
4. **English-Only Repository**: Keep all plugin source files (`plugin.json`, `README.md`, `rules/`, `skills/`, `references/`) strictly in English.

## Workflow

### Step 1: Load Baseline & Plugin Paths

1. Read [Audit Checklist](./references/audit-checklist.md) to get the last calibration date and the 7 canonical surfaces to inspect.
2. Locate the plugin source directory (resolve symlink from `~/.gemini/config/plugins/antigravity-flow` if editing from another workspace).

### Step 2: Run Strictly Read-Only Live Browser Audit

Delegate to the `browser` subagent (`Model: "flash"`, reusing any existing Flow `browser` subagent via `send_message`) at `https://flow.google.com/?hl=en` using the Fast-Path Authentication Check from `rules/AGENTS.md`. Enforce randomized `8-15s` pacing between route navigations, project reuse first (inspect an existing project rather than creating `+ New project`), and zero-retry (`retry_count = 0`) `PAUSED_*` stops if `ACCOUNT_VERIFICATION_REQUIRED`, `CAPTCHA_REQUIRED`, `RATE_LIMITED`, `WAF_BLOCKED`, or `LOGIN_REQUIRED` appears.

Instruct the `browser` subagent to inspect all 7 surfaces from [Audit Checklist](./references/audit-checklist.md) without spending credits or mutating data:
1. **Dashboard (`https://flow.google.com/?hl=en`)**: Entry URL behavior, auth signals (`Account details`, plan badge, `+ New project`), promo banners, top nav links.
2. **Changelogs (`https://flow.google.com/changelogs`)**: All entries newer than the last calibration date in `audit-checklist.md` (dates, titles, new features, deprecation notices).
3. **Project Workspace (`/project/<id>`, reusing an existing project)**: Top bar (`Add media menu`, `More options`), left sidebar (`Project navigation`), `Flow Agent` toggle vs. Manual Mode controls.
4. **Generation Settings (`Settings trigger` in Manual Mode)**:
   - `Image` mode: aspect ratios, exact model names, `Thinking level` / options, output counts, live credit readout.
   - `Video` mode: `Video type` options (`Frames`, `Ingredients`, or any new modes), aspect ratios, exact model names (flag any `Leaving <Date>` deprecation badges or removed models), resolutions, durations, output counts, live credit readouts.
   - Check whether any new control panels (e.g., Camera Controls, Audio controls) were added.
5. **Characters, Collections & Ingredients (`/project/<id>/character`, `+` / `@` picker)**: Exact `@` filter tabs, character archetypes, upload/generate flows.
6. **Scenes, Clip Editor (`/project/<id>/edit/<clipId>`) & Download Submenu**: Card `More options` items, `Download` submenu resolutions and credit costs, editor player buttons (`Save frame`, etc.), timeline actions (`Add clip`, `Extend`, etc.), and inline edit composer models.
7. **Tools (`/project/<id>/tools`) & Create tool (`/project/<id>/create-tool`)**: Tab names (`My Tools`, `Community`, `Templates`), newly added or removed template tools, and `Create tool` starter presets / pricing notice.

### Step 3: Produce a Structured Drift Diff

Compare the live browser report against the plugin's current files (`rules/AGENTS.md`, `skills/*/SKILL.md`, `skills/*/references/*.md`, `plugin.json`, `README.md`) and classify every difference into 4 buckets:

- **Added**: New models, UI modes, tools, export tiers, or workflows present on Flow Web but missing from the plugin.
- **Changed**: Renamed buttons/menus, shifted routes, updated default models, or changed credit costs.
- **Deprecated (Upcoming Removal)**: Models or features marked `Leaving <Date>` or announced for retirement in `/changelogs`.
- **Removed / Obsolete**: Models, tabs, buttons, or workflows still documented in the plugin that no longer exist in the live UI.

### Step 4: Patch & Prune Plugin Files

Apply targeted edits across the plugin:
- Update `rules/AGENTS.md` if entry URLs, auth signals, credit-gating actions, or sandbox constraints changed.
- Update `skills/flow-director/`, `skills/flow-ingredients/`, `skills/flow-generate/`, `skills/flow-scene-builder/`, and `skills/flow-tools/` (and their `references/`) to reflect all **Added** and **Changed** items and **delete** all **Removed / Obsolete** instructions.
- If Flow introduced a major new top-level capability that does not fit any existing skill, scaffold a new `skills/flow-<capability>/SKILL.md` and document it in `README.md`.
- Update `plugin.json` (`version` bump if appropriate, `description`, `suggestedPrompts`) and update the baseline snapshot date and changelog notes in [Audit Checklist](./references/audit-checklist.md).

### Step 5: Verify Integrity & Plugin Discovery

Run all checks before reporting completion:
1. **Verification suite**: Run `python tests/run_tests.py` (passes cleanly under default Windows console encoding and UTF-8).
2. **English-only / 7-bit ASCII check**: Verify zero CJK characters exist in core plugin files and English docs.
3. **Plugin loader verification**: Re-run Antigravity's plugin inventory (`lsrpc GetAllPlugins`) and confirm `antigravity-flow` loads cleanly with all expected skills and `rules/AGENTS.md`.

### Step 6: Report the Sync Changelog

Present a concise summary grouped by **Added**, **Changed**, **Deprecated**, and **Removed**, with clickable links to all modified files and the updated calibration date.
