#!/usr/bin/env python3
"""Publish selected Obsidian notes as Jekyll Chirpy posts (no Git actions)."""
import argparse
import datetime as dt
import json
import re
import shutil
import hashlib
import yaml
import sys
from pathlib import Path
from urllib.parse import quote

REPO = Path(__file__).resolve().parent.parent
VAULT = REPO.parent
IMAGE_DIR = VAULT / 'UPLOADED PICTURE'
POST_DIR = REPO / '_posts'
ASSET_DIR = REPO / 'assets' / 'img' / 'obsidian'
MANIFEST = REPO / 'tools' / '.obsidian-published.json'
IMAGE = re.compile(r'!\[\[([^\]]+)\]\]')
WIKILINK = re.compile(r'(?<!!)\[\[([^\]]+)\]\]')
SUPPORTED = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg'}


def slugify(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


def source_path(arg):
    p = Path(arg).expanduser()
    if not p.is_absolute():
        p = VAULT / p
    p = p.resolve(strict=True)
    if not p.is_file() or p.suffix.lower() != '.md':
        raise ValueError('Source must be an existing Markdown file')
    if not p.is_relative_to(VAULT) or p.is_relative_to(REPO):
        raise ValueError('Source must be inside the vault but outside the website repository')
    return p


def load_manifest():
    if not MANIFEST.exists():
        return {}
    obj = json.loads(MANIFEST.read_text(encoding='utf-8'))
    if not isinstance(obj, dict):
        raise ValueError('Invalid manifest')
    return obj



def read_existing_description(post_path):
    """Read the description from an existing Chirpy post."""
    if not post_path.is_file():
        return None

    content = post_path.read_text(encoding="utf-8")

    if not content.startswith("---\n"):
        return None

    match = re.match(
        r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)",
        content,
        re.DOTALL
    )

    if not match:
        return None

    for line in match.group(1).splitlines():
        if line.startswith("description:"):
            value = line.split(":", 1)[1].strip()

            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value.strip("'\"")

    return None

def frontmatter(title, published, category, tags, description=None, math_enabled=None, last_modified_at=None):
    """Generate Chirpy-compatible YAML front matter."""
    result = (
        "---\n"
        + f"title: {json.dumps(title, ensure_ascii=False)}\n"
        + f"date: {published}\n"
        + f"categories: {json.dumps(category, ensure_ascii=False)}\n"
        + f"tags: {json.dumps(tags, ensure_ascii=False)}\n"
    )

    if description:
        result += (
            "description: "
            + json.dumps(description, ensure_ascii=False)
            + "\n"
        )

    if last_modified_at is not None:
        result += f"last_modified_at: {last_modified_at}\n"

    if math_enabled is not None:
        result += "math: " + ("true" if math_enabled else "false") + "\n"

    result += "toc: true\ncomments: false\n---\n\n"
    return result

def read_obsidian_metadata(content):
    """Read YAML front matter from an Obsidian note."""
    content = content.lstrip("\ufeff\r\n")

    if not content.startswith("---\n"):
        return {}

    match = re.match(
        r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)",
        content,
        re.DOTALL
    )

    if not match:
        return {}

    metadata = yaml.safe_load(match.group(1))

    if metadata is None:
        return {}

    if not isinstance(metadata, dict):
        raise ValueError(
            "Obsidian front matter must be a YAML mapping."
        )

    for key in ("date", "last_modified_at"):
        if key in metadata and metadata[key] is not None:
            value = metadata[key]
            if isinstance(value, dt.date) and not isinstance(value, dt.datetime):
                metadata[key] = value.isoformat()
            elif isinstance(value, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
                try:
                    dt.date.fromisoformat(value)
                except ValueError:
                    raise ValueError(f"{key} must be a valid YYYY-MM-DD date")
            else:
                raise ValueError(f"{key} must be a valid YYYY-MM-DD date or null")

    description = metadata.get("description")
    tags = metadata.get("tags")
    if "math" in metadata and type(metadata["math"]) is not bool:
        raise ValueError("Math must be a YAML boolean (true or false).")

    if description is not None and not isinstance(description, str):
        raise ValueError("Description must be a string.")

    if tags is not None:
        if isinstance(tags, str):
            tags = [tags]
        elif not isinstance(tags, list):
            raise ValueError("Tags must be a list or string.")

        if not all(isinstance(tag, str) for tag in tags):
            raise ValueError("Every tag must be a string.")

        metadata["tags"] = [
            slugify(tag.lstrip("#"))
            for tag in tags
            if tag.strip()
        ]

    return metadata


def extract_body(s):
    """Remove Obsidian YAML front matter from article content."""
    s = s.lstrip("\ufeff\r\n")

    match = re.match(
        r"\A---\r?\n.*?\r?\n---(?:\r?\n|$)",
        s,
        re.DOTALL
    )

    if match:
        return s[match.end():].lstrip("\r\n")

    return s


def convert(source, slug, known_posts):
    body = extract_body(source)
    original_body = body
    images = {}
    unsupported_image_modifiers = []
    def image_replace(m):
        parts = m.group(1).split('|')
        raw = parts[0].strip()
        modifier = '|'.join(parts[1:]).strip().lower() if len(parts) > 1 else ''
        filename = Path(raw).name
        if filename != raw and '/' not in raw.replace('\\', '/'):
            raise ValueError('Unsupported image path')
        if filename.lower().endswith(tuple(SUPPORTED)) is False:
            raise ValueError(f'Unsupported embed (not an image): {raw}')
        if filename in images and images[filename] != raw:
            raise ValueError(f'Ambiguous image basename: {filename}')
        images[filename] = raw
        image = f'![{Path(filename).stem}](/assets/img/obsidian/{slug}/{quote(filename)})'
        if modifier in ('left', 'right'):
            image += f'{{: .obsidian-image-{modifier} }}'
        elif modifier:
            unsupported_image_modifiers.append(modifier)
        # A standalone Obsidian embed must become its own Markdown paragraph.
        # Otherwise Kramdown joins adjacent prose into the same <p> as the
        # image, allowing text to flow beside a tall screenshot.
        line_start = original_body.rfind('\n', 0, m.start()) + 1
        line_end = original_body.find('\n', m.end())
        if line_end < 0:
            line_end = len(original_body)
        standalone = (
            not original_body[line_start:m.start()].strip()
            and not original_body[m.end():line_end].strip()
        )
        return f'\n\n{image}\n\n' if standalone else image
    body = IMAGE.sub(image_replace, body)
    unresolved = []
    def link_replace(m):
        target, _, label = m.group(1).partition('|')
        target = target.strip()
        key = slugify(Path(target.split('#', 1)[0]).stem)
        if key in known_posts:
            anchor = target.split('#', 1)[1] if '#' in target else ''
            suffix = '#' + slugify(anchor) if anchor else ''
            return f'[{label.strip() or Path(target).stem}](/posts/{known_posts[key]}/{suffix})'
        unresolved.append(m.group(0))
        return m.group(0)
    body = WIKILINK.sub(link_replace, body)
    return body, images, unresolved, sorted(set(unsupported_image_modifiers))


def sha256_bytes(data):
    """Return the SHA-256 digest of bytes."""
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):
    """Return the SHA-256 digest of a file."""
    return sha256_bytes(path.read_bytes())


def prepare_math(body):
    """Translate opt-in math to Kramdown delimiters, preserving code and prices.

    Numeric-leading inline math needs a mathematical operator or LaTeX token;
    bare dollar amounts stay text. Use $$25$$ or \\(25\\) for a number alone.
    No math is detected or enabled automatically.
    """
    def escaped(pos):
        slashes = 0
        while pos > 0 and body[pos - 1] == '\\':
            slashes += 1
            pos -= 1
        return slashes % 2 == 1

    def numeric_math(expression):
        """Accept mathematical tokens, not prices or prose between dollars."""
        commands = (
            r'frac|sqrt|times|cdot|div|pm|mp|geq?|leq?|neq?|equiv|'
            r'bmod|mod|pi|alpha|beta|gamma|delta|theta|lambda|mu|sigma|'
            r'phi|varphi|omega|infty|sin|cos|tan|log|ln|exp|left|right'
        )
        # Removing known TeX commands also avoids treating their names as prose.
        plain = re.sub(r'\\(?:' + commands + r')\b', ' ', expression)
        if re.search(r'[A-Za-z]{2,}', plain):
            return False
        if re.search(r'[^\s0-9A-Za-z\u0370-\u03ff+*/^_=<>≤≥≠×÷·%{}()[\],.!|:\-]', plain):
            return False
        # A number, decimal, or comma-separated amount alone is not math.
        return bool(re.search(r'[+*/^_=<>≤≥≠×÷·%\-]', plain)
                    or re.search(r'\\(?:' + commands + r')\b', expression))

    def end_delimiter(start, delimiter, same_line=False):
        pos = start
        while True:
            pos = body.find(delimiter, pos)
            if pos < 0 or (same_line and '\n' in body[start:pos]):
                return -1
            if not escaped(pos):
                return pos
            pos += len(delimiter)

    result = []
    i = 0
    while i < len(body):
        if i == 0 or body[i - 1] == '\n':
            line_end = body.find('\n', i)
            line_end = len(body) if line_end < 0 else line_end + 1
            line = body[i:line_end]
            fence = re.match(
                r'(?: {0,3}>[ \t]?)*(?: {0,3}(?:[-+*]|\d+[.)])[ \t]+)?'
                r' {0,3}(`{3,}|~{3,})([^\n]*)', line)
            if fence and not (fence[1][0] == '`' and '`' in fence[2]):
                marker = fence[1]
                close = re.compile(r'^(?: {0,3}>[ \t]?)* {0,3}' + re.escape(marker[0])
                                   + '{' + str(len(marker)) + r',}[ \t]*\r?$', re.M)
                match = close.search(body, line_end)
                stop = len(body) if match is None else match.end()
                result.append(body[i:stop])
                i = stop
                continue
            if line.startswith(('    ', '\t')):
                result.append(line)
                i = line_end
                continue

        # Markdown code spans can use any number of backticks and span lines.
        if body[i] == '`' and not escaped(i):
            run = re.match(r'`+', body[i:])[0]
            close = re.compile(r'(?<!`)' + re.escape(run) + r'(?!`)').search(body, i + len(run))
            if close:
                result.append(body[i:close.end()])
                i = close.end()
                continue

        if not escaped(i):
            if body.startswith('$$', i):
                end = end_delimiter(i + 2, '$$')
                if end >= 0:
                    result.append(body[i:end + 2])
                    i = end + 2
                    continue
                result.append('$$')
                i += 2
                continue
            elif body.startswith(('\\(', '\\['), i):
                display = body[i + 1] == '['
                end = end_delimiter(i + 2, '\\]' if display else '\\)', not display)
                if end >= 0:
                    formula = body[i + 2:end]
                    result.append('\n\n$$\n' + formula.strip() + '\n$$\n\n'
                                  if display else '$$' + formula + '$$')
                    i = end + 2
                    continue
            elif body[i] == '$' and i + 1 < len(body):
                first = body[i + 1]
                if not first.isspace() and first != '$':
                    end = end_delimiter(i + 1, '$', same_line=True)
                    if (end > i + 1 and not body[end - 1].isspace()
                            and not body.startswith('$$', end)
                            and (end + 1 == len(body)
                                 or not (body[end + 1].isalnum() or body[end + 1] == '_'))
                            and (not first.isdigit() or numeric_math(body[i + 1:end]))):
                        result.append('$$' + body[i + 1:end] + '$$')
                        i = end + 1
                        continue
        result.append(body[i])
        i += 1
    return ''.join(result)


def read_existing_math(post_path):
    """Preserve an existing post's explicit math opt-in on update."""
    if not post_path.is_file():
        return None
    match = re.match(r'\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)',
                     post_path.read_text(encoding='utf-8'), re.S)
    metadata = yaml.safe_load(match[1]) if match else None
    value = metadata.get('math') if isinstance(metadata, dict) else None
    if value is not None and type(value) is not bool:
        raise ValueError('Math must be a YAML boolean (true or false).')
    return value


def calculate_fingerprints(source, post, images, image_dir):
    """Calculate fingerprints for source, post, and images."""
    return {
        "source_sha256": sha256_file(source),
        "post_sha256": sha256_file(post),
        "image_sha256": {
            name: sha256_file(image_dir / name)
            for name in sorted(images)
        },
    }

def execute(args):
    source = source_path(args.note)
    rel = source.relative_to(VAULT).as_posix()
    manifest = load_manifest()
    existing = manifest.get(rel)
    if args.command == 'publish' and existing:
        raise ValueError('Already published. Use update instead.')
    if args.command == 'update' and not existing:
        raise ValueError('Not registered as published. Use publish first or migrate it.')
    slug = existing['slug'] if existing else slugify(source.stem)
    if not slug:
        raise ValueError('Cannot create slug from note name')
    if not existing and any(v.get('slug') == slug for v in manifest.values()):
        raise ValueError('Slug already belongs to another source note')
    
    # Read metadata from the original Obsidian note.
    source_content = source.read_text(encoding="utf-8")
    metadata = read_obsidian_metadata(source_content)

    # Preserve categories and publication dates.
    category = (
        existing["categories"]
        if existing
        else [args.platform, args.category]
    )

    old_published = existing["published"] if existing else None
    if "date" in metadata:
        published = metadata["date"]
    elif existing:
        published = str(old_published)[:10]
        dt.date.fromisoformat(published)
    else:
        published = dt.date.today().isoformat()
    if "last_modified_at" in metadata:
        last_modified_at = metadata["last_modified_at"]
    elif existing:
        last_modified_at = existing.get("last_modified_at")
    else:
        last_modified_at = None

    # Obsidian tags take priority over existing tags.
    if "tags" in metadata:
        tags = metadata["tags"]
    elif existing:
        tags = existing["tags"]
    else:
        tags = (
            [slugify(tag.strip()) for tag in args.tags.split(",") if tag.strip()]
            if args.tags is not None
            else [slugify(args.platform)]
        )

    date_prefix = published[:10]
    post_rel = existing['post'] if existing else f'_posts/{date_prefix}-{slug}.md'
    post = REPO / post_rel
    if not post.is_relative_to(POST_DIR):
        raise ValueError('Unsafe post location in manifest')
    if args.command == 'publish' and post.exists():
        raise ValueError(f'Post already exists: {post}')
    if args.command == 'update' and not post.is_file():
        raise ValueError(f'Expected post missing: {post}')
    if 'last_modified_at' not in metadata and existing:
        if last_modified_at is None:
            match = re.search(r"^last_modified_at:\s*(.+)$", post.read_text(encoding="utf-8"), re.M)
            if match:
                value = yaml.safe_load(match.group(1))
                last_modified_at = value.isoformat() if isinstance(value, dt.date) else value
        if last_modified_at is not None:
            last_modified_at = str(last_modified_at)[:10]
            try:
                dt.date.fromisoformat(last_modified_at)
            except ValueError:
                raise ValueError('last_modified_at in existing post must be a valid date')
    math_enabled = (
        metadata['math'] if 'math' in metadata
        else read_existing_math(post) if args.command == 'update'
        else None
    )
    known = {v['slug']: v['slug'] for v in manifest.values()}
    known[slug] = slug
    body, images, unresolved, unsupported_image_modifiers = convert(
    source_content,
    slug,
    known
    )
    if math_enabled:
        body = prepare_math(body)
    for name in images:
        if not (IMAGE_DIR / name).is_file():
            raise ValueError(f'Missing image: {name}')
    dest_dir = ASSET_DIR / slug
    old_images = set(existing.get('images', [])) if existing else set()
    new_images = set(images)
    for name in new_images:
        dest = dest_dir / name
        if dest.exists() and name not in old_images:
            raise ValueError(f'Unmanaged image already exists: {dest}')
    
    # Obsidian description takes priority.
    if "description" in metadata:
        description = metadata["description"]
    elif args.command == "update":
        description = read_existing_description(post)
    else:
        description = None

    text = frontmatter(
        source.stem,
        published,
        category,
        tags,
        description,
        math_enabled=math_enabled,
        last_modified_at=last_modified_at
    ) + body

    print(f'Mode: {args.command} ({"WRITE" if args.write else "PREVIEW"})')
    print(f'Source: {source}\nPost: {post}\nImages: {len(images)}; new: {len(new_images-old_images)}; removed: {len(old_images-new_images)}')
    print(f'Categories: {category}; tags: {tags}')
    if unresolved:
        print('WARNING: unresolved Obsidian links: ' + ', '.join(sorted(set(unresolved))[:10]))
    if unsupported_image_modifiers:
        print('WARNING: unsupported Obsidian image modifiers (ignored): '
              + ', '.join(unsupported_image_modifiers))
    print('Review code blocks, embedded HTML, links, screenshots, secrets, and room publication rules manually.')
    if not args.write:
        print('PREVIEW ONLY: no files changed.')
        return
    # Update is deliberately non-destructive: leave removed images in place until reviewed.
    dest_dir.mkdir(parents=True, exist_ok=True)
    for name in sorted(new_images):
        shutil.copy2(IMAGE_DIR / name, dest_dir / name)
    post.parent.mkdir(parents=True, exist_ok=True)
    post.write_text(text, encoding='utf-8')

    # Record the exact generated files for later deployment checks.
    fingerprints = calculate_fingerprints(
        source,
        post,
        new_images,
        dest_dir
    )

    manifest[rel] = dict(
        slug=slug,
        published=published,
        **({"last_modified_at": last_modified_at} if last_modified_at is not None else {}),
        post=post_rel,
        categories=category,
        tags=tags,
        images=sorted(new_images),
        **fingerprints
    )
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    if old_images-new_images:
        print('Unused old images retained for safety: ' + ', '.join(sorted(old_images-new_images)))
    print('Files generated locally. Nothing committed or pushed.')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('command', choices=['preview', 'publish', 'update'])
    p.add_argument('note', help='Vault-relative or absolute path to .md note')
    p.add_argument('--platform', default='TryHackMe')
    p.add_argument('--category', default='Challenge')
    p.add_argument('--tags', default=None)
    p.add_argument('--write', action='store_true', help='Write generated files locally')
    args = p.parse_args()
    if args.command == 'preview' and args.write:
        p.error('preview does not accept --write')
    try:
        execute(args)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
