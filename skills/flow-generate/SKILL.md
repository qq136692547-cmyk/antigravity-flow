---
name: flow-generate
description: >-
  Generate video shots in Google Flow (Video -> Ingredients or Video -> Frames)
  via Antigravity's built-in browser. Supports Omni 1.2 Flash and Veo 3.1 model
  selection, resolution/duration/output count configuration, exact pre-flight credit
  checks, batch storyboard execution, visual inspection, and downloading clips in
  checkpoint or full-auto mode.
---

# Flow Generate (Shot Generation & Iteration)

Drive Google Flow (`https://flow.google.com`) via Antigravity's built-in `browser` subagent to generate individual video shots or execute a full multi-shot batch from `storyboard.md`.

## Prerequisites & Shared Rules

Follow `rules/AGENTS.md`:
- Reuse the active Flow `browser` subagent (`send_message`) whenever one is already open; otherwise invoke a new `browser` subagent (`Model: "flash"`) directly at `https://flow.google.com/` and apply the Fast-Path Authentication Check before pausing for login.
- Respect the detected autonomy mode (`checkpoint` by default; `auto` when the user prompt requests full-auto execution).
- Enforce the **Fail-Closed Live Credit Sniffer**: If the UI readout contains `NaN` (e.g., `"Generating will use NaN credits"`), unparsed text, or non-integers, pause immediately in checkpoint mode. Never assume 0 credits on parse failure.
- Enforce the **Credit Ceiling Gate**: To protect the shared Google One AI credit pool with Antigravity, any single generation or batch action exceeding `MAX_CREDIT_CEILING = 60` credits must pause for explicit user confirmation, even in `auto` mode.
- Enforce **Dynamic Upscale Gating**: 1080p upscales past 10s (1 credit/s) and all 4K upscales (50 credits + 5 credits/s past 10s) must pause for confirmation.
- Always pause for Google sign-in, CAPTCHA, or credit/payment blocks (`PAYMENT_REQUIRED`).

## Workflow

### Step 1: Resolve Shot Specification(s) & Autonomy Mode

Determine what is being generated:
- **Single shot**: Prompt (including explicit camera direction and audio cues, since Flow has no separate Camera Control menu), Video type (`Ingredients` for Text-to-Video / Ingredients-to-Video, or `Frames` for Start/End keyframe animation), Ingredients (`@handles`), keyframes (if any), aspect ratio (`16:9` or `9:16`), model (`Omni 1.2 Flash` primary flagship, `Veo 3.1 - Lite [Lower Priority]` or `Veo 3.1 - Lite` secondary baseline; note Veo Fast/Quality retire Dec 5, 2026), resolution (`360p` draft mode at 1 credit/s or `720p` standard at 3 credits/s for Omni; seconds 11-15 billed at double rate), duration (`4s` / `6s` / `8s` / `10s`), and output count (`x1`–`x4`).
- **Batch from `storyboard.md`**: Read the shot list (`S01..Sn`) and note which shots are still pending.
- **Autonomy mode**:
  - Check the user's current prompt (and `storyboard.md` header) for full-auto cues in any language (e.g., `"auto mode"`, `"full-auto"`, `"run unattended"`, `"batch without asking"`).
  - Default to `checkpoint` mode if unspecified.

### Step 2: Stage Local Keyframes (If Using `Video` -> `Frames`)

For any shot requiring local `Start` or `End` keyframes:
1. Copy each keyframe image to `<Artifact Directory Path>/browser_sandbox/uploads/<filename>` (single-segment filename).
2. Pass only the bare `<filename>` to the `browser` subagent.

### Step 3: Configure Manual Mode & Check Exact Credit Cost

Instruct the `browser` subagent to prepare the composer (without clicking `Start generation` yet in `checkpoint` mode):
1. Ensure the target Flow project is open.
2. **Switch to Manual Mode**: Verify the bottom composer's **`Flow Agent` toggle is OFF** (`aria-pressed="false"`), so direct generation controls are visible.
3. Click **`Settings trigger`** and configure:
   - **`Mode`**: `Video`
   - **`Video type`**:
     - `Ingredients` (for pure Text-to-Video with nothing attached, or Ingredients-to-Video using `+` `Add ingredients to the prompt box` / typing `@` -> filter tabs `All` / `Images` / `Videos` / `Voices` / `Characters` / `Avatars` / `Uploads` -> `Add to prompt`)
     - `Frames` (exposes `Start`, `Swap first and last frames`, and `End` slots in the prompt bar to upload or pick keyframes)
   - **Aspect ratio**: `16:9` or `9:16`
   - **Model (`Select model family`)**: e.g., `Omni 1.2 Flash`, `Veo 3.1 - Lite [Lower Priority]` (0 credits on ULTRA), `Veo 3.1 - Lite`, or another requested model
   - **Resolution & Length / Duration**: e.g., `360p` or `720p` and `Length` slider for `Omni 1.2 Flash`, or `4s` / `6s` / `8s` for `Veo 3.1`
   - **Output count**: `x1`, `x2`, `x3`, or `x4`
4. Read the exact live credit indicator at the bottom of the Settings popover: **`Generating will use <N> credits`**.

### Step 4: Pre-Generation Checkpoint (In `checkpoint` Mode Only)

- **In `checkpoint` mode**: Present a concise pre-flight table (Shot ID, Video Type, Model, Resolution/Duration, Output Count, **exact credit cost from Flow UI**, Ingredients/Frames, Prompt summary) and ask the user to confirm before clicking **`Start generation`**. Also mention they can reply `"switch to auto mode"` to run the remaining shots without per-shot prompts.
- **In `auto` mode**: Skip this confirmation and proceed directly to Step 5.

### Step 5: Execute Shot Generation in Browser

Send semantic instructions to the `browser` subagent for each shot (or sequential batch):
1. Attach any required Ingredients (`+` -> `Add to prompt` or `@` mention) or upload `Start` / `End` frames (`Frames` mode).
2. Enter the prompt text into `"What do you want to create?"`.
3. Click **`Start generation`** (arrow button).
4. Wait for the generation progress indicator to complete (video generation typically takes 30 seconds to several minutes; wait patiently without refreshing unless stuck).
5. Verify the rendered video card(s) appear under `All media` / `Videos` with no error banner, policy block, or credit exhaustion notice.

### Step 6: Inspect, Iterate, or Download

- **Visual verification**: Ask the `browser` subagent to inspect the rendered video card thumbnails/playback and report any obvious defects (broken anatomy, wrong Ingredient identity, cut-off framing, policy refusal).
- **Card actions available**: Hover for `Favorite`, `Reuse prompt`, or `More options` (`Add to scene`, `Add to prompt`, `Download`, `Rename`, `Copy`, `Share`, `Publish to YouTube`, `Set project cover`, `Flag output`, `Move to trash`).
- **Download submenu (`More options` -> `Download`)**: Clicking/hovering `Download` opens a 4-option format/resolution submenu:
  - `270p Animated GIF` (0 credits)
  - `720p Original size` (0 credits)
  - `1080p Upscaled` (0 credits for 1-10s; 1 credit/s past 10s on Plus+; confirm if duration > 10s)
  - `4K Upscaled · 50 credits` (consumes 50 credits for 1-10s + 5 credits/s past 10s on Ultra — confirm first in `checkpoint` mode before selecting)
- **In `checkpoint` mode**: Report the generated takes and ask whether to `Favorite` / keep, `Reuse prompt` to re-roll, switch model/resolution (e.g., `360p` -> `720p` on `Omni 1.2 Flash`), `Add to scene`, or `Download` (specifying resolution tier).
- **In `auto` mode**:
  - If a shot fails with a transient error, retry once automatically; if blocked by a safety/policy filter, lightly soften the phrasing once or log the block and continue with remaining shots.
  - `Favorite` the best take per shot (or click `More options` -> `Add to scene` if assembling next) and `Download` clips if local export was requested.

### Step 7: Sync Outputs & Status

- Update shot status (e.g., `generated`, `favorited`, `added-to-scene`, `downloaded`) in `storyboard.md` if present.
- If clips were downloaded, copy/organize them into the requested local output directory (e.g., `./outputs/shots/S01.mp4`) with clean shot-numbered filenames.
- Hand off to `flow-scene-builder` if the user wants to sequence, extend, edit, and export the final film.
