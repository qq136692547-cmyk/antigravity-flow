"""
Shared fixtures, regex parsers, and utilities for the antigravity-flow 5-tier test suite.
"""

import os
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

PLUGIN_ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------
# Regex Definitions for Live Credit Sniffer & Autonomy Modes
# ---------------------------------------------------------

CREDIT_SNIFFER_PATTERNS = [
    re.compile(r"(?:generating\s+will\s+use|costs?)\s+(\d+)\s+credits?", re.IGNORECASE),
    re.compile(r"\b(\d+)\s+credits?\b", re.IGNORECASE),
]

AUTO_MODE_CUES = [
    re.compile(r"\b(?:auto\s+mode|full[- ]auto|unattended|run\s+unattended|without\s+asking|batch\s+generate\s+all)\b", re.IGNORECASE),
    re.compile(r"全自动|免打扰|自动模式|别问我|无需确认", re.IGNORECASE),
]

# ---------------------------------------------------------
# Helper Functions: Credit Sniffer & Autonomy Decisions
# ---------------------------------------------------------

def parse_credit_cost(ui_text: str) -> Optional[int]:
    """Parse integer credit cost from live UI text string."""
    if not ui_text:
        return None
    for pattern in CREDIT_SNIFFER_PATTERNS:
        match = pattern.search(ui_text)
        if match:
            return int(match.group(1))
    return None


def parse_plan_badge(dom_badge_text: str) -> str:
    """Identify account plan tier from top header badge."""
    clean = (dom_badge_text or "").strip().upper()
    if "ULTRA" in clean:
        return "ULTRA"
    if "PRO" in clean:
        return "PRO"
    return "FREE"


def detect_autonomy_mode(prompt: str, default_mode: str = "checkpoint") -> str:
    """Detect whether user requested auto mode from prompt cues."""
    if not prompt:
        return default_mode
    for cue in AUTO_MODE_CUES:
        if cue.search(prompt):
            return "auto"
    return default_mode


def should_auto_proceed(credit_cost: int, autonomy_mode: str, is_upscale_4k: bool = False) -> Tuple[bool, str]:
    """
    Evaluate whether browser automation can proceed without pausing:
    Returns (can_proceed, reason).
    """
    if is_upscale_4k:
        return False, "4K Upscale (50 credits) requires explicit single-turn confirmation."
    if credit_cost == 0:
        return True, "0-credit action allowed in auto mode."
    if autonomy_mode == "auto":
        return True, f"Auto mode override active: consuming {credit_cost} credits."
    return False, f"Generation costs {credit_cost} credits. Checkpoint confirmation required."


# ---------------------------------------------------------
# Veo 3.1 5-Slot Grammar & Prompt Compiler
# ---------------------------------------------------------

VELOCITY_ADVERB_PATTERN = re.compile(
    r"\b(subtle|barely\s+perceptible|smooth|steady|gentle|measured|controlled|cinematic|deliberate|pronounced|brisk|rapid|sweeping|dramatic)\b",
    re.IGNORECASE
)

NUMERIC_WEIGHT_PATTERN = re.compile(
    r"(\(\s*[^)]+:\s*\d+(?:\.\d+)?\s*\)|::\s*\d+(?:\.\d+)?|\[\s*[^\]]+::\s*\d+)",
    re.IGNORECASE
)

CONFLICTING_CAMERA_PATTERNS = [
    (re.compile(r"\bpan(?:ning)?\s+left\b", re.IGNORECASE), re.compile(r"\bpan(?:ning)?\s+right\b", re.IGNORECASE)),
    (re.compile(r"\bdolly\s+in\b", re.IGNORECASE), re.compile(r"\bdolly\s+out\b", re.IGNORECASE)),
    (re.compile(r"\bcrane\s+up\b", re.IGNORECASE), re.compile(r"\bcrane\s+down\b", re.IGNORECASE)),
]

AUDIO_PREFIX_PATTERN = re.compile(
    r"(Ambient\s+noise:\s*[^.]+\.|SFX:\s*[^.]+\.|@[a-zA-Z0-9_]+\s+speaks[^:]*:\s*\"[^\"]+\"[.]?)",
    re.IGNORECASE
)


def validate_veo_prompt_syntax(prompt: str) -> Dict[str, Any]:
    """
    Validate a Veo 3.1 prompt against lowering rules and syntax guidelines.
    """
    issues = []
    
    # 1. Check for forbidden Midjourney/SD numeric weights
    weight_matches = NUMERIC_WEIGHT_PATTERN.findall(prompt)
    if weight_matches:
        issues.append(f"Contains forbidden numeric weights: {weight_matches}")
        
    # 2. Check for conflicting camera trajectories
    for pat_a, pat_b in CONFLICTING_CAMERA_PATTERNS:
        if pat_a.search(prompt) and pat_b.search(prompt):
            issues.append(f"Contradictory camera directions detected: {pat_a.pattern} and {pat_b.pattern}")
            
    # 3. Check for presence of velocity adverbs
    has_velocity = bool(VELOCITY_ADVERB_PATTERN.search(prompt))
    
    # 4. Check for trailing audio sentences
    audio_matches = AUDIO_PREFIX_PATTERN.findall(prompt)
    
    # 5. Extract unique @handles preserving order
    all_handles = re.findall(r"@([a-zA-Z0-9_]+)", prompt)
    unique_handles = list(dict.fromkeys(all_handles))
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "has_velocity_adverb": has_velocity,
        "audio_elements": audio_matches,
        "handles": unique_handles,
        "handle_count": len(unique_handles),
    }


def parse_storyboard_markdown(markdown_text: str) -> Dict[str, Any]:
    """Parse structured storyboard.md into Python dictionary."""
    result = {
        "title": None,
        "project_name": None,
        "aspect_ratio": None,
        "autonomy_mode": "checkpoint",
        "ingredients": [],
        "shots": []
    }
    
    title_match = re.search(r"^#\s+Flow Production Plan:\s*(.+)$", markdown_text, re.MULTILINE)
    if title_match:
        result["title"] = title_match.group(1).strip()
        
    proj_match = re.search(r"-\s+\*\*Project Name\*\*:\s*(.+)$", markdown_text, re.MULTILINE)
    if proj_match:
        result["project_name"] = proj_match.group(1).strip()
        
    ratio_match = re.search(r"-\s+\*\*Aspect Ratio\*\*:\s*([0-9:]+)", markdown_text, re.MULTILINE)
    if ratio_match:
        result["aspect_ratio"] = ratio_match.group(1).strip()
        
    auto_match = re.search(r"-\s+\*\*Autonomy Mode\*\*:\s*(checkpoint|auto)", markdown_text, re.MULTILINE)
    if auto_match:
        result["autonomy_mode"] = auto_match.group(1).strip()
        
    # Parse shot sections: ### S01 — <Title>
    shot_blocks = re.findall(r"###\s+(S\d+)\s*—\s*([^\n]+)\n(.*?)(?=(?:###\s+S\d+|\Z))", markdown_text, re.DOTALL)
    for shot_id, shot_title, shot_body in shot_blocks:
        prompt_match = re.search(r"-\s+\*\*Prompt\*\*:\s*(.+)", shot_body)
        model_match = re.search(r"-\s+\*\*Model\*\*:\s*(.+)", shot_body)
        video_type_match = re.search(r"-\s+\*\*Video Type\*\*:\s*(.+)", shot_body)
        
        result["shots"].append({
            "id": shot_id.strip(),
            "title": shot_title.strip(),
            "video_type": video_type_match.group(1).strip() if video_type_match else "Ingredients",
            "model": model_match.group(1).strip() if model_match else "Omni 1.2 Flash",
            "prompt": prompt_match.group(1).strip() if prompt_match else "",
        })
        
    return result
