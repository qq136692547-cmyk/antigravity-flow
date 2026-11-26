---
name: flow-scene-builder
description: >-
  Assemble, sequence, extend, edit, and export multi-shot videos inside Google Flow's
  Scenes view and Clip/Scene Editor (/project/<id>/edit/<clipId>) via Antigravity's
  built-in browser. Use when the user wants to combine generated Flow clips into a
  scene timeline, extend a shot, extract a frame with Save frame, run in-place video
  edits, or download the finished video.
---

# Flow Scene Builder (Scenes & Timeline Editor)

Operate Google Flow's **`Scenes`** view and **Clip/Scene Editor** (`/project/<projectId>/edit/<clipId>`) via Antigravity's built-in `browser` subagent to turn individual generated shots into a cohesive edited scene and download the final video.

> **UI calibration note**: Current Google Flow does not use a literal `"Scene Builder"` tab. Scenes are managed via the left sidebar **`Scenes`** view, top-right `+` -> **`New scene`**, clip card `More options` -> **`Add to scene`**, and clicking any clip/scene to enter the timeline editor (`/project/<projectId>/edit/<clipId>`).

## Prerequisites & Shared Rules

Follow `rules/AGENTS.md`:
- Reuse the active Flow `browser` subagent (`send_message`) so the open `/project/<projectId>` tab and generated clip library remain open (project reuse first before creating any new project).
- Respect `checkpoint` vs. `auto` mode:
  - Creating a scene, adding/reordering existing clips (`Add to scene`, `Add clip`), `Save frame`, and `Download media` do **not** consume credits and can run directly.
  - **`Extend`** (exclusively Omni 1.2 Flash, 3-10s per extend up to 30s) and inline video edits (`"Describe how to edit this video..."`) invoke video generation and **do** consume credits — confirm first in `checkpoint` mode, or run directly in `auto` mode (up to `MAX_CREDIT_CEILING = 60`, `MAX_SESSION_DISPATCHES = 12` including `0-credit` actions, and randomized `8-15s` pacing jitter between successive dispatches).
- Enforce zero-retry (`retry_count = 0`) hard-stop boundaries (`PAUSED_*`) on `ACCOUNT_VERIFICATION_REQUIRED`, `CAPTCHA_REQUIRED`, `RATE_LIMITED`, `WAF_BLOCKED`, `SAFETY_BLOCKED`, `LOGIN_REQUIRED`, and `PAYMENT_REQUIRED` (no auto-retry, no blind refresh-resubmit, no prompt softening).
- **Timeline Invariant**: All in-place video edits MUST be executed *prior* to applying `Extend`. Flow Web UI blocks inline edits on extended clips.

## Workflow

### Step 1: Confirm Timeline Order & Edit Operations

From `storyboard.md` or the user's request, identify:
- Ordered list of shots (`S01` -> `S02` -> ...) to include in the scene.
- Any clips that need an in-place video edit (`"Describe how to edit this video..."` with `Omni 1.2 Flash` and optional `+` Ingredients) — **execute these first**.
- Any clips that need AI **`Extend`** on the timeline (exclusively `Omni 1.2 Flash`), along with the continuation prompt.
- Any frame extractions needed for continuity (**`Save frame`** in the player controls).
- Desired export destination in the local workspace (e.g., `./outputs/final/<project-name>.mp4`).

### Step 2: Assemble Clips into a Scene

Instruct the `browser` subagent:
1. Inside the active Flow project:
   - Either hover each selected clip card in storyboard order -> click `More options` -> **`Add to scene`**, OR
   - Create a fresh scene via top-right `+` (`Add media menu`) -> **`New scene`** (or open an existing scene from the left sidebar **`Scenes`** tab), then add clips via the timeline's **`Add clip`** menu -> **`Add clip`**.
2. Click the scene / clip to open the **Clip/Scene Editor** (`/project/<projectId>/edit/<clipId>`).
3. Verify all intended clips appear on the timeline in the requested sequence (use `Zoom out` / `Zoom in` if needed to inspect the full timeline).

### Step 3: Extend, Edit, or Extract Frames

- **Save frame** (no credits): Scrub to the desired timestamp in the player and click **`Save frame`** to capture a clean keyframe asset for downstream `Frames` generation.
- **Extend** (consumes credits):
  - Wait a randomized `8-15s` pacing cooldown after any prior dispatch and respect `MAX_SESSION_DISPATCHES = 12`.
  - In `checkpoint` mode: Confirm the extension prompt and model before triggering generation.
  - In `auto` mode: Open the timeline **`Add clip`** menu -> select **`Extend`**, enter the continuation prompt, trigger generation, wait without blind refresh-resubmit (inspect banners first if stuck, pausing with `retry_count = 0` on any error), and verify the new segment attaches cleanly to the timeline.
- **In-place Video Edit** (consumes credits):
  - Wait a randomized `8-15s` pacing cooldown after any prior dispatch and respect `MAX_SESSION_DISPATCHES = 12`.
  - In the editor's bottom composer (`"Describe how to edit this video..."`), optionally attach Ingredients via `+`, choose `Select model family` (`Omni 1.2 Flash`), and confirm (in `checkpoint` mode) or click **`Start generation`** (in `auto` mode).

### Step 4: Preview & Download Final Video

Instruct the `browser` subagent:
1. Use the player controls (`Play`, `Skip to previous clip`, `Skip to next clip`) to verify clip transitions and check for any error badges.
2. Click **`Download media`** in the top bar of the editor, or click **`Done editing scene`** / **`Done`** and use `More options` -> **`Download`** on the card to select from the 4-option submenu (`270p Animated GIF`, `720p Original size`, `1080p Upscaled`, or `4K Upscaled · 50 credits` — confirm first in `checkpoint` mode or if duration > 10s incurring per-second billing). Project-wide export is also available via top-right `More options` -> **`Download project`**.
3. Wait for the download to finish and return the downloaded file path.

### Step 5: Organize Local Output & Summarize

- Copy the downloaded final video from the browser download path into the user's requested workspace output directory (e.g., `./outputs/final/<title>.mp4`).
- Report:
  - Final local file path (clickable markdown link)
  - Included shots, extensions/edits performed, and scene URL
  - Any shots that were skipped or need manual fine-tuning in the browser pane.
