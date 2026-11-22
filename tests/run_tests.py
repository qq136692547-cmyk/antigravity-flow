"""
Master Test Runner for antigravity-flow (5-Tier Test Suite)
"""

import sys
import time
from pathlib import Path

# Add plugin root to sys.path
PLUGIN_ROOT = Path(__file__).resolve().parent.parent
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from tests.test_tier1_manifest_schema import (
    test_plugin_json_schema,
    test_rules_agents_md,
    test_skills_frontmatter_and_presence,
    test_references_presence,
)
from tests.test_tier2_credit_sniffer import (
    test_credit_sniffer_standard_patterns,
    test_credit_sniffer_html_noise,
    test_credit_sniffer_empty_and_invalid,
    test_plan_badge_parsing,
    test_should_auto_proceed_logic,
)
from tests.test_tier3_autonomy_modes import (
    test_detect_autonomy_mode_english_triggers,
    test_detect_autonomy_mode_chinese_triggers,
    test_detect_autonomy_mode_default_checkpoint,
    test_hard_safety_gates_and_4k_upscale,
    test_safety_boundary_simulation,
)
from tests.test_tier4_storyboard_compiler import (
    test_valid_veo_prompt_5_slot_grammar,
    test_reject_numeric_weights,
    test_reject_conflicting_camera_trajectories,
    test_velocity_adverb_detection,
    test_storyboard_markdown_parser,
)
from tests.test_tier5_adversarial_cjk import (
    test_zero_cjk_in_english_codebase,
    test_zero_cjk_in_readme_english_section,
    test_redos_safety_on_pathological_inputs,
    test_no_deprecated_models_referenced,
)


def run_all_tiers():
    tiers = [
        ("Tier 1: Manifest Schema & Skill Integrity", [
            ("plugin_json_schema", test_plugin_json_schema),
            ("rules_agents_md", test_rules_agents_md),
            ("skills_frontmatter_and_presence", test_skills_frontmatter_and_presence),
            ("references_presence", test_references_presence),
        ]),
        ("Tier 2: Live Credit Sniffer & Plan Badge Parsing", [
            ("credit_sniffer_standard_patterns", test_credit_sniffer_standard_patterns),
            ("credit_sniffer_html_noise", test_credit_sniffer_html_noise),
            ("credit_sniffer_empty_and_invalid", test_credit_sniffer_empty_and_invalid),
            ("plan_badge_parsing", test_plan_badge_parsing),
            ("should_auto_proceed_logic", test_should_auto_proceed_logic),
        ]),
        ("Tier 3: Autonomy Modes & Safety Boundaries", [
            ("detect_autonomy_mode_english_triggers", test_detect_autonomy_mode_english_triggers),
            ("detect_autonomy_mode_chinese_triggers", test_detect_autonomy_mode_chinese_triggers),
            ("detect_autonomy_mode_default_checkpoint", test_detect_autonomy_mode_default_checkpoint),
            ("hard_safety_gates_and_4k_upscale", test_hard_safety_gates_and_4k_upscale),
            ("safety_boundary_simulation", test_safety_boundary_simulation),
        ]),
        ("Tier 4: Veo 3.1 5-Slot Grammar & Storyboard Parsing", [
            ("valid_veo_prompt_5_slot_grammar", test_valid_veo_prompt_5_slot_grammar),
            ("reject_numeric_weights", test_reject_numeric_weights),
            ("reject_conflicting_camera_trajectories", test_reject_conflicting_camera_trajectories),
            ("velocity_adverb_detection", test_velocity_adverb_detection),
            ("storyboard_markdown_parser", test_storyboard_markdown_parser),
        ]),
        ("Tier 5: Adversarial Hardening & Zero-CJK Verification", [
            ("zero_cjk_in_english_codebase", test_zero_cjk_in_english_codebase),
            ("zero_cjk_in_readme_english_section", test_zero_cjk_in_readme_english_section),
            ("redos_safety_on_pathological_inputs", test_redos_safety_on_pathological_inputs),
            ("no_deprecated_models_referenced", test_no_deprecated_models_referenced),
        ]),
    ]

    total_passed = 0
    total_failed = 0
    start_time = time.time()

    print("=" * 70)
    print("STARTING 5-TIER VERIFICATION SUITE FOR antigravity-flow")
    print(f"Target Root: {PLUGIN_ROOT}")
    print("=" * 70)

    for tier_name, tests in tiers:
        print(f"\n[+] Running {tier_name} ({len(tests)} tests)...")
        tier_passed = 0
        tier_failed = 0
        for test_name, test_fn in tests:
            try:
                test_fn()
                print(f"    ✓ {test_name}")
                tier_passed += 1
                total_passed += 1
            except Exception as e:
                print(f"    ✗ {test_name}: {e}")
                tier_failed += 1
                total_failed += 1
        print(f"    Result: {tier_passed}/{len(tests)} passed.")
        if tier_failed > 0:
            print(f"    [!] Failures detected in {tier_name}")

    elapsed = time.time() - start_time
    print("\n" + "=" * 70)
    print(f"SUMMARY: {total_passed} Passed, {total_failed} Failed in {elapsed:.3f}s")
    print("=" * 70)

    if total_failed > 0:
        sys.exit(1)
    else:
        print("ALL TIERS PASSED WITH 100% SUCCESS RATE!")
        sys.exit(0)


if __name__ == "__main__":
    run_all_tiers()
