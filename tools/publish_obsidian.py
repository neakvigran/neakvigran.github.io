
#!/usr/bin/env python3

import argparse
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

REPO = Path(__file__).resolve().parent.parent
VAULT = REPO.parent
IMAGE_DIR = VAULT / "UPLOADED PICTURE"
POST_DIR = REPO / "_posts"
ASSET_DIR = REPO / "assets" / "img" / "obsidian"

IMAGE_PATTERN = re.compile(
    r"!\[\[([^\]|]+\.(?:png|jpg|jpeg|gif|webp))(?:\|[^\]]*)?\]\]",
    re.IGNORECASE,
)


def slugify(text):
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def yaml_quote(value):
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def publish(note_path, category, tags, write_files=False):
    note_path = note_path.expanduser().resolve()

    if not note_path.is_file():
        raise ValueError(f"Note not found: {note_path}")

    # Only allow notes from the Obsidian vault,
    # excluding files inside the website repository.
    if not note_path.is_relative_to(VAULT):
        raise ValueError("The note must be inside your Obsidian vault.")

    if note_path.is_relative_to(REPO):
        raise ValueError("Select a source note outside the website repository.")

    content = note_path.read_text(encoding="utf-8")
    filenames = list(dict.fromkeys(IMAGE_PATTERN.findall(content)))

    missing = [
        name for name in filenames
        if not (IMAGE_DIR / name).is_file()
    ]

    if missing:
        raise ValueError(
            "Missing images:\n" + "\n".join(missing)
        )

    title = note_path.stem
    slug = slugify(title)

    if not slug:
        raise ValueError("Unable to generate a valid post filename.")

    today = datetime.now().astimezone()
    date_prefix = today.strftime("%Y-%m-%d")
    post_date = today.strftime("%Y-%m-%d %H:%M:%S %z")

    post_path = POST_DIR / f"{date_prefix}-{slug}.md"
    image_output = ASSET_DIR / slug

    if post_path.exists():
        raise FileExistsError(
            f"Post already exists: {post_path}"
        )

    # Avoid silently replacing images from a previous publication.
    for filename in filenames:
        destination = image_output / filename
        if destination.exists():
            raise FileExistsError(
                f"Image already exists: {destination}"
            )

    def replace_image(match):
        filename = match.group(1)
        encoded = quote(filename)
        url = f"/assets/img/obsidian/{slug}/{encoded}"
        return f"![{filename}]({url})"

    converted = IMAGE_PATTERN.sub(replace_image, content)

    tag_list = [
        slugify(tag)
        for tag in tags.split(",")
        if tag.strip()
    ]

    front_matter = (
        "---\n"
        f"title: {yaml_quote(title)}\n"
        f"date: {post_date}\n"
        f"categories: [TryHackMe, {category}]\n"
        f"tags: [{', '.join(tag_list)}]\n"
        "toc: true\n"
        "comments: false\n"
        "---\n\n"
    )

    output = front_matter + converted

    print(f"Source: {note_path}")
    print(f"Post: {post_path}")
    print(f"Images: {len(filenames)}")
    print(f"Category: TryHackMe / {category}")
    print(f"Tags: {', '.join(tag_list)}")

    if not write_files:
        print("\nDRY RUN: No files were changed.")
        return

    POST_DIR.mkdir(parents=True, exist_ok=True)

    if filenames:
        image_output.mkdir(parents=True, exist_ok=True)

    for filename in filenames:
        shutil.copy2(
            IMAGE_DIR / filename,
            image_output / filename
        )

    post_path.write_text(output, encoding="utf-8")

    print("\nPost generated successfully.")
    print("Review the post and screenshots before committing.")


def main():
    parser = argparse.ArgumentParser(
        description="Convert Obsidian notes to Chirpy posts."
    )

    parser.add_argument("note", type=Path)
    parser.add_argument(
        "--category",
        default="Challenge"
    )
    parser.add_argument(
        "--tags",
        default="tryhackme,web-security"
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Generate the post and copy referenced images."
    )

    args = parser.parse_args()

    try:
        publish(
            args.note,
            args.category,
            args.tags,
            args.write
        )
    except (OSError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
