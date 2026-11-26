---
name: flow-director
description: >-
  Plan an AI filmmaking or video production: break a story idea, brief, or script into a structured storyboard with consistent Ingredients (characters, objects, styles), cinematic shot prompts (including camera direction), audio cues, and model choices (Omni 1.2 Flash, Veo 3.1, Nano Banana). Use when planning videos, drafting shot lists, designing cinematographic prompts, or creating storyboards.
---

# Flow Director (Storyboard & Prompt Planner)

Turn a creative idea, script, or reference brief into a structured, execution-ready **Google Flow Production Plan** (`storyboard.md`) without spending any Flow credits.

## When to Use

- The user wants to plan a short film, commercial, music video, or multi-shot sequence for Google Flow.
- The user wants to refine or translate rough ideas into Flow-optimized cinematic prompts using Veo 3.1 5-slot grammar.
- The user wants a structured `storyboard.md` that downstream skills (`flow-ingredients`, `flow-generate`, `flow-scene-builder`) can execute in either `checkpoint` or `auto` mode.

## Workflow

### Step 1: Capture Creative Brief & Constraints

Extract from the user's request (ask briefly only if critical parameters are missing):

- **Narrative & Tone**: Logline, mood, genre, pacing, and visual style.
- **Aspect Ratio**: `16:9` (landscape, default) or `9:16` (vertical) for video; `16:9`, `4:3`, `1:1`, `3:4`, or `9:16` for image Ingredients.
- **Budget / Model Tier Strategy**:
  - **Zero-cost / low-cost drafting**: `Veo 3.1 - Lite [Lower Priority]` (0 credits on ULTRA) or `Omni 1.2 Flash` at `360p` draft mode (1 credit/s for rapid blocking).
  - **Hero / final video**: `Omni 1.2 Flash` at `720p` (3 credits/s; industry-leading character and scene consistency; primary recommended flagship; note: 11-15s clips bill seconds 11-15 at double rate). Note that `Veo 3.1 - Quality` and `Veo 3.1 - Fast` retire on Dec 5, 2026, while `Veo 3.1 - Lite` remains active as secondary baseline.
  - **Image Ingredients**: `Nano Banana 2.1` (0 credits on Pro/Ultra) with `Thinking level` (`Low` / `Medium` / `High`).
- **Autonomy Preference**: Check whether the user requested `auto` mode (e.g., `"auto mode"`, `"full-auto"`, `"run unattended"`) or default `checkpoint` mode. In `auto` mode, recommend `x1` output count by default and plan batches within `MAX_SESSION_DISPATCHES = 12` (including `0-credit` actions) with a randomized `8-15s` pacing cooldown between dispatches.

### Step 2: Design Consistent Ingredients

Identify recurring visual and audio anchors that must stay consistent across shots:

- **Characters** (e.g., `@detective_chen`, `@me` avatar) — uploaded, generated with `Nano Banana 2.1`, or built in `Create character`.
- **Objects & Environments** (e.g., `@brass_compass`, `@rainy_neo_tokyo_style`).

For each Ingredient, specify:
- Handle (`@slug`, lowercase ASCII with underscores)
- Category (`Characters`, `Images`, `Uploads`, `Voices`, etc.)
- Source: `upload` (with local file path) or `generate` (with a crisp `Nano Banana 2.1` prompt)
- Invariant visual traits

### Step 3: Break Down the Shot List with Veo 3.1 5-Slot Grammar

Read [Veo Prompt Guide](./references/veo-prompt-guide.md). Apply the mandatory 5-slot grammar:

`[Cinematography] + [Subject] + [Action] + [Context] + [Style & Ambiance] . [Audio Sentences]`

1. **Cinematography**: Camera framing, lens, and velocity adverb (e.g., `Low-angle tracking shot, 35mm lens, slow steady push-in`). Avoid numeric weights like `(pan:1.4)` or multi-axis camera conflicts.
2. **Subject**: Hero character or asset with `@handle` (e.g., `@detective_chen in trench coat`).
3. **Action**: Single clear physical action tailored to clip duration (4s-8s).
4. **Context**: Location, weather, practical lighting, background elements.
5. **Style & Ambiance**: Color grading, lighting atmosphere, rendering quality.
6. **Audio Sentences**: Isolated trailing sentences (`Ambient noise: ... SFX: ... @speaker speaks: "..."`).

### Step 4: Write `storyboard.md`

Output the plan to `storyboard.md`:

```markdown
# Flow Production Plan: <Title>

- **Project Name**: <Flow project name>
- **Aspect Ratio**: 16:9
- **Default Video Model**: Omni 1.2 Flash (720p, 8s) / Veo 3.1 - Lite [Lower Priority] (draft)
- **Default Image Model**: Nano Banana 2.1 (Thinking: Medium)
- **Autonomy Mode**: checkpoint | auto

## Ingredients

| Handle | Category | Source | Local Path / Generation Prompt |
| :--- | :--- | :--- | :--- |
| `@hero` | Characters | generate | Full-length character sheet of a futuristic explorer in white spacesuit, neutral lighting |

## Shot List

### S01 — Entering the Ruins
- **Video Type**: Ingredients
- **Ingredients / Frames**: `@hero`
- **Model**: Omni 1.2 Flash (720p, 8s, x1)
- **Prompt**: Low-angle tracking shot, 35mm anamorphic lens, slow steady push-in, @hero walks cautiously forward through ancient stone archway, dust motes floating in diagonal beams of morning sunlight, photorealistic cinematic lighting with soft golden haze. Ambient noise: hollow wind whistling through stone corridors. SFX: heavy boot steps echoing on fractured marble.
- **Audio**: Ambient wind, heavy boot steps
- **Scene Transition**: Add to scene -> Cut to S02
```

### Step 5: Hand Off to Execution

- Proceed to `flow-ingredients` to configure project assets.
- Proceed to `flow-generate` to render shots in `checkpoint` mode or `auto` mode.
