"""
Tier 4: Veo 3.1 5-Slot Grammar Compiler & Storyboard Parser Tests
"""

from tests.conftest import validate_veo_prompt_syntax, parse_storyboard_markdown


def test_valid_veo_prompt_5_slot_grammar():
    prompt = (
        "Low-angle tracking shot, 35mm anamorphic lens, slow steady push-in, "
        "@detective_chen walks cautiously forward through the rain-slicked alleyway, "
        "tall brick walls adorned with buzzing holographic neon signs, "
        "cinematic teal and amber color grade with photorealistic volumetric smoke. "
        "Ambient noise: steady rainfall dripping onto metal fire escapes. "
        "SFX: leather boots splashing softly in puddles. "
        '@detective_chen speaks in a calm whisper: "The trace ends here."'
    )
    result = validate_veo_prompt_syntax(prompt)
    assert result["valid"] is True, f"Prompt should be valid: {result['issues']}"
    assert result["has_velocity_adverb"] is True
    assert len(result["audio_elements"]) == 3
    assert result["handles"] == ["detective_chen"]


def test_reject_numeric_weights():
    invalid_prompts = [
        "Dolly push-in (pan:1.4) on @actor standing in field",
        "Wide shot of mountain landscape ::2 with sunset",
        "Cinematic portrait [zoom::1.5] @character in armor",
    ]
    for prompt in invalid_prompts:
        result = validate_veo_prompt_syntax(prompt)
        assert result["valid"] is False, f"Should reject numeric weight in: {prompt}"
        assert any("numeric weight" in issue for issue in result["issues"])


def test_reject_conflicting_camera_trajectories():
    conflicting_prompts = [
        "Drone panning left across the coastline while panning right over the cliffs",
        "Camera dolly in on hero face then immediately dolly out within 4 seconds",
        "Crane up to the tower roof and crane down simultaneously",
    ]
    for prompt in conflicting_prompts:
        result = validate_veo_prompt_syntax(prompt)
        assert result["valid"] is False, f"Should reject camera conflict in: {prompt}"
        assert any("Contradictory camera directions" in issue for issue in result["issues"])


def test_velocity_adverb_detection():
    test_cases = [
        ("Subtle, barely perceptible camera drift to the right", True),
        ("Smooth, gentle crane down revealing the garden", True),
        ("Steady, controlled tracking shot following the car", True),
        ("Deliberate, pronounced push-in on the envelope", True),
        ("Rapid, sweeping whip pan to the door", True),
        ("Fast camera moves around the room without description", False),
    ]
    for prompt, expected in test_cases:
        res = validate_veo_prompt_syntax(prompt)
        assert res["has_velocity_adverb"] is expected, f"Failed for velocity check: {prompt}"


def test_storyboard_markdown_parser():
    sample_storyboard = """# Flow Production Plan: Neon Odyssey

- **Project Name**: Neon_Odyssey_Teaser
- **Aspect Ratio**: 16:9
- **Default Video Model**: Omni 1.2 Flash (720p, 8s)
- **Default Image Model**: Nano Banana 2.1 (Thinking: Medium)
- **Autonomy Mode**: auto

## Ingredients

| Handle | Category | Source | Local Path / Generation Prompt |
| :--- | :--- | :--- | :--- |
| `@hero` | Characters | generate | Concept art of cyberpunk ranger in matte black carbon suit |

## Shot List

### S01 — The Neon Alley
- **Video Type**: Ingredients
- **Ingredients / Frames**: `@hero`
- **Model**: Omni 1.2 Flash (720p, 8s, x2)
- **Prompt**: Low-angle tracking shot, 35mm lens, slow steady push-in, @hero steps out of the shadows. Ambient noise: rain. SFX: footsteps.
- **Audio**: Rain and footsteps
- **Scene Transition**: Add to scene -> Cut to S02

### S02 — The Discovery
- **Video Type**: Frames
- **Ingredients / Frames**: `Save frame` from S01
- **Model**: Veo 3.1 - Lite (720p, 6s)
- **Prompt**: Smooth, deliberate crane up revealing the glowing datapad in hero hands. SFX: electronic beep.
- **Audio**: Electronic beep
- **Scene Transition**: Add to scene
"""
    parsed = parse_storyboard_markdown(sample_storyboard)
    assert parsed["title"] == "Neon Odyssey"
    assert parsed["project_name"] == "Neon_Odyssey_Teaser"
    assert parsed["aspect_ratio"] == "16:9"
    assert parsed["autonomy_mode"] == "auto"
    assert len(parsed["shots"]) == 2
    
    s01 = parsed["shots"][0]
    assert s01["id"] == "S01"
    assert s01["title"] == "The Neon Alley"
    assert s01["video_type"] == "Ingredients"
    assert "@hero" in s01["prompt"]
    
    s02 = parsed["shots"][1]
    assert s02["id"] == "S02"
    assert s02["title"] == "The Discovery"
    assert s02["video_type"] == "Frames"


if __name__ == "__main__":
    test_valid_veo_prompt_5_slot_grammar()
    test_reject_numeric_weights()
    test_reject_conflicting_camera_trajectories()
    test_velocity_adverb_detection()
    test_storyboard_markdown_parser()
    print("Tier 4 Tests PASSED: Veo 3.1 5-slot grammar and storyboard parser verified.")
