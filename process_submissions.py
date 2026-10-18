import os
import re
import sys
import subprocess
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
INPUT_FILE = REPO_ROOT / "paste_here.txt"

TEMPLATE_HEADER = """# ==============================================================================
# PASTE YOUR LEETCODE CODES HERE
# ==============================================================================
# You can paste multiple problems below.
# To help identify each problem, please include the problem name, number, or URL
# above each solution.
#
# Examples of acceptable formats:
#
# ---
# Problem: 1. Two Sum
# class Solution:
#     def twoSum(self, nums: List[int], target: int) -> List[int]:
#         ...
#
# ---
# Problem: 217. Contains Duplicate
# class Solution {
# public:
#     bool containsDuplicate(vector<int>& nums) {
#         ...
#     }
# };
#
# ------------------------------------------------------------------------------
# Paste your code below this line:
"""

def slugify(title: str) -> str:
    title = title.lower()
    # Replace non-alphanumeric (except dashes and spaces)
    title = re.sub(r'[^a-z0-9\s\-]', ' ', title)
    # Replace whitespace sequences with single hyphen
    title = re.sub(r'[\s\-]+', '-', title).strip('-')
    return title

def detect_language(code: str) -> str:
    # Check for C++ indicators
    if re.search(r'#include\s*<|std::|vector\s*<|nullptr|cout\s*<<|cin\s*>>|class\s+Solution\s*\{[\s\S]*public:', code):
        return ".cpp"
    # Check for Java indicators
    if re.search(r'public\s+class\s+Solution|System\.out\.print|public\s+(?:int|boolean|void|String|List|TreeNode|ListNode)\b', code):
        return ".java"
    # Check for C indicators
    if re.search(r'#include\s*<stdio\.h>|#include\s*<stdlib\.h>', code):
        return ".c"
    # Check for TypeScript / JavaScript
    if re.search(r'function\s+\w+\s*\(|console\.log\(|let\s+\w+\s*=|const\s+\w+\s*=', code):
        if re.search(r':\s*(?:number|string|boolean|any|void)\b', code):
            return ".ts"
        return ".js"
    # Check for Python indicators
    if re.search(r'def\s+\w+\s*\(|class\s+Solution\s*:|self\b|import\s+\w+|from\s+\w+\s+import', code):
        return ".py"
    
    # Default fallback
    return ".py"

def extract_problem_metadata(block: str, default_index: int):
    lines = block.splitlines()
    problem_title = None
    problem_number = None
    cleaned_code_lines = []
    
    url_match = re.search(r'https?://leetcode\.com/problems/([a-zA-Z0-9\-]+)', block)
    url_slug = url_match.group(1) if url_match else None

    in_header = True
    for line in lines:
        stripped = line.strip()
        
        # Check if line indicates problem title/number
        m_prob = re.search(r'^(?:#|//|/\*|\*|--+)?\s*(?:problem\s*:\s*|leetcode\s*:\s*|question\s*:\s*)?(\d+)?[\.\:\-\s]*([A-Za-z0-9\s\-]+?)(?:\*/)?$', stripped, re.IGNORECASE)
        
        if in_header and (stripped.startswith(('---', '===', '___')) or not stripped):
            continue
            
        if in_header and m_prob and not re.search(r'^(class|def|int|void|public|import|#include|from|var|let|const)\b', stripped):
            num = m_prob.group(1)
            title = m_prob.group(2).strip()
            # Avoid matching random comment lines
            if len(title) > 1 and not title.lower().startswith(('time complexity', 'space complexity', 'solution', 'approach')):
                if num:
                    problem_number = int(num)
                if title:
                    problem_title = title
            continue
        
        # Once we see code, stop header processing
        if stripped and not stripped.startswith(('#', '//', '/*', '*', '--')):
            in_header = False
            
        cleaned_code_lines.append(line)

    code = "\n".join(cleaned_code_lines).strip()
    
    # Construct filename
    if problem_number and problem_title:
        fname = f"{problem_number:04d}-{slugify(problem_title)}"
    elif problem_number:
        fname = f"{problem_number:04d}-problem"
    elif problem_title:
        fname = slugify(problem_title)
    elif url_slug:
        fname = url_slug
    else:
        fname = f"problem-{default_index:02d}"

    return fname, code

def split_submissions(raw_text: str):
    # Remove initial template comments if present
    marker = "Paste your code below this line:"
    if marker in raw_text:
        raw_text = raw_text.split(marker, 1)[1]

    # Split by delimiter lines (e.g., --- or ===) or Problem: headers
    parts = re.split(r'(?:\r?\n)(?:-{3,}|={3,}|_{3,}|\/\/{3,}|#{3,})(?:\r?\n)', raw_text)
    
    # If no delimiter found, check if multiple 'Problem:' or multiple 'class Solution' exist
    if len(parts) <= 1:
        # Check for multiple 'Problem:'
        subparts = re.split(r'(?=(?:^|\n)\s*(?:#|//)?\s*Problem\s*:)', raw_text, flags=re.IGNORECASE)
        if len(subparts) > 1:
            parts = subparts
        else:
            # Check for multiple 'class Solution'
            subparts = re.split(r'(?=(?:^|\n)\s*(?:class\s+Solution|public\s+class\s+Solution))', raw_text)
            if len(subparts) > 1:
                parts = subparts

    blocks = [p.strip() for p in parts if p.strip()]
    return blocks

def process():
    if not INPUT_FILE.exists():
        print(f"Error: {INPUT_FILE} does not exist.")
        sys.exit(1)

    content = INPUT_FILE.read_text(encoding="utf-8")
    
    blocks = split_submissions(content)
    if not blocks:
        print("No solutions found in paste_here.txt. Please paste your code first!")
        return

    today_str = datetime.now().strftime("%Y-%m-%d")
    date_dir = REPO_ROOT / today_str
    date_dir.mkdir(exist_ok=True)

    saved_files = []
    for idx, block in enumerate(blocks, start=1):
        filename_base, code = extract_problem_metadata(block, idx)
        if not code:
            continue
        ext = detect_language(code)
        filename = f"{filename_base}{ext}"
        target_path = date_dir / filename
        
        # Handle duplicates if same file name in same day
        counter = 1
        while target_path.exists():
            target_path = date_dir / f"{filename_base}_{counter}{ext}"
            counter += 1

        target_path.write_text(code + "\n", encoding="utf-8")
        saved_files.append(target_path)
        print(f" [OK] Saved: {target_path.relative_to(REPO_ROOT)}")

    if not saved_files:
        print("No valid code blocks found to save.")
        return

    # Reset paste_here.txt with clean template
    INPUT_FILE.write_text(TEMPLATE_HEADER, encoding="utf-8")
    print(f" Reset {INPUT_FILE.name} for your next batch.")

    # Git operations
    print("\n Running Git operations...")
    try:
        subprocess.run(["git", "add", str(date_dir)], cwd=REPO_ROOT, check=True)
        file_list_str = ", ".join([f.stem for f in saved_files])
        commit_msg = f"Add solutions for {today_str}: {file_list_str}"
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=REPO_ROOT, check=True)
        print(f" Committed: {commit_msg}")
    except subprocess.CalledProcessError as e:
        print(f" Git commit failed or nothing new to commit: {e}")
        return

    # Check remote origin
    check_remote = subprocess.run(["git", "remote", "get-url", "origin"], cwd=REPO_ROOT, capture_output=True, text=True)
    if check_remote.returncode != 0:
        print("\n[!] Notice: Git remote 'origin' is not configured yet.")
        print("    To push automatically to your GitHub/GitLab repo, link it by running:")
        print("    git remote add origin <your-repo-url>")
        print("    git push -u origin main")
    else:
        print(" Pushing to remote repository...")
        push_res = subprocess.run(["git", "push", "origin", "main"], cwd=REPO_ROOT, capture_output=True, text=True)
        if push_res.returncode == 0:
            print(" Successfully pushed to your remote repository!")
        else:
            print(" Git push error:")
            print(push_res.stderr)

if __name__ == "__main__":
    process()
