# Google Flow Plugin Operating Rules

These rules apply whenever the user works with **Google Flow** (`https://flow.google.com`) using this plugin.

## 1. Browser Delegation, Entry URL & Session Reuse

- Always drive Google Flow through Antigravity's built-in `browser` subagent (`invoke_subagent` with `TypeName: "browser"`, `Model: "flash"` unless the user specifies another model). Do not use `curl`, Playwright scripts, or external browser launchers to access Flow.
- Always open **`https://flow.google.com/?hl=en`** directly as the canonical entry URL to enforce standard English UI strings (`"Generating will use <N> credits"`). Avoid navigating through legacy redirect URLs such as `https://labs.google/fx/tools/flow`, which can trigger an unnecessary `accounts.google.com` SSO hop even when the user is already signed in.
- Within a Flow production session, reuse the same `browser` subagent via `send_message` using its `conversationId` so the open project tab and authenticated session stay intact. Do not kill an idle `browser` subagent between steps.
- Give the `browser` subagent **semantic UI goals** (visible labels, controls, visual verification criteria) rather than brittle CSS selectors, so workflows remain resilient across Flow UI updates.

## 2. Fast-Path Authentication Check (Signed-In Shortcut)

Before assuming the user needs to sign in, always verify whether an authenticated Flow session is already active:

- **Check the current tab first** (if already on `https://flow.google.com/...`); otherwise navigate directly to `https://flow.google.com/?hl=en`.
- **Verify signed-in state using visual, DOM, and network signals together**:
  - **Above-the-fold visual & DOM signals**: Presence of the top-right `Account details` button (user profile avatar and optional plan badge such as `ULTRA`/`PRO`/`PLUS`), the floating `+ New project` button, the `Sort projects` control, or existing `/project/<id>` project cards (`Open project`), with no `Sign in` button.
  - **URL & network signals**: Page remains on `https://flow.google.com/` (for example `/?pli=1` or `/project/...`) and Flow's frontend RPC (`POST https://flow.google.com/_/AiSandboxAngularFrontend/data/batchexecute`) returns HTTP `200`.
  - **Sandbox constraint**: Do not attempt to read `document.cookie`, `localStorage`, or `sessionStorage` via `page.evaluate`, as those APIs are blocked by the sandboxed browser runtime.
- **Shortcut**: As soon as the signed-in signals are confirmed, skip all authentication prompts and proceed directly to the user's task.
- Only pause with `LOGIN_REQUIRED` when opening `https://flow.google.com/` directly blocks on `accounts.google.com` or renders a logged-out page with a `Sign in` button.

## 3. Live Credit Sniffer & Autonomy Modes (Single Source of Truth)

Account tiers (Free, PLUS, PRO, ULTRA 5x/20x) determine whether image and video generation costs credits. The plugin never assumes generation is unconditionally free. It implements a **Hardened Live Credit Sniffer** as the single source of truth by reading the live UI indicator prior to clicking `Start generation`:

- **Account Plan Detection**: Check the top-right `Account details` badge for `ULTRA` (5x or 20x tier), `PRO`, `PLUS`, or unbadged (`FREE` tier).
- **Hardened Indicator Reading & Fail-Closed Safeguard**: Inspect the visible text near the bottom composer or Settings popover:
  - Regex: `/(?:Generating will use|Costs?)\s+(?<![\d.,-])(\d+)(?![\d.,])\s+credits?\b/i` or `^\s*(?<![\d.,-])(\d+)(?![\d.,])\s+credits?\s*$`
  - **Fail-Closed Gate**: If the UI text displays `"Generating will use NaN credits"`, non-integer values, negative numbers (`-10 credits`), unparsed text, or is delayed due to SPA hydration, NEVER assume 0 credits. Word-boundary invalid token checks (`\b(?:nan|undefined|null|infinity)\b`) halt execution while preserving `"Nano Banana"` image prompts. Unanchored balance readouts (such as `"1,000 credits remaining"`) are strictly ignored.
- **Autonomy Decision Matrix**:
  1. **Zero Credits (`0 credits`)**:
     - Automatically execute in auto mode (unattended, full-auto).
     - Applies to Nano Banana 2.1 static images on all tiers (bounded by 24h rolling quotas: 400 images for Free, 1,000 for Plus+), scene creation/reordering, frame extraction (`Save frame`), standard downloads (`GIF`), and standard upscales (`720p`, `1080p` up to 10s on Plus, Pro, or Ultra). Tool creation in `Create tool` is 0 credits and gated to Plus+ accounts.
  2. **Paid Credits (`> 0 credits`)**:
     - Pause in checkpoint mode (default).
     - Inform the user of the exact credit cost before clicking `Start generation`:
       `"Generation will consume <N> credits. Proceed?"`
     - Proceed only upon user confirmation.
  3. **Shared Google One AI Credit Pool Protection & Ceilings**:
     - Antigravity and Google Flow share the unified Google One AI credit pool.
     - Single-Action Ceiling: Any generation or upscale exceeding `MAX_CREDIT_CEILING = 60` credits MUST pause for user confirmation even in `auto` mode.
     - Cumulative Session Ceiling: Total generation spend within one session is capped at `MAX_SESSION_CREDITS = 120` credits. Once exceeded, automation pauses for explicit approval.
  4. **Dynamic Upscale Duration Gating**:
     - 720p / 1080p Upscale: 0 credits for 1-10s; 1 credit per second past 10s on Google AI Plus+.
     - 4K Upscale: 50 credits for 1-10s; 50 + 5 credits per second past 10s, exclusively gated to Google AI Ultra.
     - Any upscale operation with duration > 10s, as well as any 4K upscale, ALWAYS requires explicit checkpoint confirmation.
  5. **Inter-Request Pacing Delay (Rate Limit Protection)**:
     - Google Flow enforces rolling 24-hour velocity limits (`"requesting generations too quickly"`). In automated generation loops (such as `flow-ingredients` or batch `flow-generate`), enforce a minimum pacing delay of `2.5 seconds` between generation dispatches, with exponential backoff on retry.
  6. **Prompt Overrides**:
     - When the user explicitly requests full automation in the prompt (e.g., `"auto mode"`, `"full-auto"`, `"run unattended"`, `"without asking"`, `"batch generate all"`), proceed automatically for all scheduled shots up to `MAX_CREDIT_CEILING = 60`, while honoring safety boundaries.

## 4. Hard Safety & Platform Boundaries (Both Modes)

Even in auto mode, always pause immediately and hand control to the user when the `browser` subagent encounters:

- **Google Sign-In / Authentication (`LOGIN_REQUIRED`)**: Protected auth origins cannot be automated. Ask the user to sign in inside the browser pane, then resume the same `browser` subagent via `send_message`.
- **Bot Challenges & Verification Prompts**: Never attempt to bypass challenge gates. Pause and ask the user to complete verification in the browser window.
- **Credit / Quota Exhaustion or Payment Pages (`PAYMENT_REQUIRED`)**: Pause and ask the user to top up credits or switch to a lower tier (e.g., `Veo 3.1 - Lite [Lower Priority]`).

## 5. Local File Staging Contract

The `browser` subagent is sandboxed and cannot read arbitrary workspace paths directly:

- **For web uploads** (Ingredients images, start/end keyframes): Copy each file to `<Artifact Directory Path>/browser_sandbox/uploads/<filename>` (single-segment filename) and pass the bare `<filename>` to the `browser` subagent.
- **For visual reference inspection**: Copy reference images to `<Artifact Directory Path>/browser_sandbox/references/<filename>` and pass the full path.
- **For downloaded outputs**: Record the downloaded file paths returned by the `browser` subagent in `<Artifact Directory Path>/browser_sandbox/downloads/<filename>`.

## 6. Asset Synchronization Pipeline

Downstream workflows must automatically persist generated outputs into the user's workspace:

1. **Extraction**: Move or copy downloaded media from `browser_sandbox/downloads/` to the target local workspace directory (e.g., `assets/` or `outputs/shots/`).
2. **Visual Inspection**: Run visual inspection on generated media to confirm anatomy, layout, and absence of visual artifacts before final reporting.
3. **Brand Asset Reuse**: Always reuse brand assets from the personal brand library (e.g., `brand-avatar.png`, `favicon.ico`) when configuring user avatars, logos, or author branding.

## 7. Proactive Multi-Modal Routing Protocol

Route creative visual requests proactively to Google Flow via this plugin without requiring explicit keywords:

- **Commercial Posters, Banners & Illustrations**: Route to `flow-ingredients` (Nano Banana 2.1).
- **Film & Commercial Storyboards**: Route to `flow-director` (Omni 1.2 Flash & Veo 3.1 5-slot grammar).
- **Video Shot Generation & Rendering**: Route to `flow-generate` (Omni 1.2 Flash primary flagship with 360p draft at 1 cr/s and 720p standard at 3 cr/s, seconds 11-15 billed at double rate; Veo 3.1 - Lite secondary baseline. Note: Veo 3.1 Fast, Veo 3.1 Quality, and Omni 1.1 Flash retire on Dec 5, 2026).
- **Multi-Shot Timeline Sequencing & Invariant**: Route to `flow-scene-builder`. Timeline Invariant: All inline video edits (insert, remove, camera, edit, in-place) must be executed before applying Extend. Extend is bound exclusively to Omni 1.2 Flash (3-10s per extend, up to 30s total).
- **Specialized Creative Tools & Mini-Apps**: Route to `flow-tools`.
