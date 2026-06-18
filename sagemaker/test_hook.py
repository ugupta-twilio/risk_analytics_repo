#!/usr/bin/env python3
"""
Standalone tests for _is_sagemaker_path().

Run with: python3 sagemaker/test_hook.py
"""

import os
from pathlib import Path


def _is_sagemaker_path(os_path, repo_dir):
    """True if os_path is a .ipynb file inside a .../<username>/sagemaker/ subtree."""
    if not os_path.endswith(".ipynb"):
        return False
    rel = os.path.relpath(os_path, repo_dir)
    parts = Path(rel).parts
    # Must be under projects/ and have 'sagemaker' as the immediate parent dir
    # of the file, preceded by a username folder.
    # e.g. projects/GM/RISK-3016/kbhat/sagemaker/notebook.ipynb
    #       parts: ('projects','GM','RISK-3016','kbhat','sagemaker','notebook.ipynb')
    # parts[-2] == 'sagemaker' ensures the file is directly inside sagemaker/ (not nested).
    # index >= 4 ensures there is at least one username component before sagemaker/.
    return (
        parts[0] == "projects"
        and parts[-2] == "sagemaker"
        and list(parts).index("sagemaker") >= 4
    )


def make_abs(repo_dir, rel_path):
    """Join repo_dir with a relative path to produce an absolute os_path."""
    return os.path.join(repo_dir, rel_path)


def run_tests():
    repo_dir = "/home/user/risk-analytics"

    cases = [
        # (description, rel_path, expected)
        (
            "valid sagemaker notebook",
            "projects/GM/RISK-3016/kbhat/sagemaker/analysis.ipynb",
            True,
        ),
        (
            "wrong extension (.py)",
            "projects/GM/RISK-3016/kbhat/sagemaker/analysis.py",
            False,
        ),
        (
            "not in sagemaker/ directory",
            "projects/GM/RISK-3016/kbhat/analysis.ipynb",
            False,
        ),
        (
            "nested too deep inside sagemaker/",
            "projects/GM/RISK-3016/kbhat/sagemaker/subdir/deep.ipynb",
            False,
        ),
        (
            "sagemaker directly under area (no username)",
            "projects/GM/sagemaker/analysis.ipynb",
            False,
        ),
        (
            "not under projects/",
            "other/stuff/sagemaker/file.ipynb",
            False,
        ),
        (
            "sagemaker at wrong depth (no username folder)",
            "projects/GM/RISK-3016/sagemaker/analysis.ipynb",
            False,
        ),
        (
            "capital-S Sagemaker/ rejected (case-sensitive)",
            "projects/GM/RISK-3016/kbhat/Sagemaker/analysis.ipynb",
            False,
        ),
    ]

    passed = 0
    failed = 0

    for description, rel_path, expected in cases:
        os_path = make_abs(repo_dir, rel_path)
        result = _is_sagemaker_path(os_path, repo_dir)
        status = "PASS" if result == expected else "FAIL"
        if result == expected:
            passed += 1
        else:
            failed += 1
        print(f"  [{status}] {description}")
        if result != expected:
            print(f"         path:     {rel_path}")
            print(f"         expected: {expected}, got: {result}")

    print()
    print(f"Results: {passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    print("Running _is_sagemaker_path tests...")
    print()
    success = run_tests()
    raise SystemExit(0 if success else 1)
