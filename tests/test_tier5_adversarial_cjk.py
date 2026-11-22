"""
Tier 5: Adversarial Hardening, Zero-CJK Verification & ReDoS Safety Tests
"""

import re
import time
from pathlib import Path
from tests.conftest import (
    CREDIT_SNIFFER_PATTERNS,
    VELOCITY_ADVERB_PATTERN,
    NUMERIC_WEIGHT_PATTERN,
    CONFLICTING_CAMERA_PATTERNS,
)

PLUGIN_ROOT = Path(__file__).resolve().parent.parent

# CJK Unicode range: unified ideographs, extension A, compatibility ideographs
CJK_PATTERN = re.compile(r"[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]")

DEPRECATED_MODELS = [
    "gemini-3-flash-preview",
    "gemini-3.1-pro-preview",
    "palm-2",
    "gemini-1.0",
    "gemini-1.5-flash-preview",
]


def test_zero_cjk_in_english_codebase():
    """Ensure zero CJK characters exist in English plugin core files."""
    files_to_check = [
        PLUGIN_ROOT / "plugin.json",
        PLUGIN_ROOT / ".gitignore",
        PLUGIN_ROOT / "rules" / "AGENTS.md",
    ]
    # Add all skill markdown files
    for skill_file in (PLUGIN_ROOT / "skills").rglob("*.md"):
        files_to_check.append(skill_file)

    for file_path in files_to_check:
        assert file_path.exists(), f"File {file_path} must exist"
        content = file_path.read_text(encoding="utf-8")
        matches = CJK_PATTERN.findall(content)
        assert len(matches) == 0, f"Found {len(matches)} CJK characters in {file_path}: {matches[:10]}"


def test_zero_cjk_in_readme_english_section():
    """Ensure zero CJK characters exist in the primary English section of README.md."""
    readme_path = PLUGIN_ROOT / "README.md"
    assert readme_path.exists(), "README.md must exist"
    
    content = readme_path.read_text(encoding="utf-8")
    # Split at Chinese documentation section if present
    sections = re.split(r"\n---\s*\n(?=#|\s*##\s*[\u4e00-\u9fff])", content)
    english_section = sections[0]
    
    matches = CJK_PATTERN.findall(english_section)
    assert len(matches) == 0, f"Found CJK characters in English README section: {matches[:10]}"


def test_redos_safety_on_pathological_inputs():
    """Verify regex patterns do not suffer from catastrophic ReDoS backtracking."""
    pathological_sniff = "Generating will use " + ("9" * 30000) + " credits?"
    pathological_prompt = ("slow steady camera " * 5000) + "@hero walks in field (pan:1.4)"
    
    # 1. Test Credit Sniffer
    t0 = time.time()
    for pattern in CREDIT_SNIFFER_PATTERNS:
        pattern.search(pathological_sniff)
    elapsed_sniffer = (time.time() - t0) * 1000
    assert elapsed_sniffer < 50.0, f"Credit sniffer took {elapsed_sniffer:.2f}ms (potential ReDoS)"

    # 2. Test Velocity Adverbs
    t0 = time.time()
    VELOCITY_ADVERB_PATTERN.search(pathological_prompt)
    elapsed_velocity = (time.time() - t0) * 1000
    assert elapsed_velocity < 50.0, f"Velocity adverb check took {elapsed_velocity:.2f}ms"

    # 3. Test Numeric Weights
    t0 = time.time()
    NUMERIC_WEIGHT_PATTERN.findall(pathological_prompt)
    elapsed_weights = (time.time() - t0) * 1000
    assert elapsed_weights < 50.0, f"Numeric weight check took {elapsed_weights:.2f}ms"

    # 4. Test Camera Direction Conflicts
    t0 = time.time()
    for pat_a, pat_b in CONFLICTING_CAMERA_PATTERNS:
        pat_a.search(pathological_prompt)
        pat_b.search(pathological_prompt)
    elapsed_camera = (time.time() - t0) * 1000
    assert elapsed_camera < 50.0, f"Camera conflict check took {elapsed_camera:.2f}ms"


def test_no_deprecated_models_referenced():
    """Verify that retired preview models are not referenced in active rules or skills."""
    skills_dir = PLUGIN_ROOT / "skills"
    for md_file in skills_dir.rglob("*.md"):
        content = md_file.read_text(encoding="utf-8").lower()
        for dep in DEPRECATED_MODELS:
            assert dep not in content, f"Deprecated model '{dep}' found in {md_file}"


if __name__ == "__main__":
    test_zero_cjk_in_english_codebase()
    test_zero_cjk_in_readme_english_section()
    test_redos_safety_on_pathological_inputs()
    test_no_deprecated_models_referenced()
    print("Tier 5 Tests PASSED: Adversarial hardening, zero-CJK, and ReDoS safety verified.")
