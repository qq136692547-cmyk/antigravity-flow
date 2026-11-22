"""
Tier 2: Live Credit Sniffer & Plan Badge Parsing Tests
"""

from tests.conftest import parse_credit_cost, parse_plan_badge, should_auto_proceed


def test_credit_sniffer_standard_patterns():
    test_cases = [
        ("Generating will use 0 credits", 0),
        ("Generating will use 1 credit", 1),
        ("Generating will use 10 credits", 10),
        ("Generating will use 15 credits", 15),
        ("Generating will use 20 credits", 20),
        ("Generating will use 50 credits", 50),
        ("Costs 0 credits", 0),
        ("Costs 20 credits", 20),
        ("0 credits", 0),
        ("1 credit", 1),
        ("50 credits", 50),
    ]
    for text, expected in test_cases:
        assert parse_credit_cost(text) == expected, f"Failed parsing: {text}"


def test_credit_sniffer_html_noise():
    noisy_cases = [
        ("<div class='footer-cost'>Generating will use 0 credits</div>", 0),
        ("<p>Settings: Mode=Video | Costs 15 credits | Length=8s</p>", 15),
        ("<span>Generating will use 50 credits (4K Upscaled)</span>", 50),
        ("   Generating will use 0 credits  \n", 0),
    ]
    for text, expected in noisy_cases:
        assert parse_credit_cost(text) == expected, f"Failed parsing noisy text: {text}"


def test_credit_sniffer_empty_and_invalid():
    assert parse_credit_cost("") is None
    assert parse_credit_cost("No cost information available here") is None
    assert parse_credit_cost("Free tier with daily quota") is None


def test_plan_badge_parsing():
    assert parse_plan_badge("ULTRA") == "ULTRA"
    assert parse_plan_badge("Google AI Ultra · Active") == "ULTRA"
    assert parse_plan_badge("PRO") == "PRO"
    assert parse_plan_badge("Google AI Pro (One AI Premium)") == "PRO"
    assert parse_plan_badge("") == "FREE"
    assert parse_plan_badge("Free Account") == "FREE"
    assert parse_plan_badge("Starter Tier") == "FREE"


def test_should_auto_proceed_logic():
    # 0 credit is always auto-proceed
    can_proceed, reason = should_auto_proceed(credit_cost=0, autonomy_mode="checkpoint")
    assert can_proceed is True
    assert "0-credit" in reason

    # >0 credit in checkpoint mode stops for confirmation
    can_proceed, reason = should_auto_proceed(credit_cost=15, autonomy_mode="checkpoint")
    assert can_proceed is False
    assert "Checkpoint confirmation required" in reason

    # >0 credit in auto mode proceeds automatically
    can_proceed, reason = should_auto_proceed(credit_cost=15, autonomy_mode="auto")
    assert can_proceed is True
    assert "Auto mode override active" in reason

    # 4K Upscale (50 credits) MUST stop even if autonomy_mode == 'auto'
    can_proceed, reason = should_auto_proceed(credit_cost=50, autonomy_mode="auto", is_upscale_4k=True)
    assert can_proceed is False
    assert "4K Upscale" in reason


if __name__ == "__main__":
    test_credit_sniffer_standard_patterns()
    test_credit_sniffer_html_noise()
    test_credit_sniffer_empty_and_invalid()
    test_plan_badge_parsing()
    test_should_auto_proceed_logic()
    print("Tier 2 Tests PASSED: Live credit sniffer and plan badge parsing verified.")
