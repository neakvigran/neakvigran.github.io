#!/usr/bin/env python3
"""Publish selected Obsidian notes as Jekyll Chirpy posts (no Git actions)."""
import argparse
import datetime as dt
import json
import re
import shutil
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


def frontmatter(title, published, category, tags):
    # JSON strings are valid YAML scalars; quote user-provided values safely.
    return ('---\n' + f'title: {json.dumps(title, ensure_ascii=False)}\n'
            + f'date: {published}\n'
            + f'categories: {json.dumps(category, ensure_ascii=False)}\n'
            + f'tags: {json.dumps(tags, ensure_ascii=False)}\n'
            + 'toc: true\ncomments: false\n---\n\n')


def extract_body(s):
    # Existing Obsidian YAML metadata is not copied into Chirpy front matter.
    if s.startswith('---\n'):
        m = re.match(r'\A---\n.*?\n---\s*\n', s, re.S)
        if m:
            return s[m.end():]
    return s


def convert(source, slug, known_posts):
    body = extract_body(source)
    images = {}
    def image_replace(m):
        raw = m.group(1).split('|', 1)[0].strip()
        filename = Path(raw).name
        if filename != raw and '/' not in raw.replace('\\', '/'):
            raise ValueError('Unsupported image path')
        if filename.lower().endswith(tuple(SUPPORTED)) is False:
            raise ValueError(f'Unsupported embed (not an image): {raw}')
        if filename in images and images[filename] != raw:
            raise ValueError(f'Ambiguous image basename: {filename}')
        images[filename] = raw
        return f'![{Path(filename).stem}](/assets/img/obsidian/{slug}/{quote(filename)})'
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
    return body, images, unresolved


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
    category = existing['categories'] if existing else [args.platform, args.category]
    tags = existing['tags'] if existing else [slugify(x.strip()) for x in args.tags.split(',') if x.strip()]
    published = existing['published'] if existing else dt.datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %z')
    date_prefix = published[:10]
    post_rel = existing['post'] if existing else f'_posts/{date_prefix}-{slug}.md'
    post = REPO / post_rel
    if not post.is_relative_to(POST_DIR):
        raise ValueError('Unsafe post location in manifest')
    if args.command == 'publish' and post.exists():
        raise ValueError(f'Post already exists: {post}')
    if args.command == 'update' and not post.is_file():
        raise ValueError(f'Expected post missing: {post}')
    known = {v['slug']: v['slug'] for v in manifest.values()}
    known[slug] = slug
    body, images, unresolved = convert(source.read_text(encoding='utf-8'), slug, known)
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
    text = frontmatter(source.stem, published, category, tags) + body
    print(f'Mode: {args.command} ({"WRITE" if args.write else "PREVIEW"})')
    print(f'Source: {source}\nPost: {post}\nImages: {len(images)}; new: {len(new_images-old_images)}; removed: {len(old_images-new_images)}')
    print(f'Categories: {category}; tags: {tags}')
    if unresolved:
        print('WARNING: unresolved Obsidian links: ' + ', '.join(sorted(set(unresolved))[:10]))
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
    manifest[rel] = dict(slug=slug, published=published, post=post_rel,
                         categories=category, tags=tags, images=sorted(new_images))
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
    p.add_argument('--tags', default='tryhackme,web-security')
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
