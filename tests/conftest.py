"""
Shared fixtures, regex parsers, and utilities for the antigravity-flow 6-tier test suite.
"""

import os
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

PLUGIN_ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------
# Constants: Safety Ceilings, Pacing & Boundaries
# ---------------------------------------------------------

MAX_CREDIT_CEILING = 60
PACING_DELAY_SECONDS = 2.5
MAX_SESSION_CREDITS = 120

# ---------------------------------------------------------
# Regex Definitions for Live Credit Sniffer & Autonomy Modes
# ---------------------------------------------------------

INVALID_COST_TOKEN_RE = re.compile(r"\b(?:nan|undefined|null|infinity)\b", re.IGNORECASE)

ANCHORED_CREDIT_PATTERNS = [
    re.compile(r"(?:generating\s+will\s+use|costs?)\s+(?<![\d.,-])(\d+)(?![\d.,])\s+credits?\b", re.IGNORECASE),
    re.compile(r"^\s*(?<![\d.,-])(\d+)(?![\d.,])\s+credits?\s*$", re.IGNORECASE),
    re.compile(r">\s*(?<![\d.,-])(\d+)(?![\d.,])\s+credits?\s*<", re.IGNORECASE),
]

# Backward-compatible alias
CREDIT_SNIFFER_PATTERNS = ANCHORED_CREDIT_PATTERNS

AUTO_MODE_CUES = [
    re.compile(r"\b(?:auto\s+mode|full[- ]auto|unattended|run\s+unattended|without\s+asking|batch\s+generate\s+all)\b", re.IGNORECASE),
    re.compile(r"全自动|免打扰|自动模式|别问我|无需确认", re.IGNORECASE),
]

INLINE_EDIT_TOKENS = ("edit", "in-place", "inline", "insert", "remove", "camera")

# ---------------------------------------------------------
# Helper Functions: Credit Sniffer & Autonomy Decisions
# ---------------------------------------------------------

def is_valid_credit_cost(val: Any) -> bool:
    """Validate that credit cost is a non-negative integer and not a boolean."""
    return isinstance(val, int) and val >= 0 and not isinstance(val, bool)


def parse_credit_cost(ui_text: str) -> Optional[int]:
    """
    Parse integer credit cost from live UI text string.
    Hardened Fail-Closed Logic:
    - Rejects invalid tokens with word boundaries (NaN, undefined, null, infinity).
    - Prevents false-positives on 'Nano Banana'.
    - Refuses comma-separated balances ('1,000 credits' -> None).
    - Refuses negative numbers ('-10 credits' -> None) and decimals ('12.5 credits' -> None).
    """
    if not isinstance(ui_text, str) or not ui_text.strip():
        return None
    if INVALID_COST_TOKEN_RE.search(ui_text):
        return None
    for pattern in ANCHORED_CREDIT_PATTERNS:
        match = pattern.search(ui_text)
        if match:
            try:
                val = int(match.group(1))
                if val >= 0:
                    return val
            except ValueError:
                return None
    return None


def parse_plan_badge(dom_badge_text: str) -> str:
    """Identify account plan tier from top header badge."""
    clean = (dom_badge_text or "").strip().upper()
    if "ULTRA" in clean:
        return "ULTRA"
    if "PRO" in clean:
        return "PRO"
    if "PLUS" in clean:
        return "PLUS"
    return "FREE"


def detect_autonomy_mode(prompt: str, default_mode: str = "checkpoint") -> str:
    """Detect whether user requested auto mode from prompt cues."""
    if not prompt:
        return default_mode
    for cue in AUTO_MODE_CUES:
        if cue.search(prompt):
            return "auto"
    return default_mode


def calculate_upscale_cost(duration_seconds: int, resolution: str) -> Optional[int]:
    """
    Calculate upscale credit cost according to live duration rules:
    - 720p / 1080p: 0 credits for 1-10s; 1 credit per second past 10s.
    - 4K / UHD / 2160p: 50 credits for 1-10s; 50 + 5 credits per second past 10s.
    Returns None (fail-closed) on invalid duration (<=0) or unrecognized resolution.
    """
    if not is_valid_credit_cost(duration_seconds) or duration_seconds <= 0:
        return None
    res = (resolution or "").strip().lower()
    if "720" in res or "1080" in res:
        return 0 if duration_seconds <= 10 else (duration_seconds - 10) * 1
    if "4k" in res or "2160" in res or "uhd" in res:
        return 50 if duration_seconds <= 10 else 50 + (duration_seconds - 10) * 5
    return None


def should_auto_proceed(
    credit_cost: Optional[int],
    autonomy_mode: str,
    account_tier: str = "ultra",
    is_upscale_4k: bool = False,
    upscale_duration: Optional[int] = None,
    upscale_resolution: Optional[str] = None,
    session_spent_credits: int = 0,
    max_session_credits: int = MAX_SESSION_CREDITS,
) -> Tuple[bool, str]:
    """
    Evaluate whether browser automation can proceed without pausing:
    - Fail-Closed: Invalid/unparsed cost halts immediately.
    - Tier Gating: 4K requires Ultra; 720p/1080p video upscaling requires Plus/Pro/Ultra.
    - Upscale Gating: 4K or duration > 10s halts for checkpoint confirmation.
    - Single Ceiling: Cost > MAX_CREDIT_CEILING (60) halts.
    - Session Ceiling: Cumulative session spend > max_session_credits halts.
    """
    if not is_valid_credit_cost(credit_cost):
        return False, "Fail-closed: Unable to determine credit cost (possible NaN or unparsed UI). Checkpoint pause required."

    res_norm = (upscale_resolution or "").strip().lower()
    tier_norm = (account_tier or "ultra").strip().lower()
    effective_4k = is_upscale_4k or any(tok in res_norm for tok in ("4k", "2160", "uhd"))

    if effective_4k:
        if "ultra" not in tier_norm:
            return False, "Blocked: 4K Upscale requires Google AI Ultra subscription."
        return False, f"4K Upscale ({credit_cost} credits) requires explicit single-turn confirmation."

    if ("720" in res_norm or "1080" in res_norm) and tier_norm == "free":
        return False, "Blocked: 720p/1080p video upscaling requires Google AI Plus, Pro, or Ultra."

    if upscale_duration is not None and upscale_duration > 10:
        return False, f"Extended upscale ({upscale_duration}s > 10s) incurs per-second billing and requires explicit checkpoint confirmation."

    if credit_cost > MAX_CREDIT_CEILING:
        return False, f"Spend exceeds max credit ceiling ({credit_cost} > {MAX_CREDIT_CEILING}). Checkpoint confirmation required to protect shared Google One AI credit pool."

    if (session_spent_credits + credit_cost) > max_session_credits and credit_cost > 0:
        return False, f"Spend exceeds cumulative session ceiling ({session_spent_credits + credit_cost} > {max_session_credits})."

    if credit_cost == 0:
        return True, "0-credit action allowed in auto mode."

    if (autonomy_mode or "").strip().lower() == "auto":
        return True, f"Auto mode override active: consuming {credit_cost} credits."

    return False, f"Generation costs {credit_cost} credits. Checkpoint confirmation required."


def validate_scene_operation_order(operations: List[str]) -> Tuple[bool, str]:
    """
    Validate that inline edits occur prior to Extend operations.
    Live Flow Web UI blocks inline video editing (insert, remove, camera, edit) on clips that have been extended.
    """
    has_extended = False
    for op in operations:
        clean = (op or "").strip().lower()
        if "extend" in clean:
            has_extended = True
        elif has_extended and any(tok in clean for tok in INLINE_EDIT_TOKENS):
            return False, "Flow invariant violated: Inline video edits (insert/remove/camera/edit) must occur before Extend. Flow Web blocks editing on extended clips."
    return True, "Operation sequence is valid."


# ---------------------------------------------------------
# Veo 3.1 / Omni 1.2 Five-Slot Grammar & Prompt Compiler
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
    Validate a Veo 3.1 / Omni 1.2 prompt against lowering rules and syntax guidelines.
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
