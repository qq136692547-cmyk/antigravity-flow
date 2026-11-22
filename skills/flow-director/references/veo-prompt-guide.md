# Google Flow & Veo 3.1 Cinematography & Prompt Guide

Use this reference when authoring video shot prompts and storyboard plans for Google Flow (`https://flow.google.com`) and Veo 3.1 / Omni 1.2 Flash.

## 1. Veo 3.1 Five-Slot Prompt Formula

Structure every video prompt following the mandatory 5-slot sequential grammar followed by isolated trailing audio sentences:

`[Cinematography] + [Subject] + [Action] + [Context] + [Style & Ambiance] . [Audio Sentences]`

### Slot Breakdown

| Slot | Purpose | Examples |
| :--- | :--- | :--- |
| **1. Cinematography** | Camera lens, framing, distance, and primary camera movement | `Low-angle tracking shot, 35mm anamorphic lens, shallow depth of field, slow steady push-in` |
| **2. Subject** | Primary character, actor, vehicle, or hero object with `@handle` | `@detective_chen wearing a charcoal trench coat with raindrops glistened on the collar` |
| **3. Action** | Concrete, single physical action occurring within the clip duration (4s-8s) | `reaches into his coat pocket and produces a polished brass pocket watch, glancing at the dial` |
| **4. Context** | Environmental location, atmosphere, weather, practical lighting, background motion | `on a rain-soaked neon-lit alleyway in Neo-Hong Kong, steam rising from underground subway grates` |
| **5. Style & Ambiance** | Cinematic lighting, color palette, rendering aesthetic, visual tone | `cinematic teal and amber color grading, volumetric haze, photorealistic film grain, 4K film still` |
| **Audio Sentences** | Isolated trailing sentences for dialogue, sound effects, and ambient hum | `Ambient noise: steady rainfall on corrugated metal roofs. SFX: metallic click of the pocket watch latch opening. @detective_chen speaks: "Time is running out."` |

---

## 2. Weight Lowering & Velocity Adverbs

Veo 3.1 does **not** accept numerical weights such as `(pan:1.4)`, `::2`, or `[zoom::1.5]`. Prompt parsers reject or ignore syntax copied from Midjourney or Stable Diffusion. Instead, translate numerical weights into front-loaded word order and **velocity adverbs**:

### Velocity Adverb Mapping

| Target Intensity | Numerical Analogue | Velocity Adverb Phrase | Example |
| :--- | :--- | :--- | :--- |
| **Minimal / Subtle** | `weight: 0.2 - 0.4` | `subtle, barely perceptible` | `Subtle, barely perceptible camera drift to the right` |
| **Gentle / Moderate** | `weight: 0.5 - 0.8` | `smooth, gentle, measured` | `Smooth, gentle crane down toward the subject` |
| **Standard / Hero** | `weight: 1.0` | `steady, cinematic, controlled` | `Steady, controlled tracking shot alongside the runner` |
| **Pronounced / Dynamic** | `weight: 1.2 - 1.5` | `deliberate, pronounced, brisk` | `Deliberate, pronounced dolly push-in on the actor's face` |
| **High-Speed / Dramatic** | `weight: 1.6 - 2.0` | `rapid, sweeping, dramatic` | `Rapid, sweeping whip pan revealing the horizon` |

---

## 3. Single-Axis Camera Primary Trajectory

Veo 3.1 creates motion distortion when given contradictory multi-axis camera commands in a single 4-8s shot. Always specify a single dominant camera trajectory:

- **Recommended Single-Axis Trajectories**:
  - `Slow push-in (dolly in)`
  - `Slow pull-back (dolly out)`
  - `Smooth horizontal tracking (pan / truck left-to-right)`
  - `Vertical boom / pedestal (crane up or crane down)`
  - `Radial orbit (orbit 90 degrees around subject)`
- **Prohibited Multi-Axis Conflicts**:
  - Do NOT combine `pan left` and `pan right` within the same shot.
  - Do NOT combine `rapid zoom in` with `rapid pull-back` unless executing an explicit vertigo effect (`dolly zoom`).

---

## 4. Flow Ingredients `@Handle` & `@me` Syntax

Google Flow links prompt text directly to project asset libraries via `@` mentions:

- `@<character_handle>`: Refers to an existing character sheet created in `Characters` or uploaded as an Ingredient (e.g., `@detective_chen`, `@sarah_pilot`).
- `@me`: Refers to the user's personal avatar profile when enabled in Flow settings.
- `@<object_handle>`: Refers to consistent props or vehicles (e.g., `@hovercar_x7`, `@ancient_relic`).
- Limit each shot prompt to a maximum of **3 Ingredients** to prevent identity bleed and cross-subject distortion.

---

## 5. Native Audio Sentences Formula

Native audio in Veo 3.1 and Omni 1.2 Flash is synthesized directly from prompt text. Always place audio specifications as distinct sentences at the end of the prompt:

1. **Ambient Bed**: `Ambient noise: <description of background acoustic space>.`
2. **Foley & Sound Effects**: `SFX: <concrete physical sound events synchronized to action>.`
3. **Dialogue**: `<Speaker> speaks in a <tone> voice: "<quoted dialogue>".`

Example:
```
Ambient noise: distant thunder echoing across the bay, gentle harbor waves lapping against the wooden pier. SFX: rubber soles creaking on wet planks, key turning in an iron padlock. @captain speaks in a gravelly whisper: "The tide is turning."
```

---

## 6. Model Compatibility & Credit Matrix

| Model Tier | Native Duration | Recommended Resolution | Credit Cost (Pro/Ultra) | Best Use Case |
| :--- | :--- | :--- | :--- | :--- |
| **Omni 1.2 Flash** | 4s / 6s / 8s | `360p` (draft) / `720p` (final) | 10 - 20 credits | Best character consistency, complex action, seamless multi-shot continuity |
| **Veo 3.1 - Quality** | 4s / 6s / 8s | `720p` / `1080p` | 20 credits | High-fidelity cinematic realism, photorealistic textures |
| **Veo 3.1 - Lite [Lower Priority]** | 4s / 6s / 8s | `720p` | **0 credits (ULTRA)** / 10 credits | Zero-credit rapid blocking, composition testing |
| **Nano Banana 2.1** | Static Image | `16:9`, `1:1`, `9:16` | **0 credits (Pro/Ultra)** | Character sheets, style boards, storyboard keyframes, commercial posters |
