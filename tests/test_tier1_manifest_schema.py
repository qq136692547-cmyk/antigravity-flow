"""
Tier 1: Plugin Manifest Schema & Skill Integrity Tests
"""

import json
import re
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent


def test_plugin_json_schema():
    manifest_path = PLUGIN_ROOT / "plugin.json"
    assert manifest_path.exists(), "plugin.json must exist in root"
    
    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    assert data.get("name") == "antigravity-flow"
    assert data.get("displayName") == "Google Flow"
    assert data.get("version") == "0.3.0"
    assert len(data.get("description", "")) > 20
    
    # Check author & repository links
    author = data.get("author", {})
    assert author.get("name") == "qq136692547-cmyk"
    assert author.get("url") == "https://qq136692547-cmyk.github.io/"
    assert data.get("homepage") == "https://qq136692547-cmyk.github.io/"
    assert data.get("repository") == "https://github.com/qq136692547-cmyk/antigravity-flow"
    
    # Check logo file
    logo_rel = data.get("logo")
    assert logo_rel, "Logo path must be defined"
    logo_path = PLUGIN_ROOT / logo_rel
    assert logo_path.exists(), f"Logo file {logo_path} must exist"
    
    # Check suggested prompts
    prompts = data.get("suggestedPrompts", [])
    assert len(prompts) >= 3, "At least 3 suggested prompts must be defined"


def test_rules_agents_md():
    agents_path = PLUGIN_ROOT / "rules" / "AGENTS.md"
    assert agents_path.exists(), "rules/AGENTS.md must exist"
    
    content = agents_path.read_text(encoding="utf-8")
    assert "Fast-Path Authentication Check" in content
    assert "Live Credit Sniffer" in content
    assert re.search(r"auto\s+mode", content, re.I) is not None
    assert re.search(r"checkpoint\s+mode", content, re.I) is not None
    assert "4K Upscaled" in content or "4K Upscale" in content


def test_skills_frontmatter_and_presence():
    expected_skills = [
        "flow-director",
        "flow-ingredients",
        "flow-generate",
        "flow-scene-builder",
        "flow-tools",
        "flow-sync",
    ]
    
    skills_dir = PLUGIN_ROOT / "skills"
    assert skills_dir.exists() and skills_dir.is_dir()
    
    for skill_name in expected_skills:
        skill_dir = skills_dir / skill_name
        assert skill_dir.exists(), f"Skill directory {skill_name} must exist"
        
        skill_file = skill_dir / "SKILL.md"
        assert skill_file.exists(), f"SKILL.md must exist in {skill_name}"
        
        content = skill_file.read_text(encoding="utf-8")
        assert content.startswith("---"), f"{skill_name}/SKILL.md must start with YAML frontmatter"
        
        # Extract frontmatter
        parts = content.split("---", 2)
        assert len(parts) >= 3, f"Valid YAML frontmatter required in {skill_name}/SKILL.md"
        fm = parts[1]
        
        name_match = re.search(r"^name:\s*([^\n]+)$", fm, re.MULTILINE)
        assert name_match, f"Frontmatter 'name' missing in {skill_name}"
        assert name_match.group(1).strip() == skill_name, f"Frontmatter name must match directory {skill_name}"
        
        desc_match = re.search(r"^description:\s*(.+)$", fm, re.MULTILINE)
        assert desc_match, f"Frontmatter 'description' missing in {skill_name}"
        
        if skill_name == "flow-sync":
            assert "disable-model-invocation: true" in fm, "flow-sync must be marked disable-model-invocation: true"


def test_references_presence():
    expected_refs = [
        PLUGIN_ROOT / "skills" / "flow-director" / "references" / "veo-prompt-guide.md",
        PLUGIN_ROOT / "skills" / "flow-tools" / "references" / "tools-catalog.md",
        PLUGIN_ROOT / "skills" / "flow-sync" / "references" / "audit-checklist.md",
    ]
    for ref_path in expected_refs:
        assert ref_path.exists(), f"Reference file {ref_path} must exist"
        assert len(ref_path.read_text(encoding="utf-8")) > 100, f"Reference {ref_path} must be non-empty"


if __name__ == "__main__":
    test_plugin_json_schema()
    test_rules_agents_md()
    test_skills_frontmatter_and_presence()
    test_references_presence()
    print("Tier 1 Tests PASSED: Manifest, rules, and all 6 skills validated.")
