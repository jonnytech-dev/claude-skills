#!/usr/bin/env python3
"""
Auto-generate README.md from skill files.
Reads SKILL.md frontmatter and creates a dynamic skills directory.
Run: python generate-readme.py
"""

import os
import re
from pathlib import Path
import yaml

SKILLS_DIR = "skills"
README_FILE = "README.md"

def extract_frontmatter(skill_path):
    """Extract YAML frontmatter from SKILL.md file."""
    try:
        with open(skill_path, 'r') as f:
            content = f.read()
        
        # Match YAML frontmatter between ---
        match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if match:
            yaml_content = match.group(1)
            return yaml.safe_load(yaml_content)
    except Exception as e:
        print(f"Error reading {skill_path}: {e}")
    
    return None

def get_skill_trigger_examples(skill_md_path):
    """Extract trigger phrases from skill description or body."""
    try:
        with open(skill_md_path, 'r') as f:
            content = f.read()
        
        # Remove frontmatter
        content = re.sub(r'^---\n.*?\n---\n', '', content, flags=re.DOTALL)
        
        # Look for "Trigger" or "When to use" patterns
        lines = content.split('\n')
        triggers = []
        capture = False
        
        for line in lines:
            if 'trigger' in line.lower() or 'when to use' in line.lower():
                capture = True
                continue
            if capture:
                if line.startswith('##'):
                    break
                if '- ' in line or '"' in line:
                    # Extract quoted or bulleted items
                    quoted = re.findall(r'"([^"]+)"', line)
                    if quoted:
                        triggers.extend(quoted)
        
        return triggers[:3]  # Return first 3 triggers
    except:
        return []

def scan_skills():
    """Scan skills directory and extract metadata."""
    skills = []
    
    if not os.path.isdir(SKILLS_DIR):
        print(f"Skills directory not found: {SKILLS_DIR}")
        return skills
    
    for skill_name in sorted(os.listdir(SKILLS_DIR)):
        skill_path = os.path.join(SKILLS_DIR, skill_name)
        skill_md = os.path.join(skill_path, "SKILL.md")
        
        if os.path.isdir(skill_path) and os.path.isfile(skill_md):
            metadata = extract_frontmatter(skill_md)
            if metadata:
                triggers = get_skill_trigger_examples(skill_md)
                metadata['path'] = skill_name
                metadata['triggers'] = triggers
                skills.append(metadata)
    
    return skills

def generate_skills_section(skills):
    """Generate markdown for skills section."""
    section = "---\n\n## 📚 Skills Directory\n\n"
    
    for i, skill in enumerate(skills, 1):
        name = skill.get('name', 'Unknown')
        description = skill.get('description', 'No description available')
        triggers = skill.get('triggers', [])
        
        section += f"### {i}. **{name}**\n"
        section += f"{description}\n\n"
        
        if triggers:
            section += "**Triggers:** " + ", ".join(f'"{t}"' for t in triggers) + "\n\n"
        
        section += "---\n\n"
    
    return section

def generate_table(skills):
    """Generate skills comparison table."""
    table = "| Skill | Purpose |\n"
    table += "|-------|----------|\n"
    
    for skill in skills:
        name = skill.get('name', 'Unknown')
        description = skill.get('description', 'No description')
        # Shorten description to fit table
        short_desc = description[:80] + "..." if len(description) > 80 else description
        table += f"| {name} | {short_desc} |\n"
    
    return table

def generate_readme(skills):
    """Generate complete README."""
    timestamp = "Last Updated: September 2, 2026"
    
    readme = """# Claude Skills Repository

A collection of custom Claude skills built for productivity, content creation, faith documentation, and technical education.

## What Are These Skills?

Claude skills are reusable instructions that extend Claude's capabilities for specific workflows. Each skill includes detailed guidelines, examples, and output formats tailored to a particular task.

"""
    
    # Skills directory section
    readme += generate_skills_section(skills)
    
    # Quick reference table
    readme += "## 🛠️ Quick Reference\n\n"
    readme += generate_table(skills)
    readme += "\n"
    
    # Rest of README
    readme += """
---

## 🚀 How to Use These Skills

1. **Download a skill file** from this repository (found in `.skill-packages/` folder)
2. **Install in Claude:** In Claude.ai settings, add the skill to your profile
3. **Trigger naturally:** Use the skill by saying the trigger phrases listed above
4. **Get custom output:** Claude will follow the skill's instructions to produce formatted, consistent results

---

## 📋 Installation

Each skill is packaged as a `.skill` file. See [INSTALLATION.md](INSTALLATION.md) for detailed steps.

---

## 💡 Philosophy

These skills are built around:

- **Accessibility:** Complex ideas explained in simple language
- **Consistency:** Same format every time, reliable output
- **Actionable:** Not just information — practical solutions and next steps
- **Personal voice:** Maintains your tone and perspective across outputs

---

## 📝 Skill Structure

Each skill folder contains:

```
skill-name/
├── SKILL.md          (Main instructions and workflow)
└── examples/         (Sample outputs)
```

The `.skill` file is a packaged version ready to install in Claude.

---

## 🔄 Keeping Skills Updated

To add or update skills:

1. Create or modify the skill folder in `skills/`
2. Ensure it has a `SKILL.md` file with frontmatter (name, description)
3. Run `python generate-readme.py` to update this README
4. Commit and push changes

---

## ✍️ Adding New Skills

1. Create a folder: `skills/your-skill-name/`
2. Add `SKILL.md` with YAML frontmatter:
   ```yaml
   ---
   name: Your Skill Name
   description: What this skill does and when to use it
   ---
   
   # Skill content here...
   ```
3. Run `python generate-readme.py`
4. Commit changes

---

## 📞 Notes

- Skills work best with Claude's latest models
- Some skills may require file upload capabilities or web search
- Each skill is designed to be standalone but can work together in conversation

---

**Built with:** Claude AI  
**Maintained by:** Jon Taylor (JonnyTech)  
""" + timestamp

    return readme

def main():
    """Main execution."""
    print("Scanning skills directory...")
    skills = scan_skills()
    
    if not skills:
        print("No skills found. Make sure you have SKILL.md files in the skills/ directory.")
        return
    
    print(f"Found {len(skills)} skills:")
    for skill in skills:
        print(f"  - {skill.get('name')}")
    
    print("\nGenerating README.md...")
    readme = generate_readme(skills)
    
    with open(README_FILE, 'w') as f:
        f.write(readme)
    
    print(f"✅ README.md generated successfully!")
    print(f"📍 Location: {README_FILE}")

if __name__ == "__main__":
    main()
