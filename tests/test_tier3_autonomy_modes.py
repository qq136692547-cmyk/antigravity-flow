"""
Tier 3: Autonomy Modes, Safety Bounds & Prompt Trigger Tests
"""

from tests.conftest import detect_autonomy_mode, should_auto_proceed


def test_detect_autonomy_mode_english_triggers():
    triggers = [
        "Please batch generate shots 1 to 4 in auto mode",
        "Run full-auto generation for storyboard.md",
        "Generate all video clips unattended and download to outputs/",
        "Execute the remaining scene without asking for confirmation",
        "Batch generate all assets now",
    ]
    for prompt in triggers:
        assert detect_autonomy_mode(prompt) == "auto", f"Failed to detect auto mode in: {prompt}"


def test_detect_autonomy_mode_chinese_triggers():
    triggers = [
        "全自动跑完所有分镜",
        "开启免打扰模式生成所有镜头",
        "自动模式运行脚本",
        "别问我直接生成",
        "无需确认直接下载",
    ]
    for prompt in triggers:
        assert detect_autonomy_mode(prompt) == "auto", f"Failed to detect Chinese auto cue in: {prompt}"


def test_detect_autonomy_mode_default_checkpoint():
    normal_prompts = [
        "Can you plan a 4-shot storyboard for my project?",
        "Generate a character sheet for @hero",
        "Let's create shot 1 using Omni 1.2 Flash",
        "Inspect the downloaded video card",
    ]
    for prompt in normal_prompts:
        assert detect_autonomy_mode(prompt) == "checkpoint", f"Expected default checkpoint for: {prompt}"


def test_hard_safety_gates_and_4k_upscale():
    # 4K upscale must be strictly gated
    can_proceed, reason = should_auto_proceed(credit_cost=50, autonomy_mode="auto", is_upscale_4k=True)
    assert can_proceed is False
    assert "4K Upscale" in reason

    can_proceed, reason = should_auto_proceed(credit_cost=50, autonomy_mode="checkpoint", is_upscale_4k=True)
    assert can_proceed is False
    assert "4K Upscale" in reason

    # Standard 1080p download costs 0 credits and can auto-proceed
    can_proceed, reason = should_auto_proceed(credit_cost=0, autonomy_mode="auto", is_upscale_4k=False)
    assert can_proceed is True


def test_safety_boundary_simulation():
    # Simulate platform boundary handler
    def handle_platform_boundary(error_type: str) -> dict:
        if error_type in ["LOGIN_REQUIRED", "CAPTCHA_REQUIRED", "PAYMENT_REQUIRED"]:
            return {"action": "pause_for_user", "status": error_type}
        return {"action": "continue", "status": "OK"}

    assert handle_platform_boundary("LOGIN_REQUIRED")["action"] == "pause_for_user"
    assert handle_platform_boundary("CAPTCHA_REQUIRED")["action"] == "pause_for_user"
    assert handle_platform_boundary("PAYMENT_REQUIRED")["action"] == "pause_for_user"
    assert handle_platform_boundary("NONE")["action"] == "continue"


if __name__ == "__main__":
    test_detect_autonomy_mode_english_triggers()
    test_detect_autonomy_mode_chinese_triggers()
    test_detect_autonomy_mode_default_checkpoint()
    test_hard_safety_gates_and_4k_upscale()
    test_safety_boundary_simulation()
    print("Tier 3 Tests PASSED: Autonomy mode transitions and safety gates verified.")
