
#!/usr/bin/env python3
"""Reject unrelated changes to the publishing manifest."""

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
VAULT = REPO.parent
MANIFEST = REPO / "tools/.obsidian-published.json"


def main():
    if len(sys.argv) < 2:
        print("Usage: verify_manifest.py NOTE...", file=sys.stderr)
        return 2

    selected = {
        Path(note).resolve().relative_to(VAULT).as_posix()
        for note in sys.argv[1:]
    }

    current = json.loads(MANIFEST.read_text(encoding="utf-8"))

    original = json.loads(
        subprocess.check_output(
            ["git", "show", "HEAD:tools/.obsidian-published.json"],
            cwd=REPO,
            text=True,
        )
    )

    if not isinstance(current, dict) or not isinstance(original, dict):
        raise ValueError("Manifest must contain a JSON object")

    changed = {
        key
        for key in current.keys() | original.keys()
        if current.get(key) != original.get(key)
    }

    unrelated = changed - selected

    if unrelated:
        print("FAIL: Unrelated manifest changes detected:")
        for key in sorted(unrelated):
            print(f"  {key}")
        return 1

    print(f"PASS: Manifest changes limited to {len(changed)} selected notes.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        sys.exit(1)
