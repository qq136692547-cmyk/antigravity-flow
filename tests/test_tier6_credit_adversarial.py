"""
Tier 6: Live Grounding & Credit Adversarial Hardening Tests
"""

from pathlib import Path
from tests.conftest import (
    PLUGIN_ROOT,
    MAX_CREDIT_CEILING,
    MAX_SESSION_CREDITS,
    PACING_DELAY_SECONDS,
    is_valid_credit_cost,
    parse_credit_cost,
    calculate_upscale_cost,
    should_auto_proceed,
    validate_scene_operation_order,
)


def test_nan_credits_fail_closed():
    """Verify that 'NaN credits' or hydration lag halts automation fail-closed."""
    nan_cases = [
        "Generating will use NaN credits",
        "Costs NaN credits",
        "<div class='cost'>Generating will use NaN credits</div>",
        "NaN credits",
        "Generating will use undefined credits",
        "Costs null credits",
        "Generating will use infinity credits",
    ]
    for text in nan_cases:
        parsed = parse_credit_cost(text)
        assert parsed is None, f"Expected None for invalid token case '{text}', got {parsed}"
        
        can_proceed, reason = should_auto_proceed(credit_cost=parsed, autonomy_mode="auto")
        assert can_proceed is False
        assert "Fail-closed" in reason


def test_nano_banana_no_false_positive():
    """Verify that 'Nano Banana' model label does not trigger a false-positive NaN lockout."""
    nano_cases = [
        ("Nano Banana 2.1 · Generating will use 0 credits", 0),
        ("Generating will use 0 credits (Nano Banana Pro)", 0),
        ("Nano Banana 2 Lite: Costs 0 credits", 0),
        ("Generating will use 1 credit · Nano Banana 2.1", 1),
    ]
    for text, expected in nano_cases:
        parsed = parse_credit_cost(text)
        assert parsed == expected, f"Failed parsing Nano Banana credit '{text}', got {parsed}"


def test_unanchored_and_comma_balance_rejection():
    """Verify comma-separated account balances never fail-open into 0 credits."""
    balance_cases = [
        "1,000 credits remaining",
        "10,000 credits",
        "25,000 credits remaining",
        "Account balance: 1,000 credits",
    ]
    for text in balance_cases:
        parsed = parse_credit_cost(text)
        assert parsed is None, f"Comma balance '{text}' must not be parsed as {parsed}"


def test_negative_and_decimal_rejection():
    """Verify negative and fractional credits fail-closed immediately."""
    corrupted_cases = [
        "Generating will use -10 credits",
        "Costs -5 credits",
        "Generating will use 12.5 credits",
        "Costs 0.5 credits",
        "Generar usará 20 créditos",
    ]
    for text in corrupted_cases:
        parsed = parse_credit_cost(text)
        assert parsed is None, f"Corrupted credit '{text}' must return None, got {parsed}"


def test_singular_and_standard_credit_parsing():
    """Verify singular '1 credit' and standard anchored credit texts parse accurately."""
    valid_cases = [
        ("Generating will use 1 credit", 1),
        ("Costs 1 credit", 1),
        ("1 credit", 1),
        ("0 credits", 0),
        ("<span>Generating will use 20 credits</span>", 20),
    ]
    for text, expected in valid_cases:
        parsed = parse_credit_cost(text)
        assert parsed == expected, f"Failed parsing credit text '{text}'"
        assert is_valid_credit_cost(parsed) is True


def test_credit_ceiling_and_session_cap():
    """Verify single-action 60 credit ceiling and cumulative session spend ceiling."""
    assert MAX_CREDIT_CEILING == 60
    assert MAX_SESSION_CREDITS == 120

    # Single-action 60 allowed, 61 halted
    can_proceed, _ = should_auto_proceed(credit_cost=60, autonomy_mode="auto")
    assert can_proceed is True

    can_proceed, reason = should_auto_proceed(credit_cost=61, autonomy_mode="auto")
    assert can_proceed is False
    assert "max credit ceiling" in reason

    # Cumulative session ceiling: spent 100, next 25 -> total 125 > 120 -> halts
    can_proceed, reason = should_auto_proceed(
        credit_cost=25,
        autonomy_mode="auto",
        session_spent_credits=100,
        max_session_credits=120,
    )
    assert can_proceed is False
    assert "cumulative session ceiling" in reason


def test_duration_upscale_math_and_gating():
    """Verify dynamic duration upscale pricing (>10s) and tier subscription gating."""
    # 720p / 1080p math
    assert calculate_upscale_cost(8, "720p") == 0
    assert calculate_upscale_cost(10, "720p") == 0
    assert calculate_upscale_cost(15, "720p") == 5
    assert calculate_upscale_cost(8, "1080p") == 0
    assert calculate_upscale_cost(15, "1080p") == 5

    # 4K / UHD math
    assert calculate_upscale_cost(8, "4K") == 50
    assert calculate_upscale_cost(15, "4K") == 75
    assert calculate_upscale_cost(15, "UHD") == 75

    # Fail-closed on invalid duration or resolution
    assert calculate_upscale_cost(-5, "1080p") is None
    assert calculate_upscale_cost(10, "144p") is None

    # Tier gating: 4K requires Ultra
    can_proceed, reason = should_auto_proceed(
        credit_cost=50,
        autonomy_mode="auto",
        account_tier="pro",
        upscale_resolution="4K",
    )
    assert can_proceed is False
    assert "requires Google AI Ultra" in reason

    # Tier gating: 1080p video upscale blocked on Free
    can_proceed, reason = should_auto_proceed(
        credit_cost=0,
        autonomy_mode="auto",
        account_tier="free",
        upscale_resolution="1080p",
    )
    assert can_proceed is False
    assert "requires Google AI Plus, Pro, or Ultra" in reason

    # 4K on Ultra requires explicit single-turn confirmation
    can_proceed, reason = should_auto_proceed(
        credit_cost=50,
        autonomy_mode="auto",
        account_tier="ultra",
        upscale_duration=10,
        upscale_resolution="4K",
    )
    assert can_proceed is False
    assert "4K Upscale" in reason


def test_rate_limit_pacing_delay():
    """Verify 2.5s pacing delay constant to avoid rolling 24h velocity lockouts."""
    assert PACING_DELAY_SECONDS >= 2.0
    assert PACING_DELAY_SECONDS == 2.5


def test_scene_editor_extend_before_edit_invariant():
    """Verify that inline video edits cannot occur after clip extension across all edit modes."""
    valid_seq = ["add_clip", "in-place edit", "extend"]
    valid, msg = validate_scene_operation_order(valid_seq)
    assert valid is True

    for forbidden_op in ["in-place edit", "insert_object", "remove_actor", "camera_reframe"]:
        invalid_seq = ["add_clip", "extend", forbidden_op]
        valid, msg = validate_scene_operation_order(invalid_seq)
        assert valid is False, f"Failed blocking {forbidden_op} after extend"
        assert "Flow invariant violated" in msg


def test_live_rules_markdown_consistency():
    """Verify that production Markdown rule files contain hardened constants and live model tags."""
    agents_md = (PLUGIN_ROOT / "rules" / "AGENTS.md").read_text(encoding="utf-8")
    assert "MAX_CREDIT_CEILING" in agents_md
    assert "MAX_SESSION_CREDITS" in agents_md
    assert "Omni 1.2 Flash" in agents_md
    assert "Dec 5, 2026" in agents_md
    assert "PLUS" in agents_md
    assert "?hl=en" in agents_md

    flow_generate_md = (PLUGIN_ROOT / "skills" / "flow-generate" / "SKILL.md").read_text(encoding="utf-8")
    assert "MAX_CREDIT_CEILING" in flow_generate_md
    assert "Omni 1.2 Flash" in flow_generate_md


if __name__ == "__main__":
    test_nan_credits_fail_closed()
    test_nano_banana_no_false_positive()
    test_unanchored_and_comma_balance_rejection()
    test_negative_and_decimal_rejection()
    test_singular_and_standard_credit_parsing()
    test_credit_ceiling_and_session_cap()
    test_duration_upscale_math_and_gating()
    test_rate_limit_pacing_delay()
    test_scene_editor_extend_before_edit_invariant()
    test_live_rules_markdown_consistency()
    print("Tier 6 Tests PASSED: All adversarial hardening and live invariants verified.")
