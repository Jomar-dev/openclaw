---
name: knowledge-saver
description: "Save reports to the `knowledge/` folder in the GitHub repository. Use `save_knowledge.py` to create a markdown file, commit, and push it."
metadata:
  {
    "openclaw":
      { "emoji": "🧠", "requires": { "bins": ["git", "python3"] } },
  }
---

# Knowledge Saver Skill

Saves markdown reports to the `knowledge/` folder of the current repository and pushes changes to GitHub using the active Codespaces credentials.

## Usage

```bash
python ~/.openclaw/skills/knowledge-saver/save_knowledge.py "My Report Title" "# Content\nHere is the report..."
```

## Output

Returns the GitHub URL of the created file upon success.
