#!/usr/bin/env python3
"""
Knowledge Saver Tool for OpenClaw
Saves reports to the 'knowledge/' directory and pushes to GitHub.
Usage: python save_knowledge.py "Title" "Markdown Content"
"""
import sys
import os
import datetime
import re
import subprocess

def get_repo_root():
    """Get Git repository root directory."""
    try:
        # Check if we are inside a git repo
        root = subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], stderr=subprocess.DEVNULL).decode().strip()
        return root
    except:
        # Fallback: assume current directory or user home/workspace if in codespaces
        return os.path.expanduser("~/.openclaw/workspace")

REPO_ROOT = get_repo_root()
KNOWLEDGE_DIR = os.path.join(REPO_ROOT, "knowledge")

def sanitize_filename(title):
    """Convert title to filename safe string."""
    # Remove special chars, spaces to underscores
    s = re.sub(r'[^\w\s-]', '', title).strip().lower()
    return re.sub(r'[-\s]+', '-', s)

def run_git_cmd(args, cwd):
    """Run a git command."""
    try:
        subprocess.check_call(['git'] + args, cwd=cwd)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Git error: {e}")
        return False

def main():
    if len(sys.argv) < 3:
        print('Usage: save_knowledge.py "Title" "Content"')
        sys.exit(1)

    title = sys.argv[1]
    content = sys.argv[2]
    
    # Ensure directory exists (in case it wasn't pulled yet)
    if not os.path.exists(KNOWLEDGE_DIR):
        os.makedirs(KNOWLEDGE_DIR)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d")
    filename = f"{timestamp}_{sanitize_filename(title)}.md"
    filepath = os.path.join(KNOWLEDGE_DIR, filename)

    # Add metadata header
    full_content = f"""# {title}
Date: {datetime.datetime.now().isoformat()}

{content}
"""

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(full_content)
        print(f"✅ File saved: knowledge/{filename}")
    except Exception as e:
        print(f"Error writing file: {e}")
        sys.exit(1)

    # Git operations
    print("🚀 Pushing to GitHub...")
    if run_git_cmd(['pull'], REPO_ROOT): # Sync first
        if run_git_cmd(['add', f'knowledge/{filename}'], REPO_ROOT):
            if run_git_cmd(['commit', '-m', f'feat(knowledge): add {title}'], REPO_ROOT):
                if run_git_cmd(['push'], REPO_ROOT):
                    print("🎉 Success! Report is on GitHub.")
                    # Link for user
                    print(f"View at: https://github.com/jomar-dev/openclaw/blob/main/knowledge/{filename}")
                else:
                    print("❌ Push failed.")
            else:
                 print("❌ Commit failed.")
        else:
             print("❌ Add failed.")
    else:
        print("⚠️ Pull failed, check conflicts.")

if __name__ == "__main__":
    main()
