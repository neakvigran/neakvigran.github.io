
#!/usr/bin/env python3
"""Verify generated Obsidian writeups before deployment."""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
VAULT = REPO.parent
MANIFEST = REPO / "tools/.obsidian-published.json"
ASSETS = REPO / "assets/img/obsidian"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_note(source, manifest):
    source = Path(source).resolve(strict=True)

    if (
        not source.is_file()
        or source.suffix.lower() != ".md"
        or not source.is_relative_to(VAULT)
        or source.is_relative_to(REPO)
    ):
        raise ValueError(f"Invalid source note: {source}")

    key = source.relative_to(VAULT).as_posix()
    entry = manifest.get(key)

    if not isinstance(entry, dict):
        raise ValueError(f"Missing manifest entry: {key}")

    required = (
        "source_sha256",
        "post_sha256",
        "image_sha256",
    )

    if any(field not in entry for field in required):
        raise ValueError(
            f"Missing fingerprints for {key}. "
            "Regenerate with --write before deployment."
        )

    slug = entry["slug"]
    post_rel = entry["post"]
    images = entry["images"]

    if (
        not isinstance(slug, str)
        or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug)
        or not isinstance(post_rel, str)
        or not isinstance(images, list)
        or not all(isinstance(name, str) for name in images)
    ):
        raise ValueError(f"Invalid manifest paths for {key}")

    post = (REPO / post_rel).resolve()

    if (
        not post.is_relative_to(REPO / "_posts")
        or not post.is_file()
    ):
        raise ValueError(f"Invalid or missing post: {post_rel}")

    if sha256(source) != entry["source_sha256"]:
        raise ValueError(
            f"Obsidian note changed since generation: {key}"
        )

    if sha256(post) != entry["post_sha256"]:
        raise ValueError(
            f"Generated post changed since generation: {post_rel}"
        )

    recorded = entry["image_sha256"]

    if not isinstance(recorded, dict) or set(recorded) != set(images):
        raise ValueError(f"Image fingerprint list mismatch: {key}")

    for name in images:
        if (
            name in (".", "..")
            or Path(name).name != name
            or "/" in name
            or "\\" in name
        ):
            raise ValueError(f"Invalid image filename: {name}")

        image = (ASSETS / slug / name).resolve()

        if not image.is_relative_to(ASSETS / slug):
            raise ValueError(f"Unsafe image path: {name}")

        if not image.is_file():
            raise ValueError(f"Missing image: {image}")

        if sha256(image) != recorded[name]:
            raise ValueError(f"Screenshot changed: {image}")

    print(f"PASS: {key} ({len(images)} images verified)")

    return post_rel, [
        f"assets/img/obsidian/{slug}/{name}"
        for name in images
    ]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("notes", nargs="+")
    args = parser.parse_args()

    try:
        manifest = json.loads(
            MANIFEST.read_text(encoding="utf-8")
        )

        if not isinstance(manifest, dict):
            raise ValueError("Invalid publishing manifest")

        for note in args.notes:
            verify_note(note, manifest)

    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    print("All selected writeup fingerprints verified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
