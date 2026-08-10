#!/usr/bin/env python3
"""
push_all_changes_one_by_one.py
==============================
Pushes every changed, deleted, or untracked file/folder to GitHub
with ONE SEPARATE COMMIT per file.

Repo  : https://github.com/Aryan140314/Text-to-Speech-Models
Branch: main
"""

import os
import sys
import subprocess

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRANCH = "main"

sep = "=" * 70

def run_git(args):
    result = subprocess.run(
        ["git"] + args,
        cwd=REPO_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()

def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    print(sep)
    print("🚀  GITHUB PUSH ALL — ONE COMMIT PER FILE")
    print(f"    Repository Root: {REPO_ROOT}")
    print(f"    Target Branch  : {BRANCH}")
    print(sep)

    # 1. Get status list
    code, out, err = run_git(["status", "--porcelain"])
    if code != 0:
        print(f"[!] Error reading git status: {err}")
        sys.exit(1)

    raw_lines = [l for l in out.splitlines() if l.strip()]
    if not raw_lines:
        print("[+] Working tree clean. Nothing to commit.")
        sys.exit(0)

    # Expand untracked directories into individual files
    staged_items = []
    for line in raw_lines:
        status_code = line[:2]
        filepath = line[3:].strip().strip('"').strip("'")

        full_path = os.path.join(REPO_ROOT, filepath)
        if os.path.isdir(full_path):
            for root, dirs, files in os.walk(full_path):
                for f in files:
                    rel_f = os.path.relpath(os.path.join(root, f), REPO_ROOT).replace("\\", "/")
                    staged_items.append((status_code, rel_f))
        else:
            rel_f = filepath.replace("\\", "/")
            staged_items.append((status_code, rel_f))

    # Remove duplicates while preserving order
    seen = set()
    unique_items = []
    for st, path in staged_items:
        if path not in seen:
            seen.add(path)
            unique_items.append((st, path))

    total = len(unique_items)
    print(f"[+] Total files to commit & push: {total}\n")

    pushed_count = 0
    failed_count = 0

    for idx, (st, rel_path) in enumerate(unique_items, 1):
        filename = os.path.basename(rel_path)
        is_deleted = "D" in st or not os.path.exists(os.path.join(REPO_ROOT, rel_path))

        if is_deleted:
            action = "Remove"
            add_code, _, add_err = run_git(["rm", "--cached", rel_path])
            if add_code != 0:
                run_git(["rm", "-f", rel_path])
            commit_msg = f"Remove {filename} from repository"
        else:
            action = "Update" if "M" in st else "Add"
            run_git(["add", rel_path])
            commit_msg = f"{action} {filename} ({rel_path})"

        # Commit single file
        c_code, c_out, c_err = run_git(["commit", "-m", commit_msg])
        if c_code != 0 and "nothing to commit" not in c_err and "nothing to commit" not in c_out:
            print(f"  [{idx:02d}/{total}] ⚠️ COMMIT SKIPPED: {rel_path} ({c_err})")

        # Push single commit to GitHub
        p_code, p_out, p_err = run_git(["push", "origin", BRANCH])
        if p_code == 0:
            print(f"  [{idx:02d}/{total}] ✅ {action.upper()} & PUSHED : {rel_path}")
            pushed_count += 1
        else:
            print(f"  [{idx:02d}/{total}] ❌ PUSH FAILED : {rel_path}")
            print(f"             Reason: {p_err[:120]}")
            failed_count += 1

    print("\n" + sep)
    print(f"🎉  PUSH COMPLETE — Total: {total} | Pushed: {pushed_count} | Failed: {failed_count}")
    print(sep)

if __name__ == "__main__":
    main()
