"""
Tier 3: Autonomy Modes, Safety Bounds & Prompt Trigger Tests
"""

from tests.conftest import (
    HARD_STOP_BOUNDARIES,
    classify_platform_error,
    detect_autonomy_mode,
    handle_platform_boundary,
    should_auto_proceed,
)


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
    # Verify zero-retry hard-stop PAUSED_* boundaries across all 7 platform/safety gates
    for err in HARD_STOP_BOUNDARIES:
        res = handle_platform_boundary(err)
        assert res["action"] == "pause_for_user", f"Expected pause_for_user for {err}"
        assert res["status"] == f"PAUSED_{err}", f"Expected PAUSED_{err}, got {res['status']}"
        assert res["retry_count"] == 0, f"Expected zero-retry for {err}"
        assert res["allow_refresh_resubmit"] is False
        assert res["allow_prompt_softening"] is False

    ok_res = handle_platform_boundary("NONE")
    assert ok_res["action"] == "continue"
    assert ok_res["status"] == "OK"
    assert ok_res["retry_count"] == 0


def test_platform_error_signal_classification():
    cases = [
        ("Your account must be verified at https://flow.google.com/verify-account", None, "ACCOUNT_VERIFICATION_REQUIRED"),
        ("Please complete the reCAPTCHA challenge to continue", None, "CAPTCHA_REQUIRED"),
        ("Error: requesting generations too quickly", None, "RATE_LIMITED"),
        ("HTTP 429 Too Many Requests", None, "RATE_LIMITED"),
        ("Status 429", None, "RATE_LIMITED"),
        ("Too many requests", 429, "RATE_LIMITED"),
        ("Our systems have detected unusual traffic from your computer network", 403, "WAF_BLOCKED"),
        ("HTTP 403 Forbidden", None, "WAF_BLOCKED"),
        ("Cloudflare Turnstile verification blocked access", None, "WAF_BLOCKED"),
        ("Generation blocked by content policy safety filter", None, "SAFETY_BLOCKED"),
        ("Redirected to accounts.google.com Sign in", None, "LOGIN_REQUIRED"),
        ("Insufficient credits: top up to continue", None, "PAYMENT_REQUIRED"),
    ]
    for signal_text, status_code, expected_err in cases:
        classified = classify_platform_error(signal_text=signal_text, status_code=status_code)
        assert classified == expected_err, f"Expected {expected_err} for {signal_text!r}, got {classified!r}"
        res = handle_platform_boundary(signal_text=signal_text, status_code=status_code)
        assert res["action"] == "pause_for_user"
        assert res["status"] == f"PAUSED_{expected_err}"
        assert res["retry_count"] == 0

    assert classify_platform_error("Generating will use 0 credits", status_code=200) is None
    assert classify_platform_error("Generating will use 429 credits", status_code=200) is None


if __name__ == "__main__":
    test_detect_autonomy_mode_english_triggers()
    test_detect_autonomy_mode_chinese_triggers()
    test_detect_autonomy_mode_default_checkpoint()
    test_hard_safety_gates_and_4k_upscale()
    test_safety_boundary_simulation()
    test_platform_error_signal_classification()
    print("Tier 3 Tests PASSED: Autonomy mode transitions and zero-retry safety gates verified.")
