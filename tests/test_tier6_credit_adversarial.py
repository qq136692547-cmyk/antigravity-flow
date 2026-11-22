"""
Tier 6: Live Grounding & Credit Adversarial Hardening Tests
"""

from tests.conftest import (
    MAX_CREDIT_CEILING,
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
    ]
    for text in nan_cases:
        parsed = parse_credit_cost(text)
        assert parsed is None, f"Expected None for NaN case '{text}', got {parsed}"
        
        # When parsed is None, should_auto_proceed MUST return False even in auto mode
        can_proceed, reason = should_auto_proceed(credit_cost=parsed, autonomy_mode="auto")
        assert can_proceed is False
        assert "Fail-closed" in reason


def test_singular_credit_parsing():
    """Verify singular '1 credit' is parsed accurately."""
    singular_cases = [
        ("Generating will use 1 credit", 1),
        ("Costs 1 credit", 1),
        ("1 credit", 1),
        ("<span>Costs 1 credit</span>", 1),
    ]
    for text, expected in singular_cases:
        parsed = parse_credit_cost(text)
        assert parsed == expected, f"Failed parsing singular credit '{text}'"
        assert is_valid_credit_cost(parsed) is True


def test_credit_ceiling_protection():
    """Verify hard ceiling of 60 credits protects shared Antigravity credit pool."""
    assert MAX_CREDIT_CEILING == 60
    
    # 60 credits in auto mode is allowed
    can_proceed, _ = should_auto_proceed(credit_cost=60, autonomy_mode="auto")
    assert can_proceed is True
    
    # 61 credits in auto mode MUST halt for explicit user confirmation
    can_proceed, reason = should_auto_proceed(credit_cost=61, autonomy_mode="auto")
    assert can_proceed is False
    assert "max credit ceiling" in reason
    
    # 75 credits (e.g. 15s 4K) in auto mode MUST halt
    can_proceed, reason = should_auto_proceed(credit_cost=75, autonomy_mode="auto")
    assert can_proceed is False
    assert "max credit ceiling" in reason


def test_duration_upscale_math_and_gating():
    """Verify dynamic duration upscale pricing (>10s) and mandatory gating."""
    # 1080p math
    assert calculate_upscale_cost(8, "1080p") == 0
    assert calculate_upscale_cost(10, "1080p") == 0
    assert calculate_upscale_cost(11, "1080p") == 1
    assert calculate_upscale_cost(15, "1080p") == 5

    # 4K math
    assert calculate_upscale_cost(8, "4K") == 50
    assert calculate_upscale_cost(10, "4K") == 50
    assert calculate_upscale_cost(11, "4K") == 55
    assert calculate_upscale_cost(15, "4K") == 75

    # Gating: 10s 1080p (0 credits) allowed in auto
    can_proceed, _ = should_auto_proceed(
        credit_cost=0,
        autonomy_mode="auto",
        is_upscale_4k=False,
        upscale_duration=10,
        upscale_resolution="1080p"
    )
    assert can_proceed is True

    # Gating: 15s 1080p (>10s) MUST halt even in auto mode
    can_proceed, reason = should_auto_proceed(
        credit_cost=5,
        autonomy_mode="auto",
        is_upscale_4k=False,
        upscale_duration=15,
        upscale_resolution="1080p"
    )
    assert can_proceed is False
    assert "Extended upscale" in reason

    # Gating: 4K upscales always halt
    can_proceed, reason = should_auto_proceed(
        credit_cost=50,
        autonomy_mode="auto",
        is_upscale_4k=True,
        upscale_duration=10,
        upscale_resolution="4K"
    )
    assert can_proceed is False


def test_rate_limit_pacing_delay():
    """Verify 2.5s pacing delay constant to avoid rolling 24h velocity lockouts."""
    assert PACING_DELAY_SECONDS >= 2.0
    assert PACING_DELAY_SECONDS == 2.5


def test_scene_editor_extend_before_edit_invariant():
    """Verify that inline video edits cannot occur after clip extension."""
    valid_seq = ["add_clip", "in-place edit", "extend"]
    valid, msg = validate_scene_operation_order(valid_seq)
    assert valid is True

    invalid_seq = ["add_clip", "extend", "in-place edit"]
    valid, msg = validate_scene_operation_order(invalid_seq)
    assert valid is False
    assert "Flow invariant violated" in msg


if __name__ == "__main__":
    test_nan_credits_fail_closed()
    test_singular_credit_parsing()
    test_credit_ceiling_protection()
    test_duration_upscale_math_and_gating()
    test_rate_limit_pacing_delay()
    test_scene_editor_extend_before_edit_invariant()
    print("Tier 6 Tests PASSED: Credit adversarial hardening and live invariants verified.")
